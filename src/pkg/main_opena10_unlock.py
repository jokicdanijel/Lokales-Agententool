"""
opena10_Unlock: Account Unlock & 2FA Agent
OTP generation, password reset, backup codes
"""

import hashlib
import json
import logging
import os
import secrets
import sys
import urllib.request
from datetime import datetime, timedelta

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(title="opena10_Unlock", version="1.0.0", description="Account Unlock & 2FA Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12358
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory OTP storage (in production: use Redis/DB)
_otp_store: dict = {}
_backup_codes_store: dict = {}
_unlock_logs: list = []

# ============================================================================
# DATA MODELS
# ============================================================================


class OTPGenerateRequest(BaseModel):
    user_id: str
    length: int = 6


class OTPVerifyRequest(BaseModel):
    user_id: str
    otp: str


class PasswordResetRequest(BaseModel):
    email: str
    new_password: str


class BackupCodesRequest(BaseModel):
    user_id: str
    count: int = 10


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena10_unlock",
            "dst": "opena2",
            "kind": "SECURITY_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_otp(length: int = 6) -> str:
    """Generate numeric OTP"""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def _generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def _hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena10_Unlock",
        "port": PORT,
        "active_otps": len(_otp_store),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/otp/generate")
async def generate_otp(req: OTPGenerateRequest, authorization: str = Header(None)):
    """Generate OTP for user"""
    _validate_token(authorization)

    try:
        otp = _generate_otp(req.length)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        _otp_store[req.user_id] = {"otp": otp, "expires_at": expires_at.isoformat(), "attempts": 0}

        logger.info(f"🔐 OTP generated for {req.user_id}")

        await _archive({"op": "OTP_GENERATE", "user_id": req.user_id, "length": req.length, "expires_minutes": 10})

        return {
            "strict": True,
            "user_id": req.user_id,
            "otp": otp,  # In production: NEVER return OTP in response!
            "expires_minutes": 10,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ OTP generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/otp/verify")
async def verify_otp(req: OTPVerifyRequest, authorization: str = Header(None)):
    """Verify OTP"""
    _validate_token(authorization)

    try:
        if req.user_id not in _otp_store:
            raise HTTPException(status_code=404, detail="No OTP found for user")

        otp_entry = _otp_store[req.user_id]

        # Check expiration
        if datetime.fromisoformat(otp_entry["expires_at"]) < datetime.utcnow():
            del _otp_store[req.user_id]
            raise HTTPException(status_code=410, detail="OTP expired")

        # Check attempt limit
        if otp_entry["attempts"] >= 3:
            del _otp_store[req.user_id]
            raise HTTPException(status_code=429, detail="Too many attempts")

        otp_entry["attempts"] += 1

        if otp_entry["otp"] == req.otp:
            del _otp_store[req.user_id]
            logger.info(f"✅ OTP verified for {req.user_id}")

            await _archive({"op": "OTP_VERIFY", "user_id": req.user_id, "success": True})

            return {"strict": True, "user_id": req.user_id, "verified": True, "ts": datetime.utcnow().isoformat() + "Z"}
        else:
            logger.warning(f"❌ OTP verification failed for {req.user_id}")

            await _archive(
                {"op": "OTP_VERIFY", "user_id": req.user_id, "success": False, "attempt": otp_entry["attempts"]}
            )

            raise HTTPException(status_code=401, detail="Invalid OTP")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/password/reset")
async def reset_password(req: PasswordResetRequest, authorization: str = Header(None)):
    """Reset user password"""
    _validate_token(authorization)

    try:
        hashed = _hash_password(req.new_password)

        logger.info(f"🔑 Password reset for {req.email}")

        await _archive({"op": "PASSWORD_RESET", "email": req.email, "timestamp": datetime.utcnow().isoformat()})

        return {"strict": True, "email": req.email, "reset": True, "ts": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.error(f"❌ Password reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/backup/codes")
async def generate_backup_codes(req: BackupCodesRequest, authorization: str = Header(None)):
    """Generate backup codes"""
    _validate_token(authorization)

    try:
        codes = _generate_backup_codes(req.count)
        _backup_codes_store[req.user_id] = codes

        logger.info(f"📋 Backup codes generated for {req.user_id}")

        await _archive({"op": "BACKUP_CODES_GENERATE", "user_id": req.user_id, "count": req.count})

        return {
            "strict": True,
            "user_id": req.user_id,
            "codes": codes,
            "count": len(codes),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Backup codes generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/unlock/log")
async def get_unlock_log(authorization: str = Header(None), limit: int = 10):
    """Get unlock/security log"""
    _validate_token(authorization)

    try:
        log_entries = _unlock_logs[-limit:]
        logger.info(f"📋 Unlock log retrieved: {len(log_entries)} entries")

        return {
            "strict": True,
            "entries": log_entries,
            "count": len(log_entries),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena10_Unlock",
        "version": "1.0.0",
        "port": PORT,
        "active_otps": len(_otp_store),
        "users_with_backup_codes": len(_backup_codes_store),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena10_Unlock on port {PORT}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
