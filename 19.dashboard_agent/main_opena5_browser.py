"""
opena5_Browser: Web Automation Agent
Orchestrates browser automation via Selenium
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import logging
import asyncio
import json
import urllib.request
from datetime import datetime
from typing import Optional, Dict, List
import os
import sys
import base64

sys.path.insert(0, os.path.dirname(__file__))

from browser_selenium import BrowserAutomation, init_browser

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="opena5_Browser",
    version="1.0.0",
    description="Web Automation Browser Agent"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12353
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# Global browser instance
browser: Optional[BrowserAutomation] = None

# ============================================================================
# DATA MODELS
# ============================================================================


class NavigateRequest(BaseModel):
    url: str
    wait_time: int = 10


class ClickRequest(BaseModel):
    selector: str
    selector_type: str = "css"  # css or xpath


class FormFillRequest(BaseModel):
    fields: Dict[str, str]


class WaitElementRequest(BaseModel):
    selector: str
    selector_type: str = "css"
    timeout: int = 10


class ExecuteScriptRequest(BaseModel):
    script: str


class ScreenshotRequest(BaseModel):
    format: str = "base64"  # base64 or file


# ============================================================================
# LIFECYCLE
# ============================================================================


@app.on_event("startup")
async def startup():
    """Initialize browser on startup"""
    global browser
    try:
        browser = await init_browser(headless=True)
        logger.info("✅ opena5_Browser startup complete")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Close browser on shutdown"""
    global browser
    if browser:
        await browser.close()
        logger.info("✅ opena5_Browser shutdown complete")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: Optional[str]):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict) -> dict:
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena5_browser",
            "dst": "opena2",
            "kind": "BROWSER_OP",
            "payload": {
                **payload,
                "ts": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=5) as r:
            result = json.loads(r.read().decode())
            return result
    except Exception as e:
        logger.warning(f"⚠️ Archive failed (non-fatal): {e}")
        return {"written": False}


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "opena5_Browser",
        "port": PORT,
        "browser_initialized": browser.is_initialized() if browser else False,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/navigate")
async def navigate(req: NavigateRequest, authorization: str = Header(None)):
    """Navigate to URL"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        success = await browser.navigate(req.url, req.wait_time)
        
        await _archive({
            "op": "NAVIGATE",
            "url": req.url,
            "success": success,
            "wait_time": req.wait_time
        })
        
        return {
            "strict": True,
            "navigated": success,
            "url": req.url,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Navigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/click")
async def click(req: ClickRequest, authorization: str = Header(None)):
    """Click element"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        success = await browser.click_element(req.selector)
        
        await _archive({
            "op": "CLICK",
            "selector": req.selector,
            "success": success
        })
        
        return {
            "strict": True,
            "clicked": success,
            "selector": req.selector,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Click failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fill")
async def fill_form(req: FormFillRequest, authorization: str = Header(None)):
    """Fill form fields"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        success = await browser.fill_form(req.fields)
        
        await _archive({
            "op": "FORM_FILL",
            "field_count": len(req.fields),
            "success": success
        })
        
        return {
            "strict": True,
            "filled": success,
            "fields": len(req.fields),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Form fill failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/wait")
async def wait_element(req: WaitElementRequest, authorization: str = Header(None)):
    """Wait for element to appear"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        success = await browser.wait_for_element(req.selector, timeout=req.timeout)
        
        await _archive({
            "op": "WAIT_ELEMENT",
            "selector": req.selector,
            "timeout": req.timeout,
            "found": success
        })
        
        return {
            "strict": True,
            "found": success,
            "selector": req.selector,
            "timeout": req.timeout,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Wait failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/screenshot")
async def screenshot(req: ScreenshotRequest, authorization: str = Header(None)):
    """Take screenshot"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        screenshot_data = await browser.get_screenshot()
        
        await _archive({
            "op": "SCREENSHOT",
            "format": req.format,
            "size": len(screenshot_data) if screenshot_data else 0
        })
        
        return {
            "strict": True,
            "screenshot": screenshot_data[:100] + "..." if screenshot_data else None,
            "format": req.format,
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute")
async def execute(req: ExecuteScriptRequest, authorization: str = Header(None)):
    """Execute JavaScript"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        result = await browser.execute_script(req.script)
        
        await _archive({
            "op": "EXECUTE_SCRIPT",
            "script_length": len(req.script),
            "result_type": type(result).__name__
        })
        
        return {
            "strict": True,
            "result": str(result)[:500],
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Script execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cookies")
async def get_cookies(authorization: str = Header(None)):
    """Get current cookies"""
    _validate_token(authorization)
    
    if not browser or not browser.is_initialized():
        raise HTTPException(status_code=503, detail="Browser not available")
    
    try:
        cookies = await browser.get_cookies()
        
        await _archive({
            "op": "GET_COOKIES",
            "count": len(cookies)
        })
        
        return {
            "strict": True,
            "cookies": cookies,
            "count": len(cookies),
            "ts": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"❌ Failed to get cookies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)
    
    return {
        "service": "opena5_Browser",
        "version": "1.0.0",
        "port": PORT,
        "browser_initialized": browser.is_initialized() if browser else False,
        "endpoints": 8,
        "ts": datetime.utcnow().isoformat() + "Z"
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting opena5_Browser on port {PORT}")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info"
    )
