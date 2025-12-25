# PORTIER 3.0 Shared Libraries

Centralized, reusable components for all PORTIER 3.0 agents.

## Overview

This package contains shared libraries that eliminate code duplication across 19+ agent directories. Instead of maintaining 78 duplicate files totaling ~9,500 lines of code, we now have 4 centralized modules totaling ~850 lines.

## Modules

### 1. `safepoint_client.py`

**Purpose**: Client for writing safepoints to opena2 archivator

**Key Features**:

- Async HTTP client using httpx
- Recursive secret masking
- Category validation (CMD, RESP, ROUTE, DISPATCH)
- Environment variable configuration

**Usage**:

```python
from src.pkg.shared.safepoint_client import SafepointClient

client = SafepointClient()
await client.write(
    category="CMD",
    source="opena4",
    destination="opena5",
    request_id="req-123",
    payload={"action": "send_message"}
)
```

### 2. `sse_client.py`

**Purpose**: SSE event streaming and safepoint archiving

**Key Features**:

- SSEClient for subscribing to dashboard events
- SafepointClient for async archiving (alternate implementation)
- Factory functions for agent-specific instances
- Singleton pattern support

**Usage**:

```python
from src.pkg.shared.sse_client import create_sse_client, create_safepoint_client

# Create agent-specific clients
sse = create_sse_client(source_agent="opena4")
safepoint = create_safepoint_client(source_agent="opena4")

# Subscribe to events
async for event in sse.subscribe():
    print(f"Event: {event['event_type']}")

# Write safepoint
await safepoint.write_safepoint(
    category="RESP",
    destination="opena20",
    payload={"status": "success"}
)
```

### 3. `security.py`

**Purpose**: Authentication, authorization, and security utilities

**Key Features**:

- Bearer token verification (FastAPI Depends compatible)
- Optional token verification for public endpoints
- Sliding window rate limiter
- Recursive secret masking
- Port policy enforcement (12344-12399 range)
- Development mode support

**Usage**:

```python
from fastapi import Depends, FastAPI
from src.pkg.shared.security import verify_token, mask_secrets, RateLimiter

app = FastAPI()

@app.get("/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    sensitive_data = {"password": "secret123", "username": "john"}
    return mask_secrets(sensitive_data)  # Returns: {"password": "***", "username": "john"}

# Rate limiting
limiter = RateLimiter(max_requests=60, window_seconds=60)

@app.get("/api/data")
async def get_data(request: Request):
    if not limiter.is_allowed(request):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return {"data": "..."}
```

### 4. `config_base.py`

**Purpose**: Base configuration classes for all agents

**Key Features**:

- PortPolicy class for port range validation
- BaseAgentConfig with common fields:
  - Service identification (name, kürzel, host, port)
  - Authentication (bearer_token)
  - Service URLs (opena1, opena2, opena20)
  - Logging configuration
  - Directory management
- AgentInfo model for agent registry
- Pydantic-based validation with environment variable support

**Usage**:

```python
from pydantic import Field
from src.pkg.shared.config_base import BaseAgentConfig, PortPolicy

class MyAgentConfig(BaseAgentConfig):
    # Common fields inherited automatically
    service_name: str = "opena4"
    kuerzel: str = "tgap"
    port: int = 12346

    # Add agent-specific fields
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")

config = MyAgentConfig()
config.ensure_directories()  # Creates data/ and logs/
logging_config = config.get_logging_config()
```

## Installation & Setup

### 1. Add to PYTHONPATH (if needed)

```bash
export PYTHONPATH=/path/to/Gesamtprojekt-start:$PYTHONPATH
```

### 2. Environment Variables

All modules respect standard PORTIER environment variables:

```bash
BEARER_TOKEN=your-token-here
OPENA1_URL=http://127.0.0.1:12344
OPENA2_URL=http://127.0.0.1:12345
OPENA20_URL=http://127.0.0.1:12349
DEV_MODE=false
LOG_LEVEL=INFO
```

### 3. Quick Import (Backward Compatibility)

For easy migration, use the compatibility wrapper:

```python
# Single import for everything
from src.pkg.portier_common import (
    SafepointClient,
    SSEClient,
    create_sse_client,
    verify_token,
    mask_secrets,
    BaseAgentConfig
)
```

## Testing

Run the test suite:

```bash
# With pytest installed
pytest src/pkg/shared/test_*.py -v

# Individual modules
pytest src/pkg/shared/test_safepoint_client.py -v
pytest src/pkg/shared/test_sse_client.py -v
```

## Migration Guide

See [MIGRATION_GUIDE_SHARED_LIBRARIES.md](../../docs/MIGRATION_GUIDE_SHARED_LIBRARIES.md) for:

- Step-by-step migration instructions
- Code examples (before/after)
- Testing procedures
- Rollback instructions

## Impact

**Code Reduction**:

- Before: 78 files, ~9,505 lines
- After: 4 modules, ~850 lines
- **Reduction: 91%** (~8,654 lines)

**Maintenance**:

- Before: Fix bugs in 19-21 places
- After: Fix bugs in 1 place

**Benefits**:

- ✅ Single source of truth
- ✅ Consistent behavior across agents
- ✅ Easier testing and debugging
- ✅ Faster development and bug fixes
- ✅ Better code quality

## API Compatibility

All modules maintain **backward compatibility** with existing agent code:

- Same function signatures
- Same return types
- Same error handling
- Environment variable support preserved

## Contributing

When adding new common functionality:

1. **Check for duplication**: If 3+ agents need it, consider adding to shared
2. **Write tests**: All shared code must have unit tests
3. **Document**: Update this README and add docstrings
4. **Maintain compatibility**: Don't break existing agents
5. **Version carefully**: Use semantic versioning for breaking changes

## Support

For questions or issues:

- Check [MIGRATION_GUIDE_SHARED_LIBRARIES.md](../../docs/MIGRATION_GUIDE_SHARED_LIBRARIES.md)
- Review [CODE_DUPLICATION_REFACTORING_IMPACT.md](../../docs/CODE_DUPLICATION_REFACTORING_IMPACT.md)
- Check inline documentation and docstrings

## License

Internal use only - Part of PORTIER 3.0 system.

---

**Created**: 2025-12-18
**Status**: Production Ready
**Version**: 1.0.0
