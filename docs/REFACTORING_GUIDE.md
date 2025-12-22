# Code Refactoring Guide: Shared Modules

## Overview

This document describes the refactoring effort to eliminate code duplication across the agent services by extracting common functionality into shared modules.

**Note:** All shared Pydantic models use Pydantic V2 `ConfigDict` style, consistent with the opena6 browser agent, eliminating deprecation warnings.

## Problem Statement

Analysis of the codebase revealed significant code duplication across 10+ agent files:

- **Bearer token loading**: Duplicated in 10 files
- **FastAPI verify_token functions**: Duplicated in 10 files
- **Health endpoints**: Duplicated in 8 files
- **Command endpoints**: Duplicated in 10 files
- **DataStore class**: Duplicated in 7 files
- **AuditLog class**: Duplicated in 2 files
- **Port configuration**: Duplicated in 3 files

This duplication led to:
- **Maintenance burden**: Bug fixes needed in multiple places
- **Inconsistency**: Different implementations with subtle variations
- **Testing overhead**: Same logic tested multiple times
- **Increased codebase size**: ~40-50% unnecessary boilerplate

## Solution: Shared Modules

We created four new shared modules in `src/pkg/shared/`:

### 1. Authentication Module (`auth.py`)

**Purpose**: Centralize authentication and authorization logic.

**Key Functions**:
- `load_bearer_token_from_env()`: Load token from env or .env file
- `verify_token_httpbearer()`: Verify token using HTTPBearer security
- `verify_token_header()`: Verify token from Authorization header
- `create_token_verifier()`: Factory to create token verifier dependencies

**Example Usage**:
```python
from src.pkg.shared import load_bearer_token_from_env, create_token_verifier

# Load token
BEARER_TOKEN = load_bearer_token_from_env(PROJECT_ROOT)

# Create verifier
verify_token = create_token_verifier(BEARER_TOKEN)

# Use in endpoint
@app.get("/protected")
async def protected_endpoint(user: str = Depends(verify_token)):
    return {"user": user}
```

### 2. Base Models Module (`base_models.py`)

**Purpose**: Provide standard Pydantic models for all agents.

**Key Models**:
- `CommandRequest`: Generic command request (Option-2-Flow)
- `HealthResponse`: Standard health check response
- `ServiceInfo`: Service information for root endpoint
- `SuccessResponse`: Generic success response
- `ErrorResponse`: Generic error response

**Helper Functions**:
- `get_current_timestamp_iso()`: Get ISO 8601 timestamp
- `create_health_response()`: Factory for health responses
- `create_service_info()`: Factory for service info

**Example Usage**:
```python
from src.pkg.shared import create_health_response

@app.get("/health")
async def health():
    return create_health_response(
        service="opena11",
        kuerzel="unlockp",
        port=12356,
        start_time=START_TIME,
        permissions_count=42  # Extra info
    )
```

### 3. Persistence Module (`persistence.py`)

**Purpose**: Provide common data persistence patterns.

**Key Classes**:
- `BaseDataStore[T]`: Abstract base class for JSON stores
- `JSONDataStore`: Simple dictionary-based store
- `AuditLog`: JSONL append-only audit log (WORM-compliant)

**Features**:
- Generic type support
- Automatic serialization/deserialization
- CRUD operations (add, remove, find, find_all)
- Metadata tracking (last_updated, count)
- JSONL format for audit logs

**Example Usage**:
```python
from src.pkg.shared import BaseDataStore, AuditLog
from dataclasses import dataclass, asdict

@dataclass
class Profile:
    id: str
    name: str
    email: str

class ProfileStore(BaseDataStore[Profile]):
    def _serialize(self, item):
        return asdict(item)
    
    def _deserialize(self, data):
        return Profile(**data)

# Use the store
store = ProfileStore(Path("data/profiles.json"))
store.load()
store.add(Profile("1", "John", "john@example.com"))

# Audit logging
audit = AuditLog(Path("data/audit.jsonl"))
audit.log(
    operation="CREATE_PROFILE",
    actor="api_user",
    resource_type="profile",
    resource_id="1"
)
```

### 4. Configuration Module (`config.py`)

**Purpose**: Centralize configuration management with validation.

**Key Functions**:
- `validate_port()`: Validate port against policy (12344-12399, not 8080)
- `get_port_from_env()`: Get and validate port from environment

**Constants**:
- `ALLOWED_PORT_RANGE`: Valid port range (12344-12399)
- `FORBIDDEN_PORTS`: Forbidden ports ([8080])

**Example Usage**:
```python
from src.pkg.shared import get_port_from_env

PORT = get_port_from_env("OPENA11_PORT", 12356, "opena11")
# Automatically validates against policy
```

## Migration Guide

### Before (Duplicated Code)

```python
# In each agent file...

# Token loading (duplicated)
BEARER_TOKEN = None
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip().startswith("BEARER_TOKEN="):
                BEARER_TOKEN = line.split("=", 1)[1].strip()
                break

# Auth verification (duplicated)
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    if not BEARER_TOKEN:
        logger.warning("BEARER_TOKEN not set - authentication disabled!")
        return "anonymous"
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return "authenticated_user"

# Health endpoint (duplicated)
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "opena11",
        "port": PORT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

# DataStore (duplicated)
class DataStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = []
    # ... duplicate implementation
```

### After (Using Shared Modules)

```python
# Import from shared modules
from src.pkg.shared import (
    load_bearer_token_from_env,
    create_token_verifier,
    create_health_response,
    get_port_from_env,
    BaseDataStore,
    AuditLog,
)

# Configuration (one line)
BEARER_TOKEN = load_bearer_token_from_env(PROJECT_ROOT)
PORT = get_port_from_env("OPENA11_PORT", 12356, "opena11")

# Auth (one line)
verify_token = create_token_verifier(BEARER_TOKEN)

# Health endpoint (one call)
@app.get("/health")
async def health():
    return create_health_response(
        service="opena11",
        kuerzel="unlockp",
        port=PORT,
        start_time=START_TIME,
        permissions_count=len(perm_store.list_all())
    )

# Custom DataStore (inherit and implement 2 methods)
class PermissionStore(BaseDataStore[Permission]):
    def _serialize(self, item):
        return item.model_dump()
    
    def _deserialize(self, data):
        return Permission(**data)
```

## Testing

All shared modules have comprehensive unit tests:

```bash
# Run all shared module tests
python3 -m pytest project-root/tests/unit/test_shared_*.py -v

# Results:
# test_shared_auth.py:        16 tests passing ✅
# test_shared_base_models.py: 15 tests passing ✅
# test_shared_config.py:      12 tests passing ✅
# test_shared_persistence.py: 13 tests passing ✅
# TOTAL:                      56 tests passing ✅
```

## Benefits

### Code Reduction
- **Before**: ~2,000 lines of duplicated code across 10 files
- **After**: ~500 lines in shared modules (75% reduction)
- **Per Agent**: 100-200 lines saved per agent file

### Maintainability
- **Single source of truth**: Bug fixes in one place
- **Consistent behavior**: All agents use same implementation
- **Easier updates**: Change once, affects all agents

### Testing
- **Test once**: Shared modules tested comprehensively
- **Higher confidence**: 56 unit tests covering edge cases
- **Faster test execution**: Don't re-test same logic

### Developer Experience
- **Cleaner code**: Agents focus on business logic
- **Faster development**: Reuse instead of rewrite
- **Better documentation**: Centralized docs for common patterns

## Next Steps

1. **Create Example**: Refactor one agent as reference implementation
2. **Gradual Migration**: Update agents one at a time
3. **Validation**: Test each migrated agent thoroughly
4. **Documentation**: Update agent-specific docs
5. **Deprecation**: Mark old patterns as deprecated

## Support

For questions or issues with the shared modules:
1. Check this documentation first
2. Review the unit tests for usage examples
3. Check inline code documentation (docstrings)
4. Consult with the team lead

## Version History

- **v1.0.0** (2025-12-18): Initial shared modules creation
  - auth.py: Authentication utilities
  - base_models.py: Standard Pydantic models
  - persistence.py: Data storage abstractions
  - config.py: Configuration management
  - 56 comprehensive unit tests
