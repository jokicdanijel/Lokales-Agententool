"""
opena6 Data Models & Schemas
Browser Agent — Playbook, Artifacts, Safepoints
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


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
    selector: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    timeout_ms: Optional[int] = None
    wait: Optional[str] = None
    full_page: Optional[bool] = False
    label: Optional[str] = None
    mode: Optional[ExtractMode] = None
    attribute: Optional[str] = None
    type: Optional[str] = None  # for download type (pdf, png, etc)
    keys: Optional[str] = None  # for keyboard input


class ViewportConfig(BaseModel):
    """Browser viewport configuration"""
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=800, ge=240, le=2160)


class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    per_domain_rps: float = Field(default=1.0, ge=0.1, le=10.0)


class ComplianceConfig(BaseModel):
    """Compliance & security configuration"""
    allow_domains: List[str] = Field(default=["localhost", "127.0.0.1"])
    obey_robots: bool = True
    legal_basis: Optional[str] = "contractual"  # contractual, consent, legit_interest


class ArtifactConfig(BaseModel):
    """Artifact attachment configuration"""
    attach_html: bool = True
    attach_har: bool = False
    attach_pdf: bool = False
    attach_screenshot: bool = True


class DownloadConfig(BaseModel):
    """File download specification"""
    type: str  # pdf, png, jpeg, html, txt
    selector: Optional[str] = None
    label: str = Field(default="download")


class PlaybookRequest(BaseModel):
    """Complete playbook execution request"""
    request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: List[PlaybookStep]
    user_agent: str = "desktop"  # desktop, mobile, or custom UA string
    headless: bool = True
    viewport: ViewportConfig = Field(default_factory=ViewportConfig)
    download: Optional[List[DownloadConfig]] = None
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    archiv: ArtifactConfig = Field(default_factory=ArtifactConfig)
    strict: bool = True


class ArtifactRef(BaseModel):
    """Reference to an archived artifact"""
    label: str
    path: str
    sha256: Optional[str] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None


class ArtifactCollection(BaseModel):
    """Collection of artifacts from a run"""
    screenshots: List[ArtifactRef] = Field(default_factory=list)
    html: List[ArtifactRef] = Field(default_factory=list)
    pdf: List[ArtifactRef] = Field(default_factory=list)
    har: List[ArtifactRef] = Field(default_factory=list)
    extractions: Dict[str, Any] = Field(default_factory=dict)


class TimingInfo(BaseModel):
    """Execution timing information"""
    total_ms: int
    per_step_ms: Dict[str, int] = Field(default_factory=dict)


class ErrorInfo(BaseModel):
    """Error details in failure response"""
    code: str
    message: str
    step: Optional[int] = None
    selector: Optional[str] = None


class PlaybookResponse(BaseModel):
    """Response from playbook execution"""
    request_id: str
    status: str  # success, failed, canceled
    artifacts: ArtifactCollection = Field(default_factory=ArtifactCollection)
    extractions: Dict[str, Any] = Field(default_factory=dict)
    timings: TimingInfo
    error: Optional[ErrorInfo] = None
    strict: bool = True


class CancelRequest(BaseModel):
    """Request to cancel a running playbook"""
    request_id: str


class CancelResponse(BaseModel):
    """Response to cancel request"""
    request_id: str
    canceled: bool
    at_step: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    service: str
    status: str  # ok, degraded, error
    component: str
    port: int
    browser: Optional[str] = None
    ts: str


class ReadyResponse(BaseModel):
    """Readiness check response"""
    ready: bool
    browser: Optional[str] = None
    version: Optional[str] = None


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
    selector: Optional[str] = None
    elapsed_ms: int
    note: str
    error: Optional[str] = None
    strict: bool = True
