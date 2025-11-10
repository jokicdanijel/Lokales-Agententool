"""
opena1/koordinator.py – 7.1 Validation router for opena1
FastAPI routes for strict request logging and validation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from datetime import datetime, timezone
import json
import logging

try:
    from schemas import Request71, ErrorSchema83
except ImportError:
    from .schemas import Request71, ErrorSchema83

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/log", tags=["opena1"])


def create_error_response_83(
    code: str,
    message: str,
    details: dict = None,  # type: ignore
    request_id: str = "unknown"
) -> ErrorSchema83:
    """Create standardized error response 8.3."""
    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return ErrorSchema83(
        request_id=request_id,
        timestamp=now_utc,
        source="opena1",
        error={
            "code": code,
            "message": message,
            "details": details or {}
        },
        strict=True
    )


@router.post("/opena1")
async def log_opena1(body: dict) -> dict:
    """
    7.1 Strict validation endpoint for opena1 logging.
    
    Accepts only fully-formed Request71 objects with strict=True.
    Returns 400 with schema 8.3 on validation failure.
    """
    request_id = body.get("request_id", "unknown")
    
    try:
        # Parse and validate
        req = Request71(**body)
        
        # Log successful validation
        logger.info(f"Valid 7.1 request: {req.request_id} from {req.project.name}")
        
        # Return success response
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            "request_id": str(req.request_id),
            "timestamp": now_utc,
            "source": "opena1",
            "status": "accepted",
            "strict": True
        }
    
    except ValidationError as ve:
        """Handle Pydantic validation errors."""
        error_details = []
        for err in ve.errors():
            error_details.append({
                "field": ".".join(str(x) for x in err["loc"]),
                "error": err["msg"]
            })
        
        # Determine error code
        if "strict" in str(ve):
            error_code = "STRICT_REQUIRED"
            error_msg = "Field 'strict' must be True"
        elif any("extra" in e["msg"] for e in ve.errors()):
            error_code = "EXTRA_FIELDS_FORBIDDEN"
            error_msg = "Extra fields not allowed"
        else:
            error_code = "SCHEMA_VIOLATION"
            error_msg = "Request does not match schema 7.1"
        
        logger.warning(f"Validation error [{error_code}]: {error_msg}")
        
        error_response = create_error_response_83(
            code=error_code,
            message=error_msg,
            details={"validation_errors": error_details},
            request_id=request_id
        )
        
        raise HTTPException(
            status_code=400,
            detail=json.loads(error_response.model_dump_json())
        )
    
    except Exception as ex:
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {type(ex).__name__}: {ex}")
        
        error_response = create_error_response_83(
            code="INTERNAL_ERROR",
            message=str(ex),
            request_id=request_id
        )
        
        raise HTTPException(
            status_code=500,
            detail=json.loads(error_response.model_dump_json())
        )
