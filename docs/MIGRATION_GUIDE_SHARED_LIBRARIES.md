# Migration Guide: Using Shared Libraries

This guide explains how to migrate an agent from duplicated local files to the centralized shared libraries in `src/pkg/shared/`.

## Overview

The following files can be replaced with shared libraries:

- `safepoint_client.py` → `src.pkg.shared.safepoint_client`
- `sse_client.py` → `src.pkg.shared.sse_client`
- `security.py` → `src.pkg.shared.security`
- `config.py` (partially) → `src.pkg.shared.config_base`

## Migration Steps

### 1. Update Imports

#### Before (using local files):

```python
from safepoint_client import SafepointClient
from sse_client import SSEClient, get_sse_client
from security import verify_token, mask_secrets
```

#### After (using shared libraries):

```python
from src.pkg.shared.safepoint_client import SafepointClient
from src.pkg.shared.sse_client import SSEClient, create_sse_client
from src.pkg.shared.security import verify_token, mask_secrets
```

### 2. Update SSE Client Usage

The new SSE client uses factory functions for better agent-specific configuration.

#### Before:

```python
# In sse_client.py - hardcoded agent name
class SafepointClient:
    def __init__(self, source_agent: str = "opena4"):  # Hardcoded
        ...

# Usage
_sse_client = None
def get_sse_client():
    global _sse_client
    if _sse_client is None:
        _sse_client = SSEClient()
    return _sse_client
```

#### After:

```python
from src.pkg.shared.sse_client import create_sse_client, create_safepoint_client

# Create agent-specific clients
sse_client = create_sse_client(source_agent="opena4")
safepoint_client = create_safepoint_client(source_agent="opena4")
```

### 3. Update Configuration

If your agent uses a custom config, you can now inherit from `BaseAgentConfig`.

#### Before (opena4/config.py):

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class PortPolicy:
    ALLOWED_RANGE = range(12344, 12400)
    # ... full implementation

class ServiceConfig(BaseSettings):
    service_name: str = "opena4"
    port: int = 12346
    bearer_token: str = Field(default="", alias="BEARER_TOKEN")
    opena1_url: str = Field(default="http://127.0.0.1:12344")
    # ... many more common fields
```

#### After (opena4/config.py):

```python
from pydantic import Field
from src.pkg.shared.config_base import BaseAgentConfig, PortPolicy

class ServiceConfig(BaseAgentConfig):
    # Common fields inherited from BaseAgentConfig:
    # - service_name, kuerzel, host, port, version
    # - bearer_token, opena1_url, opena2_url, opena20_url
    # - log_level, log_format
    # - base_dir, data_dir, logs_dir properties

    # Override defaults
    service_name: str = "opena4"
    kuerzel: str = "tgap"
    port: int = 12346

    # Add agent-specific fields only
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_allowed_users: List[int] = Field(default_factory=list)
```

### 4. Update Security Imports

#### Before:

```python
from security import verify_token, mask_secrets, RateLimiter
```

#### After:

```python
from src.pkg.shared.security import verify_token, mask_secrets, RateLimiter
```

No code changes needed - the API is identical!

### 5. Remove Duplicated Files

After migration and testing:

```bash
# From agent directory (e.g., 3.opena4_telegram/)
rm safepoint_client.py  # If using shared version
rm sse_client.py        # If using shared version
rm security.py          # If using shared version
# Keep config.py but simplify it using BaseAgentConfig
```

## Complete Example: Migrating opena4

### Before Structure:

```
3.opena4_telegram/
├── main_telegram_agent.py
├── safepoint_client.py      ← 53 lines (duplicated)
├── sse_client.py            ← 190 lines (duplicated)
├── security.py              ← 138 lines (duplicated)
├── config.py                ← 167 lines (partially duplicated)
└── models.py
```

### After Structure:

```
3.opena4_telegram/
├── main_telegram_agent.py   ← Updated imports
├── config.py                ← Simplified (70 lines)
└── models.py
```

### Changes to main_telegram_agent.py:

```python
# Old imports
# from safepoint_client import SafepointClient
# from sse_client import get_sse_client, get_safepoint_client
# from security import verify_token, mask_secrets

# New imports
from src.pkg.shared.safepoint_client import SafepointClient
from src.pkg.shared.sse_client import create_sse_client, create_safepoint_client
from src.pkg.shared.security import verify_token, mask_secrets

# Create agent-specific clients
sse_client = create_sse_client(source_agent="opena4")
safepoint_client = create_safepoint_client(source_agent="opena4")
```

### Changes to config.py:

```python
from typing import List
from pydantic import Field, field_validator
from src.pkg.shared.config_base import BaseAgentConfig, PortPolicy

class ServiceConfig(BaseAgentConfig):
    service_name: str = "opena4"
    kuerzel: str = "tgap"
    port: int = 12346

    # Agent-specific fields
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_allowed_users: List[int] = Field(default_factory=list)

    @field_validator("telegram_allowed_users", mode="before")
    @classmethod
    def parse_allowed_users(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return []

    def to_dict(self) -> dict:
        """Override to add telegram-specific fields."""
        base_dict = super().to_dict(mask_secrets=True)
        base_dict.update({
            "telegram_bot_token": "***" if self.telegram_bot_token else "",
            "telegram_allowed_users": self.telegram_allowed_users,
        })
        return base_dict
```

## Testing After Migration

1. **Import Test**: Verify imports work

   ```bash
   python3 -c "from src.pkg.shared import SafepointClient; print('✅ OK')"
   ```

2. **Agent Test**: Start the agent and verify functionality

   ```bash
   cd 3.opena4_telegram
   python3 main_telegram_agent.py
   ```

3. **Integration Test**: Test safepoint writes and SSE subscriptions

## Benefits

- **~380 lines** removed per agent (safepoint_client + sse_client + security)
- **Single source of truth** for bug fixes
- **Consistent behavior** across all agents
- **Easier maintenance** and updates
- **Better testability** with centralized tests

## Rollback

If issues occur, you can temporarily revert:

```bash
git checkout HEAD -- safepoint_client.py sse_client.py security.py
```

## Next Steps

1. Migrate one agent (e.g., opena4) as a pilot
2. Test thoroughly
3. Apply to remaining agents
4. Update documentation
5. Remove all duplicated files

## FAQ

**Q: Do I need to change my agent's functionality?**
A: No. The shared libraries provide the same API.

**Q: What if my agent has customizations?**
A: Keep the customizations in the agent's directory. Only common code goes to shared.

**Q: Can I still use environment variables?**
A: Yes. The shared modules read from the same environment variables.

**Q: What about backward compatibility?**
A: The factory functions (`create_sse_client`, `create_safepoint_client`) provide backward compatibility.
