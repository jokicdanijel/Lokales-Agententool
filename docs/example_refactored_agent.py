#!/usr/bin/env python3
"""
Example Refactored Agent using Shared Modules
==============================================

This is a reference implementation showing how to use the shared modules
to eliminate code duplication.

Before refactoring:
- 577 lines with duplicated auth, health, datastore logic
- Manual token loading and validation
- Custom health response formatting
- Custom datastore implementation

After refactoring:
- ~300 lines focused on business logic
- Shared auth utilities
- Standard health responses
- Inherited datastore with minimal code

Reduction: ~48% fewer lines, clearer structure

Note: Uses Pydantic V2 ConfigDict style for consistency with opena6 browser agent.
"""

import logging
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# IMPORT SHARED MODULES (NEW!)
# ============================================================================
from src.pkg.shared import (  # Authentication; Base Models; Persistence; Configuration
    AuditLog,
    BaseDataStore,
    CommandRequest,
    create_health_response,
    create_service_info,
    create_token_verifier,
    get_port_from_env,
    load_bearer_token_from_env,
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Service metadata
SERVICE_NAME = "opena_example"
KUERZEL = "examplep"
VERSION = "1.0"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "example_agent" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load configuration using shared utilities
BEARER_TOKEN = load_bearer_token_from_env(PROJECT_ROOT)
PORT = get_port_from_env("EXAMPLE_PORT", 12380, SERVICE_NAME)
HOST = os.getenv("EXAMPLE_HOST", "127.0.0.1")

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(SERVICE_NAME)

# ============================================================================
# DOMAIN MODELS
# ============================================================================


@dataclass
class ExampleItem:
    """Example business domain model."""

    id: str
    name: str
    value: int
    created_at: str = ""
    active: bool = True


# ============================================================================
# PERSISTENCE LAYER (Using Shared BaseDataStore)
# ============================================================================


class ExampleItemStore(BaseDataStore[ExampleItem]):
    """
    Store for example items.

    Only need to implement serialization methods - everything else inherited!
    """

    def _serialize(self, item: ExampleItem) -> dict:
        """Convert ExampleItem to dictionary."""
        return asdict(item)

    def _deserialize(self, data: dict) -> ExampleItem:
        """Convert dictionary to ExampleItem."""
        return ExampleItem(**data)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CreateItemRequest(BaseModel):
    """Request to create a new item."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=200)
    value: int = Field(..., ge=0)


class ItemResponse(BaseModel):
    """Response with item data."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    value: int
    created_at: str
    active: bool


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=f"{SERVICE_NAME} - Example Refactored Agent",
    description="Reference implementation using shared modules",
    version=VERSION,
)

# Initialize stores using shared classes
item_store = ExampleItemStore(DATA_DIR / "items.json")
audit_log = AuditLog(DATA_DIR / "audit.jsonl")

# Create token verifier using shared utility
verify_token = create_token_verifier(BEARER_TOKEN)

# Track service start time
START_TIME = time.time()

# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint - service information."""
    # Use shared factory function
    return create_service_info(
        service=SERVICE_NAME,
        kuerzel=KUERZEL,
        description="Example refactored agent using shared modules",
        port=PORT,
        version=VERSION,
        endpoints=["/health", "/items", "/items/create", "/command"],
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    # Use shared factory function - one line instead of 10!
    return create_health_response(
        service=SERVICE_NAME,
        kuerzel=KUERZEL,
        port=PORT,
        start_time=START_TIME,
        # Extra service-specific info
        items_count=item_store.count(),
        audit_entries=audit_log.count(),
    )


@app.get("/items", response_model=list[ItemResponse])
async def list_items(active_only: bool = True, user: str = Depends(verify_token)):
    """List all items (authenticated)."""
    # Load and filter
    items = item_store.load()
    if active_only:
        items = [item for item in items if item.active]

    return [ItemResponse(**asdict(item)) for item in items]


@app.post("/items/create", response_model=ItemResponse)
async def create_item(req: CreateItemRequest, user: str = Depends(verify_token)):
    """Create a new item (authenticated)."""
    import uuid
    from datetime import datetime

    # Create item
    item = ExampleItem(
        id=str(uuid.uuid4()),
        name=req.name,
        value=req.value,
        created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        active=True,
    )

    # Save using inherited method
    item_store.add(item)

    # Audit using shared AuditLog
    audit_log.log(
        operation="CREATE_ITEM",
        actor=user,
        resource_type="item",
        resource_id=item.id,
        result="success",
        details={"name": item.name, "value": item.value},
    )

    logger.info(f"Created item {item.id}: {item.name}")
    return ItemResponse(**asdict(item))


@app.post("/command")
async def handle_command(req: CommandRequest, user: str = Depends(verify_token)):
    """
    Handle generic command (Option-2-Flow compatibility).

    Uses shared CommandRequest model!
    """
    cmd = req.command.lower()

    if cmd == "list":
        items = await list_items(active_only=True, user=user)
        return {"status": "success", "command": cmd, "result": items}

    elif cmd == "create":
        create_req = CreateItemRequest(**req.params)
        item = await create_item(create_req, user)
        return {"status": "success", "command": cmd, "result": item}

    elif cmd == "stats":
        return {
            "status": "success",
            "command": cmd,
            "result": {"total_items": item_store.count(), "audit_entries": audit_log.count()},
        }

    else:
        return {"status": "error", "message": f"Unknown command: {cmd}"}


# ============================================================================
# STARTUP
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    # Load data
    item_store.load()

    logger.info(f"🚀 {SERVICE_NAME} ({KUERZEL}) started on {HOST}:{PORT}")
    logger.info(f"📁 Data directory: {DATA_DIR}")
    logger.info(f"📦 Items loaded: {item_store.count()}")
    logger.info(f"📜 Audit entries: {audit_log.count()}")

    if not BEARER_TOKEN:
        logger.warning("⚠️  BEARER_TOKEN not set - authentication disabled!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
