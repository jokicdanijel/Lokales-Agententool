"""
Shared Authentication Utilities
Provides common authentication and authorization functions for all agents.
"""

import logging
import os
from pathlib import Path

from fastapi import Header, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

# HTTPBearer instance for dependency injection
security = HTTPBearer()


def load_bearer_token_from_env(project_root: Path | None = None) -> str:
    """
    Load BEARER_TOKEN from environment or .env file.

    Args:
        project_root: Optional path to project root directory (will look for .env there)

    Returns:
        Bearer token string, or empty string if not found

    Example:
        >>> token = load_bearer_token_from_env()
        >>> token = load_bearer_token_from_env(Path("/path/to/project"))
    """
    # First try environment variable
    token = os.getenv("BEARER_TOKEN", "")
    if token:
        return token

    # Try loading from .env file
    if project_root:
        env_path = project_root / ".env"
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("BEARER_TOKEN="):
                            token = line.split("=", 1)[1].strip()
                            # Remove quotes if present
                            token = token.strip('"').strip("'")
                            return token
            except Exception as e:
                logger.warning(f"Error reading .env file: {e}")

    return ""


def verify_token_httpbearer(
    credentials: HTTPAuthorizationCredentials = Security(security), bearer_token: str | None = None
) -> str:
    """
    Verify Bearer token using FastAPI HTTPBearer security.

    Args:
        credentials: Injected by FastAPI HTTPBearer dependency
        bearer_token: The expected token to validate against

    Returns:
        String indicating authenticated user (default: "authenticated_user")

    Raises:
        HTTPException: If token is invalid (401 Unauthorized)

    Example:
        In FastAPI endpoint:
        >>> @app.get("/protected")
        >>> async def protected_endpoint(user: str = Depends(lambda creds: verify_token_httpbearer(creds, BEARER_TOKEN))):
        >>>     return {"user": user}
    """
    if not bearer_token:
        logger.warning("BEARER_TOKEN not set - authentication disabled!")
        return "anonymous"

    if credentials.credentials != bearer_token:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return "authenticated_user"


def verify_token_header(authorization: str | None = Header(None), bearer_token: str | None = None) -> str:
    """
    Verify Bearer token from Authorization header (alternative to HTTPBearer).

    Args:
        authorization: Authorization header value
        bearer_token: The expected token to validate against

    Returns:
        String indicating authenticated user

    Raises:
        HTTPException: If header is missing or token is invalid

    Example:
        In FastAPI endpoint:
        >>> @app.get("/protected")
        >>> async def protected_endpoint(user: str = Depends(lambda auth: verify_token_header(auth, BEARER_TOKEN))):
        >>>     return {"user": user}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = parts[1]
    if not bearer_token:
        logger.warning("BEARER_TOKEN not set - authentication disabled!")
        return "anonymous"

    if token != bearer_token:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")

    return "authenticated_user"


def create_token_verifier(bearer_token: str, use_header: bool = False):
    """
    Factory function to create a token verifier dependency.

    Args:
        bearer_token: The token to validate against
        use_header: If True, use header-based verification; else use HTTPBearer

    Returns:
        A callable that can be used as a FastAPI dependency

    Example:
        >>> BEARER_TOKEN = load_bearer_token_from_env()
        >>> verify_token = create_token_verifier(BEARER_TOKEN)
        >>>
        >>> @app.get("/protected")
        >>> async def endpoint(user: str = Depends(verify_token)):
        >>>     return {"user": user}
    """
    if use_header:

        def verifier(authorization: str | None = Header(None)) -> str:
            return verify_token_header(authorization, bearer_token)

    else:

        def verifier(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
            return verify_token_httpbearer(credentials, bearer_token)

    return verifier
