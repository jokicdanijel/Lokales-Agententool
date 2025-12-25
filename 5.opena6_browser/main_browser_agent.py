#!/usr/bin/env python3
"""
opena6 – Browser Automation Agent (Playwright)
Port: 12350 | Kürzel: browsep
Compliance: PORTIER 3.0 (Option-2-Flow, Strict JSON, ENV-only Secrets)
"""

import base64
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

# Playwright Import (mit Fallback)
try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    PlaywrightTimeout = Exception

# ============================================================================
# KONFIGURATION (ENV-only, niemals hardcoded)
# ============================================================================

PORT = int(os.getenv("OPENA6_PORT", "12350"))
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
ARCHIVP_ROOT = Path(os.getenv("ARCHIVP_ROOT", "../1.opena1&2_portier/archivp_store"))
SCREENSHOT_DIR = Path(os.getenv("SCREENSHOT_DIR", "data/screenshots"))
MAX_PARALLEL_BROWSERS = int(os.getenv("MAX_PARALLEL_BROWSERS", "3"))
HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
DEFAULT_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # ms
USER_AGENT = os.getenv("BROWSER_USER_AGENT", "")

# Port-Policy (PORTIER 3.0 Standard)
PORTS_ALLOWED = list(range(12344, 12400))
PORT_FORBIDDEN = [8080]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[logging.FileHandler("logs/opena6.nohup.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("opena6")

# ============================================================================
# PORT-POLICY ENFORCEMENT (Startup)
# ============================================================================

if PORT not in PORTS_ALLOWED:
    logger.error(f"❌ FATAL: Port {PORT} nicht im erlaubten Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")
    sys.exit(1)

if PORT in PORT_FORBIDDEN:
    logger.error(f"❌ FATAL: Port {PORT} ist für Backend verboten (nur UI)!")
    sys.exit(1)

logger.info(f"✅ Port-Policy OK: {PORT} in Bereich {PORTS_ALLOWED[0]}-{PORTS_ALLOWED[-1]}")

# ============================================================================
# BEARER TOKEN VALIDATION
# ============================================================================

if not BEARER_TOKEN:
    logger.error("❌ FATAL: BEARER_TOKEN nicht gesetzt in .env")
    sys.exit(1)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Bearer token")
    return True


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena6 – Browser Automation Agent",
    description="Playwright-based browser automation (PORTIER 3.0)",
    version="1.0.0",
)

# Optional tracing: initialize if environment and packages permit
try:
    from pkg.observability import init_tracing

    init_tracing(app, service_name="opena6")
except Exception as _e:  # pragma: no cover - optional
    logger.debug("Tracing not initialized or not available: %s", _e)

# ============================================================================
# STARTUP
# ============================================================================

START_TIME = time.time()

# Erstelle Screenshot-Verzeichnis
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVP_ROOT.mkdir(parents=True, exist_ok=True)

logger.info("🚀 opena6 (Browser Agent) startet...")
logger.info(f"   Port: {PORT}")
logger.info(f"   Browser: {BROWSER_TYPE} (Headless: {HEADLESS})")
logger.info(f"   Playwright: {'✅ Available' if PLAYWRIGHT_AVAILABLE else '❌ Not installed'}")
logger.info(f"   Screenshot-Dir: {SCREENSHOT_DIR.absolute()}")
logger.info(f"   Archiv: {ARCHIVP_ROOT.absolute()}")
logger.info(f"   Max Parallel: {MAX_PARALLEL_BROWSERS}")

# ============================================================================
# PYDANTIC SCHEMAS (Strict JSON)
# ============================================================================


class NavigateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., description="Target URL to navigate")
    wait_until: str = Field(
        "load", description="When to consider navigation done (load, domcontentloaded, networkidle)"
    )
    timeout: int = Field(DEFAULT_TIMEOUT, description="Timeout in milliseconds")


class ScreenshotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., description="Target URL")
    selector: str | None = Field(None, description="CSS selector for element screenshot")
    full_page: bool = Field(False, description="Capture full page (scrolling)")
    format: str = Field("png", description="Image format (png, jpeg)")
    timeout: int = Field(DEFAULT_TIMEOUT, description="Timeout in milliseconds")


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., description="Target URL")
    selectors: dict[str, str] = Field(..., description="Map of name -> CSS selector")
    wait_for: str | None = Field(None, description="Selector to wait for before extraction")
    timeout: int = Field(DEFAULT_TIMEOUT, description="Timeout in milliseconds")


class ClickRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., description="Target URL")
    selector: str = Field(..., description="CSS selector to click")
    wait_after: int = Field(1000, description="Wait milliseconds after click")
    timeout: int = Field(DEFAULT_TIMEOUT, description="Timeout in milliseconds")


class FormFillRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., description="Target URL")
    fields: dict[str, str] = Field(..., description="Map of selector -> value")
    submit_selector: str | None = Field(None, description="Submit button selector")
    wait_after_submit: int = Field(2000, description="Wait after submit (ms)")
    timeout: int = Field(DEFAULT_TIMEOUT, description="Timeout in milliseconds")


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: str = Field(..., description="Command to execute")
    params: dict[str, Any] = Field(default_factory=dict, description="Command parameters")


# ============================================================================
# SAFEPOINT SYSTEM (PORTIER 3.0)
# ============================================================================


def mask_secrets(data: Any) -> Any:
    """Maskiert Secrets in Daten (Bearer-Token, API-Keys, Passwords)"""
    if isinstance(data, dict):
        return {
            k: (
                "***"
                if any(s in k.lower() for s in ["token", "password", "secret", "key", "bearer", "auth"])
                else mask_secrets(v)
            )
            for k, v in data.items()
        }
    elif isinstance(data, str):
        # Kürze lange Strings (z.B. Base64-Screenshots)
        if len(data) > 200:
            return data[:200] + f"... [truncated {len(data) - 200} chars]"
        # Maskiere URLs mit Tokens
        if "?" in data and any(s in data.lower() for s in ["token=", "key=", "auth="]):
            return data.split("?")[0] + "?***"
    return data


def write_safepoint(src: str, dst: str, msg_type: str, data: dict[str, Any], request_id: str):
    """Schreibt Safepoint im PORTIER 3.0 Format"""
    try:
        now = datetime.now(UTC)
        date_path = ARCHIVP_ROOT / now.strftime("%Y/%m/%d")
        date_path.mkdir(parents=True, exist_ok=True)

        ts = now.strftime("%Y%m%d%H%M%S%f")[:17]
        # Unicode-Pfeil → (U+2192) – PFLICHT
        filename = f"SP{ts}_{src}→{dst}_{msg_type}.json"
        filepath = date_path / filename

        masked_data = mask_secrets(data)

        envelope = {
            "sp_id": ts,
            "request_id": request_id,
            "timestamp": now.isoformat().replace("+00:00", "Z"),
            "src": src,
            "dst": dst,
            "type": msg_type,
            "data": masked_data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2, ensure_ascii=False)

        logger.debug(f"✅ Safepoint: {filename}")
    except Exception as e:
        logger.error(f"❌ Safepoint-Fehler: {e}")


# ============================================================================
# BROWSER AUTOMATION HELPERS
# ============================================================================


def execute_with_browser(action_fn, request_id: str):
    """Führt Aktion mit Playwright-Browser aus"""
    if not PLAYWRIGHT_AVAILABLE:
        raise HTTPException(
            status_code=503, detail="Playwright not installed. Run: pip install playwright && playwright install"
        )

    try:
        with sync_playwright() as p:
            browser_launcher = getattr(p, BROWSER_TYPE)
            browser = browser_launcher.launch(headless=HEADLESS)

            # User-Agent setzen (falls konfiguriert)
            context_options = {}
            if USER_AGENT:
                context_options["user_agent"] = USER_AGENT

            context = browser.new_context(**context_options)
            page = context.new_page()

            try:
                result = action_fn(page)
                return result
            finally:
                context.close()
                browser.close()

    except PlaywrightTimeout:
        raise HTTPException(status_code=504, detail="Browser action timed out")
    except Exception as e:
        logger.error(f"❌ Browser error: {e}")
        raise HTTPException(status_code=500, detail=f"Browser error: {e!s}")


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health-Check mit Browser-Status"""
    uptime = time.time() - START_TIME
    return JSONResponse(
        {
            "status": "ok",
            "agent": "opena6",
            "port": PORT,
            "kuerzel": "browsep",
            "uptime": round(uptime, 2),
            "playwright_available": PLAYWRIGHT_AVAILABLE,
            "browser_type": BROWSER_TYPE,
            "headless": HEADLESS,
            "screenshot_dir": str(SCREENSHOT_DIR.absolute()),
            "max_parallel": MAX_PARALLEL_BROWSERS,
        }
    )


@app.get("/")
async def root():
    """Agent-Info"""
    return JSONResponse(
        {
            "agent": "opena6",
            "kuerzel": "browsep",
            "port": PORT,
            "status": "running",
            "capabilities": ["navigate", "screenshot", "extract", "click", "form_fill"],
            "browser": {"type": BROWSER_TYPE, "headless": HEADLESS, "playwright": PLAYWRIGHT_AVAILABLE},
        }
    )


@app.post("/navigate")
async def navigate(req: NavigateRequest, _: bool = Depends(verify_token)):
    """Navigiere zu URL"""
    request_id = str(uuid4())

    write_safepoint(
        "browsep",
        "kordp",
        "CMD",
        {"endpoint": "/navigate", "url": req.url, "wait_until": req.wait_until, "timeout": req.timeout},
        request_id,
    )

    def action(page):
        page.goto(req.url, wait_until=req.wait_until, timeout=req.timeout)
        return {"url": page.url, "title": page.title(), "status": "success"}

    result = execute_with_browser(action, request_id)

    write_safepoint("kordp", "browsep", "RESP", result, request_id)

    return JSONResponse(result)


@app.post("/screenshot")
async def screenshot(req: ScreenshotRequest, _: bool = Depends(verify_token)):
    """Erstelle Screenshot"""
    request_id = str(uuid4())

    write_safepoint(
        "browsep",
        "kordp",
        "CMD",
        {
            "endpoint": "/screenshot",
            "url": req.url,
            "selector": req.selector,
            "full_page": req.full_page,
            "format": req.format,
        },
        request_id,
    )

    def action(page):
        page.goto(req.url, timeout=req.timeout)

        # Screenshot erstellen
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.{req.format}"
        filepath = SCREENSHOT_DIR / filename

        if req.selector:
            # Element-Screenshot
            element = page.locator(req.selector)
            element.screenshot(path=str(filepath), type=req.format)
        else:
            # Page-Screenshot
            page.screenshot(path=str(filepath), full_page=req.full_page, type=req.format)

        # Optional: Base64 für kleine Screenshots
        with open(filepath, "rb") as f:
            img_bytes = f.read()

        # Nur kleine Bilder als Base64 (< 1 MB)
        base64_data = None
        if len(img_bytes) < 1_000_000:
            base64_data = base64.b64encode(img_bytes).decode("utf-8")

        return {
            "path": str(filepath.absolute()),
            "filename": filename,
            "size_bytes": len(img_bytes),
            "base64": base64_data,
            "url": req.url,
        }

    result = execute_with_browser(action, request_id)

    # Entferne Base64 aus Safepoint (zu groß)
    safe_result = {**result, "base64": "*** [excluded from safepoint]" if result.get("base64") else None}
    write_safepoint("kordp", "browsep", "RESP", safe_result, request_id)

    return JSONResponse(result)


@app.post("/extract")
async def extract(req: ExtractRequest, _: bool = Depends(verify_token)):
    """Extrahiere Daten via CSS-Selektoren"""
    request_id = str(uuid4())

    write_safepoint(
        "browsep",
        "kordp",
        "CMD",
        {"endpoint": "/extract", "url": req.url, "selectors": req.selectors, "wait_for": req.wait_for},
        request_id,
    )

    def action(page):
        page.goto(req.url, timeout=req.timeout)

        # Optional: Warte auf Element
        if req.wait_for:
            page.wait_for_selector(req.wait_for, timeout=req.timeout)

        # Extrahiere Daten
        extracted = {}
        for name, selector in req.selectors.items():
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    # Text extrahieren
                    extracted[name] = element.first.text_content()
                else:
                    extracted[name] = None
            except Exception as e:
                extracted[name] = f"Error: {e!s}"

        return {"url": req.url, "extracted": extracted, "status": "success"}

    result = execute_with_browser(action, request_id)

    write_safepoint("kordp", "browsep", "RESP", result, request_id)

    return JSONResponse(result)


@app.post("/click")
async def click(req: ClickRequest, _: bool = Depends(verify_token)):
    """Klicke Element"""
    request_id = str(uuid4())

    write_safepoint(
        "browsep",
        "kordp",
        "CMD",
        {"endpoint": "/click", "url": req.url, "selector": req.selector, "wait_after": req.wait_after},
        request_id,
    )

    def action(page):
        page.goto(req.url, timeout=req.timeout)
        page.click(req.selector, timeout=req.timeout)

        # Warte nach Click
        if req.wait_after > 0:
            page.wait_for_timeout(req.wait_after)

        return {"url": page.url, "status": "clicked", "selector": req.selector}

    result = execute_with_browser(action, request_id)

    write_safepoint("kordp", "browsep", "RESP", result, request_id)

    return JSONResponse(result)


@app.post("/form/fill")
async def form_fill(req: FormFillRequest, _: bool = Depends(verify_token)):
    """Fülle Formular aus"""
    request_id = str(uuid4())

    write_safepoint(
        "browsep",
        "kordp",
        "CMD",
        {
            "endpoint": "/form/fill",
            "url": req.url,
            "fields": mask_secrets(req.fields),  # Maskiere Passwörter
            "submit_selector": req.submit_selector,
        },
        request_id,
    )

    def action(page):
        page.goto(req.url, timeout=req.timeout)

        # Fülle Felder
        for selector, value in req.fields.items():
            page.fill(selector, value)

        # Optional: Submit
        if req.submit_selector:
            page.click(req.submit_selector)
            page.wait_for_timeout(req.wait_after_submit)

        return {
            "url": page.url,
            "status": "filled",
            "fields_filled": len(req.fields),
            "submitted": bool(req.submit_selector),
        }

    result = execute_with_browser(action, request_id)

    write_safepoint("kordp", "browsep", "RESP", result, request_id)

    return JSONResponse(result)


@app.post("/command")
async def command(req: CommandRequest, _: bool = Depends(verify_token)):
    """Generischer Command-Endpoint (Option-2-Flow Compatibility)"""
    request_id = str(uuid4())

    write_safepoint("browsep", "kordp", "CMD", {"command": req.command, "params": mask_secrets(req.params)}, request_id)

    response = {
        "status": "executed",
        "command": req.command,
        "agent": "opena6",
        "result": "Command received (use specific endpoints for browser actions)",
    }

    write_safepoint("kordp", "browsep", "RESP", response, request_id)

    return JSONResponse(response)


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("✅ opena6 bereit!")
    logger.info(f"   Health: http://127.0.0.1:{PORT}/health")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
