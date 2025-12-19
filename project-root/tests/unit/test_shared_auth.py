"""
Unit tests for shared authentication module.
"""

import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.pkg.shared.auth import (
    load_bearer_token_from_env,
    verify_token_httpbearer,
    verify_token_header,
    create_token_verifier,
)


class TestLoadBearerToken:
    """Tests for load_bearer_token_from_env function."""
    
    def test_load_from_env_variable(self, monkeypatch):
        """Should load token from BEARER_TOKEN environment variable."""
        monkeypatch.setenv("BEARER_TOKEN", "test-token-123")
        token = load_bearer_token_from_env()
        assert token == "test-token-123"
    
    def test_load_from_env_file(self):
        """Should load token from .env file."""
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text('BEARER_TOKEN=file-token-456\n')
            
            token = load_bearer_token_from_env(Path(tmpdir))
            assert token == "file-token-456"
    
    def test_load_from_env_file_with_quotes(self):
        """Should strip quotes from token in .env file."""
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text('BEARER_TOKEN="quoted-token"\n')
            
            token = load_bearer_token_from_env(Path(tmpdir))
            assert token == "quoted-token"
    
    def test_env_variable_takes_precedence(self, monkeypatch):
        """Environment variable should take precedence over .env file."""
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text('BEARER_TOKEN=file-token\n')
            
            monkeypatch.setenv("BEARER_TOKEN", "env-token")
            token = load_bearer_token_from_env(Path(tmpdir))
            assert token == "env-token"
    
    def test_returns_empty_when_not_found(self):
        """Should return empty string when token not found."""
        with TemporaryDirectory() as tmpdir:
            token = load_bearer_token_from_env(Path(tmpdir))
            assert token == ""
    
    def test_handles_missing_env_file(self):
        """Should handle missing .env file gracefully."""
        with TemporaryDirectory() as tmpdir:
            token = load_bearer_token_from_env(Path(tmpdir))
            assert token == ""


class TestVerifyTokenHTTPBearer:
    """Tests for verify_token_httpbearer function."""
    
    def test_valid_token(self):
        """Should accept valid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        result = verify_token_httpbearer(credentials, "valid-token")
        assert result == "authenticated_user"
    
    def test_invalid_token(self):
        """Should reject invalid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        with pytest.raises(HTTPException) as exc_info:
            verify_token_httpbearer(credentials, "valid-token")
        assert exc_info.value.status_code == 401
    
    def test_no_token_configured(self):
        """Should return anonymous when no token configured."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="any-token"
        )
        result = verify_token_httpbearer(credentials, None)
        assert result == "anonymous"


class TestVerifyTokenHeader:
    """Tests for verify_token_header function."""
    
    def test_valid_bearer_header(self):
        """Should accept valid Bearer header."""
        result = verify_token_header("Bearer valid-token", "valid-token")
        assert result == "authenticated_user"
    
    def test_invalid_token_in_header(self):
        """Should reject invalid token in header."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token_header("Bearer invalid-token", "valid-token")
        assert exc_info.value.status_code == 401
    
    def test_missing_authorization_header(self):
        """Should reject missing authorization header."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token_header(None, "valid-token")
        assert exc_info.value.status_code == 401
        assert "Missing Authorization header" in str(exc_info.value.detail)
    
    def test_invalid_header_format(self):
        """Should reject invalid header format."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token_header("InvalidFormat", "valid-token")
        assert exc_info.value.status_code == 401
        assert "Invalid Authorization header" in str(exc_info.value.detail)
    
    def test_case_insensitive_bearer(self):
        """Should accept 'bearer' in any case."""
        result = verify_token_header("bearer valid-token", "valid-token")
        assert result == "authenticated_user"
        
        result = verify_token_header("BEARER valid-token", "valid-token")
        assert result == "authenticated_user"


class TestCreateTokenVerifier:
    """Tests for create_token_verifier factory function."""
    
    def test_creates_httpbearer_verifier(self):
        """Should create HTTPBearer-based verifier."""
        verifier = create_token_verifier("test-token", use_header=False)
        assert callable(verifier)
    
    def test_creates_header_verifier(self):
        """Should create header-based verifier."""
        verifier = create_token_verifier("test-token", use_header=True)
        assert callable(verifier)
