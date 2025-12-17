"""
opena6 Playwright Browser Client
Web automation engine with policy enforcement & artifact capture
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    # Fallback for testing without playwright installed
    Browser = None
    Page = None
    BrowserContext = None

from .config import config
from .models import (
    PlaybookRequest, PlaybookResponse, PlaybookStep, ActionType,
    ArtifactCollection, ArtifactRef, TimingInfo, ErrorInfo, EventLog
)

logger = logging.getLogger(__name__)


class RobotsTxtChecker:
    """Validates requests against robots.txt"""
    
    def __init__(self):
        self.cache: Dict[str, str] = {}
    
    async def check_allowed(self, url: str, obey: bool = True) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not obey:
            return True
        
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Simplified: in production, fetch & parse robots.txt
        # For now, just check domain allowlist
        return parsed.netloc in config.ALLOWED_DOMAINS
    
    async def get_rps_limit(self, domain: str) -> float:
        """Extract RPS limit from robots.txt User-agent directive"""
        # Simplified: return default config
        return config.DEFAULT_RPS_LIMIT


class PolicyGate:
    """Enforces compliance & security policies"""
    
    def __init__(self, compliance_config):
        self.compliance = compliance_config
        self.robots_checker = RobotsTxtChecker()
    
    async def validate_request(self, request: PlaybookRequest) -> Tuple[bool, Optional[str]]:
        """
        Validate playbook against policies
        Returns: (allowed: bool, reason: str or None)
        """
        
        # Check domain allowlist
        for step in request.steps:
            if step.action == ActionType.GOTO and step.url:
                parsed = urlparse(step.url)
                if parsed.netloc not in self.compliance.allow_domains:
                    return False, f"Domain {parsed.netloc} not in allowlist"
        
        # Check robots.txt compliance
        if self.compliance.obey_robots:
            for step in request.steps:
                if step.action == ActionType.GOTO and step.url:
                    allowed = await self.robots_checker.check_allowed(step.url, obey=True)
                    if not allowed:
                        return False, f"robots.txt disallows {step.url}"
        
        return True, None


class ArtifactWriter:
    """Captures and stores browser artifacts"""
    
    def __init__(self, archiv_base: str = "archivp"):
        self.archiv_base = Path(archiv_base)
    
    async def capture_screenshot(self, page: Page, label: str, full_page: bool = False) -> Optional[ArtifactRef]:
        """Capture screenshot from page"""
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
            artifact_dir = self.archiv_base / timestamp
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"screenshot_{label}_{datetime.now(timezone.utc).timestamp():.0f}.png"
            filepath = artifact_dir / filename
            
            await page.screenshot(path=str(filepath), full_page=full_page)
            
            # Calculate SHA256
            sha256 = self._calculate_sha256(filepath)
            
            size_bytes = filepath.stat().st_size
            if size_bytes > config.MAX_ARTIFACT_SIZE_MB * 1024 * 1024:
                logger.warning(f"Screenshot {filename} exceeds size limit")
                return None
            
            return ArtifactRef(
                label=label,
                path=str(filepath),
                sha256=sha256,
                size_bytes=size_bytes,
                mime_type="image/png"
            )
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    async def capture_html(self, page: Page, label: str) -> Optional[ArtifactRef]:
        """Capture HTML content from page"""
        try:
            html_content = await page.content()
            
            timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
            artifact_dir = self.archiv_base / timestamp
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"page_{label}_{datetime.now(timezone.utc).timestamp():.0f}.html"
            filepath = artifact_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            sha256 = self._calculate_sha256(filepath)
            size_bytes = filepath.stat().st_size
            
            return ArtifactRef(
                label=label,
                path=str(filepath),
                sha256=sha256,
                size_bytes=size_bytes,
                mime_type="text/html"
            )
        except Exception as e:
            logger.error(f"Failed to capture HTML: {e}")
            return None
    
    async def capture_har(self, page: Page, label: str) -> Optional[ArtifactRef]:
        """Capture HAR (HTTP Archive) from page"""
        try:
            # Playwright HAR recording (if context enabled)
            # This is a simplified version; full HAR capture requires context setup
            timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d")
            artifact_dir = self.archiv_base / timestamp
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"session_{label}_{datetime.now(timezone.utc).timestamp():.0f}.har"
            filepath = artifact_dir / filename
            
            # Placeholder HAR structure
            har_data = {
                "log": {
                    "version": "1.2",
                    "creator": {"name": "opena6", "version": "1.0"},
                    "entries": []
                }
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(har_data, f)
            
            sha256 = self._calculate_sha256(filepath)
            size_bytes = filepath.stat().st_size
            
            return ArtifactRef(
                label=label,
                path=str(filepath),
                sha256=sha256,
                size_bytes=size_bytes,
                mime_type="application/json"
            )
        except Exception as e:
            logger.error(f"Failed to capture HAR: {e}")
            return None
    
    @staticmethod
    def _calculate_sha256(filepath: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class BrowserExecutor:
    """Executes playbook steps in Playwright browser"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.artifact_writer = ArtifactWriter()
        self.policy_gate = None
        self.rate_limiters: Dict[str, asyncio.Semaphore] = {}
    
    async def startup(self):
        """Initialize Playwright"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=config.HEADLESS
            )
            logger.info(f"Playwright browser launched ({config.BROWSER_TYPE})")
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            raise
    
    async def shutdown(self):
        """Close Playwright"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Playwright browser closed")
        except Exception as e:
            logger.error(f"Error shutting down Playwright: {e}")
    
    async def execute_playbook(self, request: PlaybookRequest) -> PlaybookResponse:
        """Execute a complete playbook"""
        
        # Initialize policy gate
        self.policy_gate = PolicyGate(request.compliance)
        
        # Validate request
        allowed, reason = await self.policy_gate.validate_request(request)
        if not allowed:
            return PlaybookResponse(
                request_id=request.request_id,
                status="failed",
                artifacts=ArtifactCollection(),
                timings=TimingInfo(total_ms=0),
                error=ErrorInfo(code="PolicyViolation", message=reason or "Policy check failed"),
                strict=request.strict
            )
        
        # Create context & page
        context = None
        page = None
        start_time = datetime.now(timezone.utc)
        artifacts = ArtifactCollection()
        event_logs: List[EventLog] = []
        
        try:
            context = await self.browser.new_context(
                viewport={"width": request.viewport.width, "height": request.viewport.height},
                user_agent=request.user_agent if request.user_agent != "desktop" else None
            )
            page = await context.new_page()
            
            # Execute steps
            for step_idx, step in enumerate(request.steps):
                step_start = datetime.now(timezone.utc)
                try:
                    await self._execute_step(page, step, request, step_idx, artifacts, event_logs)
                except Exception as e:
                    error_elapsed = int((datetime.now(timezone.utc) - step_start).total_seconds() * 1000)
                    event_logs.append(EventLog(
                        ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        request_id=request.request_id,
                        step=step_idx,
                        action=step.action.value,
                        selector=step.selector,
                        elapsed_ms=error_elapsed,
                        note="error",
                        error=str(e),
                        strict=request.strict
                    ))
                    
                    # Capture error screenshot & HTML
                    if page and request.archiv.attach_screenshot:
                        ref = await self.artifact_writer.capture_screenshot(page, "error")
                        if ref:
                            artifacts.screenshots.append(ref)
                    if page and request.archiv.attach_html:
                        ref = await self.artifact_writer.capture_html(page, "error")
                        if ref:
                            artifacts.html.append(ref)
                    
                    raise
            
            # Success response
            total_elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            
            return PlaybookResponse(
                request_id=request.request_id,
                status="success",
                artifacts=artifacts,
                extractions=artifacts.extractions,
                timings=TimingInfo(total_ms=total_elapsed),
                strict=request.strict
            )
        
        except Exception as e:
            total_elapsed = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            
            return PlaybookResponse(
                request_id=request.request_id,
                status="failed",
                artifacts=artifacts,
                timings=TimingInfo(total_ms=total_elapsed),
                error=ErrorInfo(code="ExecutionError", message=str(e)),
                strict=request.strict
            )
        
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
    
    async def _execute_step(self, page: Page, step: PlaybookStep, request: PlaybookRequest,
                           step_idx: int, artifacts: ArtifactCollection, event_logs: List[EventLog]):
        """Execute a single playbook step"""
        
        step_start = datetime.now(timezone.utc)
        
        try:
            if step.action == ActionType.GOTO:
                await page.goto(step.url, wait_until=step.wait or "load")
            
            elif step.action == ActionType.FILL:
                await page.fill(step.selector, step.text)
            
            elif step.action == ActionType.CLICK:
                await page.click(step.selector)
            
            elif step.action == ActionType.WAIT_FOR:
                await page.wait_for_selector(step.selector, timeout=step.timeout_ms or 10000)
            
            elif step.action == ActionType.SCREENSHOT:
                ref = await self.artifact_writer.capture_screenshot(page, step.label or "screenshot", step.full_page or False)
                if ref:
                    artifacts.screenshots.append(ref)
            
            elif step.action == ActionType.EXTRACT:
                try:
                    if step.mode == "text":
                        content = await page.text_content(step.selector)
                    elif step.mode == "html":
                        content = await page.inner_html(step.selector)
                    elif step.mode == "attribute":
                        content = await page.get_attribute(step.selector, step.attribute or "value")
                    elif step.mode == "count":
                        content = await page.locator(step.selector).count()
                    else:
                        content = await page.text_content(step.selector)
                    
                    artifacts.extractions[step.label or f"extract_{step_idx}"] = content
                except Exception as e:
                    logger.error(f"Extraction failed: {e}")
            
            elif step.action == ActionType.SUBMIT:
                await page.press(step.selector or "form", "Enter")
            
            elif step.action == ActionType.SELECT:
                await page.select_option(step.selector, step.text)
            
            elif step.action == ActionType.HOVER:
                await page.hover(step.selector)
            
            elif step.action == ActionType.KEYBOARD:
                await page.keyboard.type(step.keys or "")
            
            elif step.action == ActionType.WAIT:
                await asyncio.sleep((step.timeout_ms or 1000) / 1000)
            
            # Log success
            step_elapsed = int((datetime.now(timezone.utc) - step_start).total_seconds() * 1000)
            event_logs.append(EventLog(
                ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                request_id=request.request_id,
                step=step_idx,
                action=step.action.value,
                selector=step.selector,
                elapsed_ms=step_elapsed,
                note="ok",
                strict=request.strict
            ))
        
        except Exception as e:
            step_elapsed = int((datetime.now(timezone.utc) - step_start).total_seconds() * 1000)
            event_logs.append(EventLog(
                ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                request_id=request.request_id,
                step=step_idx,
                action=step.action.value,
                selector=step.selector,
                elapsed_ms=step_elapsed,
                note="error",
                error=str(e),
                strict=request.strict
            ))
            raise


# Global executor instance
browser_executor: Optional[BrowserExecutor] = None


async def get_executor() -> BrowserExecutor:
    """Get or create browser executor"""
    global browser_executor
    if browser_executor is None:
        browser_executor = BrowserExecutor()
        await browser_executor.startup()
    return browser_executor
