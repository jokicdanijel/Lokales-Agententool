# Shared Modules

This directory contains common utilities and base classes used across all agent services.

## Overview

The shared modules were created to eliminate code duplication across the 20+ agent services in the ELION system. Instead of each agent implementing its own authentication, persistence, and configuration logic, agents now import from these shared modules.

## Modules

### 📦 `auth.py` - Authentication Utilities

Provides common authentication and authorization functionality for FastAPI agents.

**Key Functions:**
- `load_bearer_token_from_env()` - Load BEARER_TOKEN from environment or .env file
- `verify_token_httpbearer()` - Verify token using HTTPBearer security scheme
- `verify_token_header()` - Verify token from Authorization header
- `create_token_verifier()` - Factory to create token verifier dependencies

**Usage Example:**
```python
from src.pkg.shared import load_bearer_token_from_env, create_token_verifier

BEARER_TOKEN = load_bearer_token_from_env(PROJECT_ROOT)
verify_token = create_token_verifier(BEARER_TOKEN)

@app.get("/protected")
async def protected_endpoint(user: str = Depends(verify_token)):
    return {"user": user}
```

### 📦 `base_models.py` - Standard Pydantic Models

Provides standard Pydantic models used across all agents.

**Key Models:**
- `CommandRequest` - Generic command request for Option-2-Flow
- `HealthResponse` - Standard health check response format
- `ServiceInfo` - Service information for root endpoints
- `SuccessResponse` - Generic success response
- `ErrorResponse` - Generic error response

**Helper Functions:**
- `get_current_timestamp_iso()` - Get ISO 8601 formatted timestamp
- `create_health_response()` - Factory for health check responses
- `create_service_info()` - Factory for service info responses

**Usage Example:**
```python
from src.pkg.shared import create_health_response

@app.get("/health")
async def health():
    return create_health_response(
        service="opena11",
        kuerzel="unlockp",
        port=12356,
        start_time=START_TIME,
        custom_metric=42
    )
```

### 📦 `persistence.py` - Data Persistence Layer

Provides base classes for JSON and JSONL data persistence.

**Key Classes:**
- `BaseDataStore[T]` - Abstract base class for type-safe JSON stores
- `JSONDataStore` - Simple dictionary-based JSON store
- `AuditLog` - JSONL append-only audit log (WORM-compliant)

**Features:**
- Generic type support with Python type hints
- Automatic serialization/deserialization
- CRUD operations: add, remove, find, find_all, count
- Metadata tracking (last_updated, count)
- JSONL format for audit logs (append-only)

**Usage Example:**
```python
from src.pkg.shared import BaseDataStore, AuditLog
from dataclasses import dataclass, asdict

@dataclass
class Profile:
    id: str
    name: str

class ProfileStore(BaseDataStore[Profile]):
    def _serialize(self, item):
        return asdict(item)
    
    def _deserialize(self, data):
        return Profile(**data)

store = ProfileStore(Path("data/profiles.json"))
store.load()
store.add(Profile("1", "Alice"))

audit = AuditLog(Path("data/audit.jsonl"))
audit.log("CREATE", "user", "profile", "1")
```

### 📦 `config.py` - Configuration Management

Extended SCTA configuration with agent-specific utilities.

**Key Functions:**
- `validate_port()` - Validate port against project policy (12344-12399, not 8080)
- `get_port_from_env()` - Get and validate port from environment variable

**Constants:**
- `ALLOWED_PORT_RANGE` - Range of allowed ports (12344-12399)
- `FORBIDDEN_PORTS` - List of forbidden ports ([8080])

**Usage Example:**
```python
from src.pkg.shared import get_port_from_env

PORT = get_port_from_env("OPENA11_PORT", 12356, "opena11")
# Automatically validates port is in allowed range
```

## Testing

All shared modules have comprehensive unit test coverage:

```bash
# Run all tests
python3 -m pytest project-root/tests/unit/test_shared_*.py -v

# Run specific module tests
python3 -m pytest project-root/tests/unit/test_shared_auth.py -v
python3 -m pytest project-root/tests/unit/test_shared_base_models.py -v
python3 -m pytest project-root/tests/unit/test_shared_persistence.py -v
python3 -m pytest project-root/tests/unit/test_shared_config.py -v
```

**Test Coverage:**
- `test_shared_auth.py`: 16 tests ✅
- `test_shared_base_models.py`: 15 tests ✅
- `test_shared_persistence.py`: 13 tests ✅
- `test_shared_config.py`: 12 tests ✅
- **Total: 56 tests passing** ✅

## Migration Guide

See [REFACTORING_GUIDE.md](../../docs/REFACTORING_GUIDE.md) for detailed migration instructions.

**Quick Start:**

1. **Import shared modules** instead of duplicating code:
   ```python
   from src.pkg.shared import (
       load_bearer_token_from_env,
       create_token_verifier,
       create_health_response,
       BaseDataStore,
       AuditLog,
   )
   ```

2. **Use shared authentication**:
   ```python
   BEARER_TOKEN = load_bearer_token_from_env(PROJECT_ROOT)
   verify_token = create_token_verifier(BEARER_TOKEN)
   ```

3. **Use standard health endpoint**:
   ```python
   @app.get("/health")
   async def health():
       return create_health_response(...)
   ```

4. **Inherit from BaseDataStore**:
   ```python
   class MyStore(BaseDataStore[MyType]):
       def _serialize(self, item): ...
       def _deserialize(self, data): ...
   ```

## Examples

See `docs/example_refactored_agent.py` for a complete working example of an agent using all shared modules.

## Benefits

### Code Reduction
- **Before**: ~100-200 lines of boilerplate per agent
- **After**: ~10-20 lines of imports and configuration
- **Savings**: ~90% reduction in duplicated code

### Consistency
- All agents use same authentication method
- All health endpoints return same format
- All audit logs follow same structure

### Maintainability
- Fix bugs in one place
- Update behavior across all agents
- Easier to understand and review code

### Testing
- Shared modules tested once, thoroughly
- Agents can focus on business logic tests
- Higher overall test coverage

## Version History

- **v1.0.0** (2025-12-18) - Initial release
  - Authentication utilities
  - Base Pydantic models
  - Persistence layer
  - Configuration management
  - 56 comprehensive unit tests

## Support

For questions or issues:
1. Check the documentation in this README
2. Review the [Refactoring Guide](../../docs/REFACTORING_GUIDE.md)
3. Look at the [example agent](../../docs/example_refactored_agent.py)
4. Check the unit tests for usage examples
5. Consult with the team lead

## Contributing

When adding new shared functionality:
1. Add it to the appropriate module (auth, base_models, persistence, config)
2. Write comprehensive unit tests (aim for 100% coverage)
3. Update this README with usage examples
4. Update the Refactoring Guide if needed
5. Create a migration example for existing agents
