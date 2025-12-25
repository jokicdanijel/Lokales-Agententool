"""
opena14_HTML: HTML Generator Agent
Template rendering, page generation, CSS styling, HTML export
"""

import json
import logging
import os
import secrets
import sys
import urllib.request
from datetime import datetime
from html import escape
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(title="opena14_HTML", version="1.0.0", description="HTML Generator Agent - Template Rendering & Export")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = 12362
TOKEN = "MEIN_SUPER_TOKEN_123"
ARCHIVE_PORT = 12345

# In-memory storage
_templates: dict = {}
_generated_pages: dict = {}
_export_history: dict = {}

# ============================================================================
# DATA MODELS
# ============================================================================


class TemplateRenderRequest(BaseModel):
    template_name: str
    variables: dict[str, Any]


class PageGenerateRequest(BaseModel):
    title: str
    content: str
    sections: dict[str, str] | None = None
    template_type: str = "standard"


class StyleApplyRequest(BaseModel):
    page_id: str
    css: str
    theme: str | None = None


class ExportRequest(BaseModel):
    page_id: str
    format: str = "html"  # html, minified_html


class PreviewRequest(BaseModel):
    page_id: str
    include_css: bool = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _validate_token(auth_header: str | None):
    """Validate Bearer token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.replace("Bearer ", "").strip()
    if token != TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


async def _archive(payload: dict):
    """Archive operation to opena2"""
    try:
        data = {
            "src": "opena14_html_generator",
            "dst": "opena2",
            "kind": "HTML_OP",
            "payload": {**payload, "ts": datetime.utcnow().isoformat() + "Z"},
        }

        req = urllib.request.Request(
            f"http://127.0.0.1:{ARCHIVE_PORT}/store/archivp",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.warning(f"⚠️ Archive failed: {e}")
        return {"written": False}


def _generate_page_id() -> str:
    """Generate unique page ID"""
    return f"PG_{secrets.token_hex(8).upper()}"


def _render_variable(template: str, variables: dict[str, Any]) -> str:
    """Simple variable rendering ({{var}} -> value)"""
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(escape(str(value))))
    return result


def _get_template(name: str) -> str:
    """Get template by name"""
    templates = {
        "landing": """
<!DOCTYPE html>
<html>
<head><title>{{title}}</title></head>
<body>
<h1>{{title}}</h1>
<p>{{description}}</p>
<footer>Generated on {{date}}</footer>
</body>
</html>
""",
        "blog": """
<!DOCTYPE html>
<html>
<head><title>{{title}}</title></head>
<body>
<article>
<h1>{{title}}</h1>
<div class="meta">By {{author}} on {{date}}</div>
<div class="content">{{content}}</div>
</article>
</body>
</html>
""",
        "profile": """
<!DOCTYPE html>
<html>
<head><title>{{name}}</title></head>
<body>
<div class="profile">
<h1>{{name}}</h1>
<p class="title">{{title}}</p>
<p>{{bio}}</p>
</div>
</body>
</html>
""",
    }
    return templates.get(name, templates["landing"])


def _minify_html(html: str) -> str:
    """Simple HTML minification"""
    import re

    # Remove comments
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    # Remove extra whitespace
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def _apply_css_to_html(html: str, css: str) -> str:
    """Apply CSS to HTML"""
    style_tag = f"<style>\n{css}\n</style>"
    # Insert style before closing head or at beginning
    if "</head>" in html:
        return html.replace("</head>", style_tag + "\n</head>")
    else:
        return style_tag + "\n" + html


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "opena14_HTML",
        "port": PORT,
        "templates": len(_templates),
        "pages": len(_generated_pages),
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/template/render")
async def render_template(req: TemplateRenderRequest, authorization: str = Header(None)):
    """Render template with variables"""
    _validate_token(authorization)

    try:
        template = _get_template(req.template_name)
        rendered = _render_variable(template, req.variables)

        page_id = _generate_page_id()
        _generated_pages[page_id] = {
            "template": req.template_name,
            "html": rendered,
            "variables": req.variables,
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"🎨 Template rendered: {req.template_name} (page: {page_id})")

        await _archive(
            {
                "op": "TEMPLATE_RENDER",
                "template": req.template_name,
                "page_id": page_id,
                "var_count": len(req.variables),
            }
        )

        return {
            "strict": True,
            "page_id": page_id,
            "html": rendered,
            "template": req.template_name,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Template rendering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/page/generate")
async def generate_page(req: PageGenerateRequest, authorization: str = Header(None)):
    """Generate custom HTML page"""
    _validate_token(authorization)

    try:
        page_id = _generate_page_id()

        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(req.title)}</title>
</head>
<body>
<header>
<h1>{escape(req.title)}</h1>
</header>
<main>
<div class="content">
{escape(req.content)}
</div>
"""

        # Add sections if provided
        if req.sections:
            for section_name, section_content in req.sections.items():
                html += f"""
<section class="{escape(section_name)}">
<h2>{escape(section_name.title())}</h2>
<p>{escape(section_content)}</p>
</section>
"""

        html += (
            """
</main>
<footer>
<p>Generated on """
            + datetime.utcnow().isoformat()
            + """</p>
</footer>
</body>
</html>
"""
        )

        _generated_pages[page_id] = {
            "title": req.title,
            "html": html,
            "sections": req.sections or {},
            "created_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"📄 Page generated: {page_id} ({req.title})")

        await _archive(
            {"op": "PAGE_GENERATE", "page_id": page_id, "title": req.title, "sections": len(req.sections or {})}
        )

        return {
            "strict": True,
            "page_id": page_id,
            "title": req.title,
            "sections": len(req.sections or {}),
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"❌ Page generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/style/apply")
async def apply_style(req: StyleApplyRequest, authorization: str = Header(None)):
    """Apply CSS styling to page"""
    _validate_token(authorization)

    try:
        if req.page_id not in _generated_pages:
            raise HTTPException(status_code=404, detail=f"Page {req.page_id} not found")

        page = _generated_pages[req.page_id]
        html_with_css = _apply_css_to_html(page["html"], req.css)

        page["html"] = html_with_css
        page["css"] = req.css
        page["theme"] = req.theme or "custom"
        page["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"🎨 Styles applied: {req.page_id} ({req.theme or 'custom'})")

        await _archive(
            {"op": "STYLE_APPLY", "page_id": req.page_id, "theme": req.theme or "custom", "css_length": len(req.css)}
        )

        return {
            "strict": True,
            "page_id": req.page_id,
            "theme": page["theme"],
            "css_applied": True,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Style application failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/html")
async def export_html(req: ExportRequest, authorization: str = Header(None)):
    """Export page to HTML file"""
    _validate_token(authorization)

    try:
        if req.page_id not in _generated_pages:
            raise HTTPException(status_code=404, detail=f"Page {req.page_id} not found")

        page = _generated_pages[req.page_id]
        html_content = page["html"]

        if req.format == "minified_html":
            html_content = _minify_html(html_content)

        export_file = f"/tmp/{req.page_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"

        # Simulate file write
        export_entry = {
            "page_id": req.page_id,
            "filename": export_file,
            "format": req.format,
            "size_bytes": len(html_content),
            "exported_at": datetime.utcnow().isoformat(),
        }

        _export_history[req.page_id] = export_entry
        logger.info(f"💾 HTML exported: {req.page_id} ({req.format}, {len(html_content)} bytes)")

        await _archive(
            {"op": "EXPORT_HTML", "page_id": req.page_id, "format": req.format, "size_bytes": len(html_content)}
        )

        return {
            "strict": True,
            "page_id": req.page_id,
            "export": export_entry,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HTML export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preview")
async def preview_page(req: PreviewRequest, authorization: str = Header(None)):
    """Get HTML page preview"""
    _validate_token(authorization)

    try:
        if req.page_id not in _generated_pages:
            raise HTTPException(status_code=404, detail=f"Page {req.page_id} not found")

        page = _generated_pages[req.page_id]

        preview_data = {
            "page_id": req.page_id,
            "title": page.get("title", "Untitled"),
            "html_length": len(page["html"]),
            "preview_html": page["html"][:500] + "..." if len(page["html"]) > 500 else page["html"],
        }

        logger.info(f"👁️ Preview generated: {req.page_id}")

        return {"strict": True, "preview": preview_data, "ts": datetime.utcnow().isoformat() + "Z"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Preview generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def status(authorization: str = Header(None)):
    """Get agent status"""
    _validate_token(authorization)

    return {
        "service": "opena14_HTML",
        "version": "1.0.0",
        "port": PORT,
        "pages_generated": len(_generated_pages),
        "exports": len(_export_history),
        "endpoints": 6,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting opena14_HTML on port {PORT}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
