"""
opena6 Data Models & Schemas
Browser Agent — Playbook, Artifacts, Safepoints
"""

import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Playbook action types"""

    GOTO = "goto"
    FILL = "fill"
    CLICK = "click"
    WAIT_FOR = "wait_for"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"
    DOWNLOAD = "download"
    SUBMIT = "submit"
    SELECT = "select"
    HOVER = "hover"
    KEYBOARD = "keyboard"
    WAIT = "wait"


class ExtractMode(str, Enum):
    """Data extraction modes"""

    TEXT = "text"
    HTML = "html"
    ATTRIBUTE = "attribute"
    VALUE = "value"
    COUNT = "count"


class WaitCondition(str, Enum):
    """Wait conditions"""

    NETWORKIDLE = "networkidle"
    DOMCONTENTLOADED = "domcontentloaded"
    LOAD = "load"
    SELECTOR = "selector"
    TIMEOUT = "timeout"


class PlaybookStep(BaseModel):
    """Single step in a playbook"""

    action: ActionType
    selector: str | None = None
    url: str | None = None
    text: str | None = None
    timeout_ms: int | None = None
    wait: str | None = None
    full_page: bool | None = False
    label: str | None = None
    mode: ExtractMode | None = None
    attribute: str | None = None
    type: str | None = None  # for download type (pdf, png, etc)
    keys: str | None = None  # for keyboard input


class ViewportConfig(BaseModel):
    """Browser viewport configuration"""

    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=800, ge=240, le=2160)


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""

    per_domain_rps: float = Field(default=1.0, ge=0.1, le=10.0)


class ComplianceConfig(BaseModel):
    """Compliance & security configuration"""

    allow_domains: list[str] = Field(default=["localhost", "127.0.0.1"])
    obey_robots: bool = True
    legal_basis: str | None = "contractual"  # contractual, consent, legit_interest


class ArtifactConfig(BaseModel):
    """Artifact attachment configuration"""

    attach_html: bool = True
    attach_har: bool = False
    attach_pdf: bool = False
    attach_screenshot: bool = True


class DownloadConfig(BaseModel):
    """File download specification"""

    type: str  # pdf, png, jpeg, html, txt
    selector: str | None = None
    label: str = Field(default="download")


class PlaybookRequest(BaseModel):
    """Complete playbook execution request"""

    request_id: str | None = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[PlaybookStep]
    user_agent: str = "desktop"  # desktop, mobile, or custom UA string
    headless: bool = True
    viewport: ViewportConfig = Field(default_factory=ViewportConfig)
    download: list[DownloadConfig] | None = None
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    archiv: ArtifactConfig = Field(default_factory=ArtifactConfig)
    strict: bool = True


class ArtifactRef(BaseModel):
    """Reference to an archived artifact"""

    label: str
    path: str
    sha256: str | None = None
    size_bytes: int | None = None
    mime_type: str | None = None


class ArtifactCollection(BaseModel):
    """Collection of artifacts from a run"""

    screenshots: list[ArtifactRef] = Field(default_factory=list)
    html: list[ArtifactRef] = Field(default_factory=list)
    pdf: list[ArtifactRef] = Field(default_factory=list)
    har: list[ArtifactRef] = Field(default_factory=list)
    extractions: dict[str, Any] = Field(default_factory=dict)


class TimingInfo(BaseModel):
    """Execution timing information"""

    total_ms: int
    per_step_ms: dict[str, int] = Field(default_factory=dict)


class ErrorInfo(BaseModel):
    """Error details in failure response"""

    code: str
    message: str
    step: int | None = None
    selector: str | None = None


class PlaybookResponse(BaseModel):
    """Response from playbook execution"""

    request_id: str
    status: str  # success, failed, canceled
    artifacts: ArtifactCollection = Field(default_factory=ArtifactCollection)
    extractions: dict[str, Any] = Field(default_factory=dict)
    timings: TimingInfo
    error: ErrorInfo | None = None
    strict: bool = True


class CancelRequest(BaseModel):
    """Request to cancel a running playbook"""

    request_id: str


class CancelResponse(BaseModel):
    """Response to cancel request"""

    request_id: str
    canceled: bool
    at_step: int | None = None


class HealthResponse(BaseModel):
    """Health check response"""

    service: str
    status: str  # ok, degraded, error
    component: str
    port: int
    browser: str | None = None
    ts: str


class ReadyResponse(BaseModel):
    """Readiness check response"""

    ready: bool
    browser: str | None = None
    version: str | None = None


class Safepoint(BaseModel):
    """Safepoint structure for archiving"""

    ts: str  # ISO 8601 timestamp
    src: str  # source agent (opena6)
    dst: str  # destination (opena2)
    kind: str  # CMD, RESP, LOG
    request_id: str
    payload: Any


class EventLog(BaseModel):
    """Structured event log entry (JSONL)"""

    ts: str  # ISO 8601
    request_id: str
    step: int
    action: str
    selector: str | None = None
    elapsed_ms: int
    note: str
    error: str | None = None
    strict: bool = True
