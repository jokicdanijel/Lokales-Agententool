#!/usr/bin/env python3
"""
Meta Data Deletion Callback - GDPR/Privacy Compliance
Required by Facebook for WhatsApp Business API apps

Handles user data deletion requests from Meta/Facebook
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataDeletionHandler:
    """Handle Meta data deletion requests"""

    def __init__(self, app_secret: str, deletion_tracking_dir: str = "data/deletion_requests"):
        self.app_secret = app_secret
        self.deletion_dir = Path(deletion_tracking_dir)
        self.deletion_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = os.getenv("BASE_URL", "https://your-domain.com")

    def parse_signed_request(self, signed_request: str) -> dict[str, Any] | None:
        """Parse Facebook signed request"""
        try:
            # Split the signed request
            parts = signed_request.split(".", 1)
            if len(parts) != 2:
                logger.error("Invalid signed request format")
                return None

            encoded_sig, payload = parts

            # Decode signature and payload
            sig = self._base64_url_decode(encoded_sig)
            data = json.loads(self._base64_url_decode(payload).decode("utf-8"))

            # Verify signature
            expected_sig = hmac.new(self.app_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()

            if not hmac.compare_digest(sig, expected_sig):
                logger.error("Invalid signature in signed request")
                return None

            return data

        except Exception as e:
            logger.error(f"Error parsing signed request: {e}")
            return None

    def _base64_url_decode(self, input_str: str) -> bytes:
        """Decode base64 URL-safe string"""
        # Add padding if needed
        padding = 4 - len(input_str) % 4
        if padding != 4:
            input_str += "=" * padding

        return base64.urlsafe_b64decode(input_str)

    async def process_deletion_request(self, user_id: str) -> tuple[str, str]:
        """Process user data deletion request

        Returns:
            Tuple of (status_url, confirmation_code)
        """
        # Generate unique confirmation code
        confirmation_code = str(uuid.uuid4()).replace("-", "")[:12]

        # Create deletion tracking record
        deletion_record = {
            "user_id": user_id,
            "confirmation_code": confirmation_code,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "completed_at": None,
        }

        # Save to file
        record_file = self.deletion_dir / f"deletion_{confirmation_code}.json"
        with open(record_file, "w") as f:
            json.dump(deletion_record, f, indent=2)

        # Create status tracking URL
        status_url = f"{self.base_url}/deletion-status?code={confirmation_code}"

        # Start async deletion process
        asyncio.create_task(self._execute_deletion(user_id, confirmation_code))

        logger.info(f"Data deletion request initiated for user {user_id}, code: {confirmation_code}")

        return status_url, confirmation_code

    async def _execute_deletion(self, user_id: str, confirmation_code: str):
        """Execute actual data deletion"""
        try:
            # Delete from WhatsApp message history
            await self._delete_whatsapp_data(user_id)

            # Delete from archiv
            await self._delete_archiv_data(user_id)

            # Delete from local storage
            await self._delete_local_data(user_id)

            # Update deletion record
            record_file = self.deletion_dir / f"deletion_{confirmation_code}.json"
            if record_file.exists():
                with open(record_file) as f:
                    record = json.load(f)

                record.update({"status": "completed", "completed_at": datetime.now().isoformat()})

                with open(record_file, "w") as f:
                    json.dump(record, f, indent=2)

            logger.info(f"Data deletion completed for user {user_id}")

        except Exception as e:
            logger.error(f"Data deletion failed for user {user_id}: {e}")
            # Update record with error status
            record_file = self.deletion_dir / f"deletion_{confirmation_code}.json"
            if record_file.exists():
                with open(record_file) as f:
                    record = json.load(f)

                record.update({"status": "error", "error": str(e), "completed_at": datetime.now().isoformat()})

                with open(record_file, "w") as f:
                    json.dump(record, f, indent=2)

    async def _delete_whatsapp_data(self, user_id: str):
        """Delete WhatsApp-related data for user"""
        # Delete messages from database/files
        messages_dir = Path("data/messages")
        if messages_dir.exists():
            for msg_file in messages_dir.glob(f"*{user_id}*"):
                msg_file.unlink(missing_ok=True)

        logger.info(f"WhatsApp data deleted for user {user_id}")

    async def _delete_archiv_data(self, user_id: str):
        """Delete user data from archiv system"""
        # Search and delete from archiv entries
        archiv_path = Path("archivp/archivp_store")
        if archiv_path.exists():
            index_file = archiv_path / "index.jsonl"
            if index_file.exists():
                # Read all entries
                entries = []
                with open(index_file) as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            # Skip entries related to this user
                            if user_id not in json.dumps(entry):
                                entries.append(entry)
                        except:
                            continue

                # Rewrite index without user data
                with open(index_file, "w") as f:
                    for entry in entries:
                        f.write(json.dumps(entry) + "\n")

        logger.info(f"Archiv data deleted for user {user_id}")

    async def _delete_local_data(self, user_id: str):
        """Delete any local user data"""
        # Delete from logs (remove lines containing user_id)
        logs_dir = Path("logs")
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                self._scrub_file(log_file, user_id)

        logger.info(f"Local data scrubbed for user {user_id}")

    def _scrub_file(self, file_path: Path, user_id: str):
        """Remove lines containing user_id from file"""
        try:
            if not file_path.exists():
                return

            with open(file_path) as f:
                lines = f.readlines()

            # Filter out lines containing user_id
            clean_lines = [line for line in lines if user_id not in line]

            with open(file_path, "w") as f:
                f.writelines(clean_lines)

        except Exception as e:
            logger.warning(f"Could not scrub file {file_path}: {e}")

    def get_deletion_status(self, confirmation_code: str) -> dict[str, Any]:
        """Get status of deletion request"""
        record_file = self.deletion_dir / f"deletion_{confirmation_code}.json"

        if not record_file.exists():
            return {"error": "Deletion request not found"}

        with open(record_file) as f:
            return json.load(f)


# FastAPI endpoints for data deletion
app = FastAPI(title="Meta Data Deletion Callback")

# Get app secret from environment
META_APP_SECRET = os.getenv("META_APP_SECRET", "your_app_secret_here")
deletion_handler = DataDeletionHandler(META_APP_SECRET)


@app.post("/data-deletion-callback")
async def data_deletion_callback(request: Request):
    """Handle Meta data deletion callback

    This endpoint is called by Facebook when a user requests data deletion
    """
    try:
        # Get the signed request from form data
        form_data = await request.form()
        signed_request = form_data.get("signed_request")

        if not signed_request:
            raise HTTPException(status_code=400, detail="Missing signed_request")

        # Parse the signed request
        data = deletion_handler.parse_signed_request(signed_request)
        if not data:
            raise HTTPException(status_code=400, detail="Invalid signed_request")

        user_id = data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id in signed_request")

        # Process the deletion request
        status_url, confirmation_code = await deletion_handler.process_deletion_request(user_id)

        # Return required JSON response
        return JSONResponse(content={"url": status_url, "confirmation_code": confirmation_code})

    except Exception as e:
        logger.error(f"Data deletion callback error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/deletion-status")
async def deletion_status(code: str):
    """Check status of data deletion request"""
    status = deletion_handler.get_deletion_status(code)
    return JSONResponse(content=status)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "data-deletion-callback"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("DATA_DELETION_PORT", "12370"))
    uvicorn.run(app, host="0.0.0.0", port=port)
