#!/usr/bin/env python3
"""
opena15 - HTML Creator Agent
Port: 12360
Kürzel: htmlp

Features:
- HTML-Generierung mit Jinja2-Templates
- HTML-Validierung (BeautifulSoup4)
- Template-Management (Liste, Auswahl, Custom)
- SEO-Optimization (Meta-Tags, Keywords)
- CSS-Framework-Integration (Bootstrap, Tailwind, Custom)
- Export-Funktionen (Datei, Base64, ZIP)
- Preview-Rendering
"""

import base64
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================

PORT = int(os.getenv("PORT", 12360))
SERVICE_NAME = "opena15"
KUERZEL = "htmlp"
VERSION = "1.0"

# ENV-Token (falls vorhanden)
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

# Pfade
BASE_DIR = Path(__file__).parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # 14.opena15_html/
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = DATA_DIR / "templates"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
HISTORY_FILE = DATA_DIR / "html_history.jsonl"

# Directories erstellen
DATA_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Jinja2 Environment
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

# App-Start-Zeit
START_TIME = time.time()

# ============================================================================
# ENUMS
# ============================================================================


class CSSFramework(str, Enum):
    """CSS Framework Options"""

    NONE = "none"
    BOOTSTRAP = "bootstrap"
    TAILWIND = "tailwind"
    BULMA = "bulma"
    CUSTOM = "custom"


class ValidationLevel(str, Enum):
    """HTML Validation Strictness"""

    LOOSE = "loose"
    STANDARD = "standard"
    STRICT = "strict"


# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================


class GenerateRequest(BaseModel):
    """HTML generieren"""

    template_name: str = Field(..., min_length=1, max_length=200)
    variables: dict[str, Any] = Field(default_factory=dict)
    css_framework: CSSFramework = CSSFramework.NONE
    custom_css: str | None = None
    title: str = Field(default="Generated Page", max_length=200)
    description: str | None = Field(None, max_length=500)
    keywords: list[str] | None = Field(None, max_items=20)

    class Config:
        extra = "forbid"


class PreviewRequest(BaseModel):
    """HTML Preview"""

    html: str = Field(..., min_length=1, max_length=1_000_000)
    width: int = Field(default=1920, ge=320, le=3840)
    height: int = Field(default=1080, ge=240, le=2160)

    class Config:
        extra = "forbid"


class ValidateRequest(BaseModel):
    """HTML validieren"""

    html: str = Field(..., min_length=1, max_length=1_000_000)
    validation_level: ValidationLevel = ValidationLevel.STANDARD

    class Config:
        extra = "forbid"


class ValidateResponse(BaseModel):
    """Validation Result"""

    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    info: dict[str, Any] = Field(default_factory=dict)


class ExportRequest(BaseModel):
    """Export HTML"""

    html: str = Field(..., min_length=1, max_length=1_000_000)
    filename: str = Field(..., min_length=1, max_length=200)
    format: str = Field(default="html", pattern="^(html|zip|base64)$")

    class Config:
        extra = "forbid"

    @field_validator("filename")
    @classmethod
    def sanitize_filename(cls, v: str) -> str:
        # Sanitize filename
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
        sanitized = "".join(c for c in v if c in allowed_chars)
        if not sanitized:
            raise ValueError("Invalid filename")
        return sanitized


class TemplateListResponse(BaseModel):
    """Templates auflisten"""

    templates: list[str]
    total: int


class GenerateResponse(BaseModel):
    """HTML Generation Result"""

    success: bool
    html: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    message: str


class ExportResponse(BaseModel):
    """Export Result"""

    success: bool
    file_path: str | None = None
    base64_data: str | None = None
    message: str


class CommandRequest(BaseModel):
    """Option-2-Flow Command Endpoint"""

    action: str = Field(..., min_length=1, max_length=100)
    params: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


# ============================================================================
# DATACLASSES (Persistence)
# ============================================================================


@dataclass
class HTMLGenerationRecord:
    """HTML Generation History Entry"""

    record_id: str
    timestamp: str
    template_name: str
    variables: dict[str, Any]
    css_framework: str
    title: str
    file_path: str
    file_size: int
    success: bool


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="opena15 - HTML Creator Agent",
    version=VERSION,
    description="HTML-Generierung, Template-Management, Validierung (htmlp)",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTH DEPENDENCY
# ============================================================================


def verify_token(authorization: str | None = Header(None)) -> bool:
    """Bearer Token Verification"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = authorization.replace("Bearer ", "")
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return True


# ============================================================================
# HTML UTILITIES
# ============================================================================


class HTMLProcessor:
    """HTML Processing Utilities"""

    @staticmethod
    def validate_html(html: str, level: ValidationLevel) -> ValidateResponse:
        """Validate HTML structure"""
        errors = []
        warnings = []
        info = {}

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Basic structure checks
            if not soup.find("html"):
                errors.append("Missing <html> tag")
            if not soup.find("head"):
                errors.append("Missing <head> tag")
            if not soup.find("body"):
                errors.append("Missing <body> tag")

            # Title check
            title_tag = soup.find("title")
            if not title_tag:
                warnings.append("Missing <title> tag")
            elif not title_tag.get_text(strip=True):
                warnings.append("Empty <title> tag")

            # Meta charset
            charset_meta = soup.find("meta", charset=True)
            if not charset_meta:
                warnings.append("Missing charset meta tag")

            # Strict mode checks
            if level == ValidationLevel.STRICT:
                # Viewport meta
                viewport_meta = soup.find("meta", attrs={"name": "viewport"})
                if not viewport_meta:
                    warnings.append("Missing viewport meta tag (recommended for responsive design)")

                # Alt attributes on images
                images = soup.find_all("img")
                for img in images:
                    if not img.get("alt"):
                        warnings.append(f"Image missing alt attribute: {img.get('src', 'unknown')}")

            # Info
            info["tag_count"] = len(soup.find_all())
            info["text_length"] = len(soup.get_text(strip=True))
            info["has_doctype"] = html.strip().lower().startswith("<!doctype")

            valid = len(errors) == 0

        except Exception as e:
            errors.append(f"Parse error: {e!s}")
            valid = False

        return ValidateResponse(valid=valid, errors=errors, warnings=warnings, info=info)

    @staticmethod
    def inject_css_framework(html: str, framework: CSSFramework, custom_css: str | None = None) -> str:
        """Inject CSS framework links into HTML"""
        soup = BeautifulSoup(html, "html.parser")
        head = soup.find("head")

        if not head:
            return html

        # Framework CDN links
        framework_links = {
            CSSFramework.BOOTSTRAP: '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">',
            CSSFramework.TAILWIND: '<script src="https://cdn.tailwindcss.com"></script>',
            CSSFramework.BULMA: '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">',
        }

        if framework in framework_links:
            link_tag = BeautifulSoup(framework_links[framework], "html.parser")
            head.append(link_tag)

        # Custom CSS
        if custom_css:
            style_tag = soup.new_tag("style")
            style_tag.string = custom_css
            head.append(style_tag)

        return str(soup)

    @staticmethod
    def inject_meta_tags(html: str, title: str, description: str | None, keywords: list[str] | None) -> str:
        """Inject SEO meta tags"""
        soup = BeautifulSoup(html, "html.parser")
        head = soup.find("head")

        if not head:
            return html

        # Title
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = title
        else:
            new_title = soup.new_tag("title")
            new_title.string = title
            head.insert(0, new_title)

        # Description
        if description:
            desc_meta = soup.find("meta", attrs={"name": "description"})
            if desc_meta:
                desc_meta["content"] = description
            else:
                new_desc = soup.new_tag("meta", attrs={"name": "description", "content": description})
                head.append(new_desc)

        # Keywords
        if keywords:
            keywords_str = ", ".join(keywords)
            kw_meta = soup.find("meta", attrs={"name": "keywords"})
            if kw_meta:
                kw_meta["content"] = keywords_str
            else:
                new_kw = soup.new_tag("meta", attrs={"name": "keywords", "content": keywords_str})
                head.append(new_kw)

        return str(soup)


class TemplateManager:
    """Template Management"""

    @staticmethod
    def list_templates() -> list[str]:
        """List available templates"""
        if not TEMPLATES_DIR.exists():
            return []

        templates = []
        # Jinja2 templates (.j2)
        for file in TEMPLATES_DIR.glob("*.j2"):
            templates.append(file.name)
        # HTML templates
        for file in TEMPLATES_DIR.glob("*.html"):
            templates.append(file.name)
        return sorted(templates)

    @staticmethod
    def render_template(template_name: str, variables: dict[str, Any]) -> str:
        """Render Jinja2 template"""
        try:
            template = jinja_env.get_template(template_name)
            html = template.render(**variables)
            return html
        except TemplateNotFound:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
        except TemplateSyntaxError as e:
            raise HTTPException(status_code=400, detail=f"Template syntax error: {str(e)}")


class DataStore:
    """Persistence Layer"""

    @staticmethod
    def save_html(html: str, filename: str) -> Path:
        """Save HTML to file"""
        file_path = OUTPUT_DIR / filename
        file_path.write_text(html, encoding="utf-8")
        return file_path

    @staticmethod
    def append_history(record: HTMLGenerationRecord):
        """Append to JSONL history"""
        with HISTORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


# ============================================================================
# ROUTES
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": PORT,
        "description": "HTML Creator Agent - Template Rendering, Validation, Export (htmlp)",
    }


@app.get("/health")
async def health():
    """Health check (no auth)"""
    uptime = round(time.time() - START_TIME, 2)

    templates = TemplateManager.list_templates()

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": uptime,
        "templates_available": len(templates),
        "jinja2_support": True,
    }


@app.get("/templates/list", response_model=TemplateListResponse)
async def list_templates(_: bool = Depends(verify_token)):
    """List available templates"""
    templates = TemplateManager.list_templates()

    return TemplateListResponse(templates=templates, total=len(templates))


@app.get("/templates")
async def get_templates(_: bool = Depends(verify_token)):
    """Get templates with metadata (extended version)"""
    if not TEMPLATES_DIR.exists():
        return {"templates": [], "total": 0}

    templates = []
    for file in TEMPLATES_DIR.glob("*.j2"):
        stat = file.stat()
        templates.append(
            {
                "name": file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
            }
        )

    # Auch .html Templates
    for file in TEMPLATES_DIR.glob("*.html"):
        stat = file.stat()
        templates.append(
            {
                "name": file.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
            }
        )

    return {"templates": sorted(templates, key=lambda x: x["name"]), "total": len(templates)}


@app.post("/generate", response_model=GenerateResponse)
async def generate_html(req: GenerateRequest, _: bool = Depends(verify_token)):
    """Generate HTML from template"""
    try:
        # Render template
        html = TemplateManager.render_template(req.template_name, req.variables)

        # Inject meta tags
        html = HTMLProcessor.inject_meta_tags(html, req.title, req.description, req.keywords)

        # Inject CSS framework
        html = HTMLProcessor.inject_css_framework(html, req.css_framework, req.custom_css)

        # Validate
        validation = HTMLProcessor.validate_html(html, ValidationLevel.STANDARD)
        if not validation.valid:
            raise HTTPException(status_code=422, detail=f"Generated HTML invalid: {validation.errors}")

        # Save
        filename = f"{uuid.uuid4().hex[:8]}_{req.template_name}"
        file_path = DataStore.save_html(html, filename)
        file_size = file_path.stat().st_size

        # History
        record = HTMLGenerationRecord(
            record_id=uuid.uuid4().hex,
            timestamp=datetime.now(UTC).isoformat(),
            template_name=req.template_name,
            variables=req.variables,
            css_framework=req.css_framework.value,
            title=req.title,
            file_path=str(file_path),
            file_size=file_size,
            success=True,
        )
        DataStore.append_history(record)

        return GenerateResponse(
            success=True,
            html=html,
            file_path=str(file_path),
            file_size=file_size,
            message="HTML generated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        return GenerateResponse(success=False, message=f"Generation failed: {e!s}")


@app.post("/preview", response_class=HTMLResponse)
async def preview_html(req: PreviewRequest, _: bool = Depends(verify_token)):
    """Preview HTML (returns rendered HTML)"""
    # Add viewport meta for preview
    soup = BeautifulSoup(req.html, "html.parser")
    head = soup.find("head")

    if head:
        viewport_meta = soup.new_tag(
            "meta", attrs={"name": "viewport", "content": f"width={req.width}, initial-scale=1.0"}
        )
        head.insert(0, viewport_meta)

    return HTMLResponse(content=str(soup))


@app.post("/validate", response_model=ValidateResponse)
async def validate_html(req: ValidateRequest, _: bool = Depends(verify_token)):
    """Validate HTML structure"""
    return HTMLProcessor.validate_html(req.html, req.validation_level)


@app.post("/export", response_model=ExportResponse)
async def export_html(req: ExportRequest, _: bool = Depends(verify_token)):
    """Export HTML (file, zip, base64)"""
    try:
        if req.format == "html":
            # Save as file
            file_path = DataStore.save_html(req.html, req.filename)

            return ExportResponse(success=True, file_path=str(file_path), message=f"HTML exported to {file_path}")

        elif req.format == "base64":
            # Base64 encode
            b64_data = base64.b64encode(req.html.encode("utf-8")).decode("ascii")

            return ExportResponse(success=True, base64_data=b64_data, message="HTML encoded to Base64")

        elif req.format == "zip":
            # Create ZIP (HTML + assets placeholder)
            import zipfile

            zip_filename = req.filename.replace(".html", ".zip")
            zip_path = OUTPUT_DIR / zip_filename

            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr(req.filename, req.html)

            return ExportResponse(success=True, file_path=str(zip_path), message=f"HTML exported to ZIP: {zip_path}")

        else:
            raise HTTPException(status_code=400, detail="Invalid format")

    except Exception as e:
        return ExportResponse(success=False, message=f"Export failed: {e!s}")


@app.post("/command")
async def command_endpoint(req: CommandRequest, _: bool = Depends(verify_token)):
    """Option-2-Flow command endpoint"""
    action = req.action
    params = req.params

    if action == "generate_html":
        # Delegate to /generate
        gen_req = GenerateRequest(**params)
        result = await generate_html(gen_req, True)

        return {
            "action": action,
            "success": result.success,
            "result": result.model_dump(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    elif action == "validate_html":
        # Delegate to /validate
        val_req = ValidateRequest(**params)
        result = await validate_html(val_req, True)

        return {
            "action": action,
            "success": result.valid,
            "result": result.model_dump(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    elif action == "list_templates":
        # Delegate to /templates/list
        result = await list_templates(True)

        return {
            "action": action,
            "success": True,
            "result": result.model_dump(),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


# ============================================================================
# STARTUP
# ============================================================================


def create_default_template():
    """Create default template if none exist"""
    default_template = TEMPLATES_DIR / "default.html"

    if not default_template.exists():
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title | default('Generated Page') }}</title>
</head>
<body>
    <h1>{{ heading | default('Welcome') }}</h1>
    <p>{{ content | default('This is a default template.') }}</p>
</body>
</html>"""

        default_template.write_text(html_content, encoding="utf-8")
        print(f"[INFO] ✅ Default template created: {default_template}")


if __name__ == "__main__":
    import uvicorn

    # Create default template
    create_default_template()

    print(f"[INFO] Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
