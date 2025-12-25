"""
Telegram Multi-Bot FastAPI Server (Port 8000)
Webhook-based, Multi-tenant, Option-2 compliant
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.routes import router as admin_router
from app.config import settings
from app.db.models import SQLModel
from app.db.session import engine
from app.telegram.webhooks import router as telegram_router

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""

    # Startup
    logger.info("🚀 Telegram Multi-Bot starting...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("✅ Database initialized")

    yield

    # Shutdown
    logger.info("🛑 Telegram Multi-Bot shutting down...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Telegram Multi-Bot",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telegram_router)
app.include_router(admin_router)

# Optional tracing: initialize if environment and packages permit
try:
    from pkg.observability import init_tracing

    init_tracing(app, service_name="telegram_multi")
except Exception as _e:  # pragma: no cover - optional
    logger.debug("Tracing not initialized or not available: %s", _e)


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "service": "telegram_multi",
        "port": settings.api_port,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Telegram Multi-Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "telegram_webhook": "/telegram/webhook/{bot_key}",
            "admin_register": "/admin/register-bot",
            "admin_webhooks": "/admin/set-webhooks",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
