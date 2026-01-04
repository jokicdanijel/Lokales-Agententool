#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
Port: 12362
Kürzel: hpcreatep

Website-Generator für statische Sites, CMS-Integration und Deployment.
Unterstützt verschiedene Site-Generatoren (11ty, Hugo, Custom), Templates und Deployment-Targets.
"""

import json
import os
import shutil
import uuid
import zipfile
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

# ================== CONFIG ==================

PORT = 12366
SERVICE_NAME = "opena17"
KUERZEL = "hpcreatep"
VERSION = "1.0"

DATA_DIR = Path(__file__).parent / "data"
SITES_DIR = DATA_DIR / "sites"
TEMPLATES_DIR = DATA_DIR / "templates"
OUTPUT_DIR = DATA_DIR / "output"
PREVIEW_DIR = DATA_DIR / "preview"
HISTORY_FILE = DATA_DIR / "homepage_history.jsonl"

# Erstelle Verzeichnisse
for directory in [DATA_DIR, SITES_DIR, TEMPLATES_DIR, OUTPUT_DIR, PREVIEW_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Bearer Token aus ENV
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")

# Start-Zeit für Uptime
START_TIME = datetime.now(UTC)


# ================== ENUMS ==================


class SiteGeneratorType(str, Enum):
    STATIC = "static"  # Einfaches HTML/CSS/JS
    SSG_11TY = "11ty"  # Eleventy (JavaScript)
    SSG_HUGO = "hugo"  # Hugo (Go)
    CUSTOM = "custom"  # Benutzerdefiniert


class DeploymentTarget(str, Enum):
    LOCAL = "local"  # Lokales Filesystem
    FTP = "ftp"  # FTP-Server
    S3 = "s3"  # AWS S3
    NETLIFY = "netlify"  # Netlify
    VERCEL = "vercel"  # Vercel


class ExportFormat(str, Enum):
    ZIP = "zip"  # ZIP-Archiv
    TAR_GZ = "tar.gz"  # TAR.GZ-Archiv


class NavigationType(str, Enum):
    TOP = "top"  # Top-Navigation
    SIDE = "side"  # Seitennavigation
    FOOTER = "footer"  # Footer-Navigation


# ================== DATA MODELS ==================


class PageDefinition(BaseModel):
    """Einzelne Seite der Website"""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="")
    meta_description: str | None = Field(default=None, max_length=500)
    meta_keywords: list[str] | None = Field(default_factory=list)
    is_homepage: bool = Field(default=False)


class NavigationItem(BaseModel):
    """Navigation-Element"""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=100)
    children: list["NavigationItem"] | None = Field(default_factory=list)


class SiteBranding(BaseModel):
    """Branding-Informationen"""

    model_config = ConfigDict(extra="forbid")

    site_name: str = Field(..., min_length=1, max_length=100)
    tagline: str | None = Field(default=None, max_length=200)
    logo_url: str | None = Field(default=None)
    favicon_url: str | None = Field(default=None)
    color_primary: str = Field(default="#007bff")
    color_secondary: str = Field(default="#6c757d")


class SiteGenerateRequest(BaseModel):
    """Request: Website generieren"""

    model_config = ConfigDict(extra="forbid")

    generator: SiteGeneratorType = Field(default=SiteGeneratorType.STATIC)
    template: str = Field(default="default")
    pages: list[PageDefinition] = Field(..., min_items=1)
    navigation: list[NavigationItem] = Field(default_factory=list)
    navigation_type: NavigationType = Field(default=NavigationType.TOP)
    branding: SiteBranding
    custom_css: str | None = Field(default=None)
    custom_js: str | None = Field(default=None)


class SiteExportRequest(BaseModel):
    """Request: Website exportieren"""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(..., min_length=1)
    format: ExportFormat = Field(default=ExportFormat.ZIP)
    include_assets: bool = Field(default=True)


class SiteDeployRequest(BaseModel):
    """Request: Website deployen"""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(..., min_length=1)
    target: DeploymentTarget = Field(default=DeploymentTarget.LOCAL)
    target_path: str | None = Field(default=None)
    credentials: dict[str, str] | None = Field(default=None)
    invalidate_cache: bool = Field(default=False)


class SitePreviewRequest(BaseModel):
    """Request: Preview starten"""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(..., min_length=1)
    port: int = Field(default=8000, ge=8000, le=9000)


class CommandRequest(BaseModel):
    """Option-2-Flow Command"""

    model_config = ConfigDict(extra="forbid")

    action: str = Field(..., min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)


# ================== RESPONSE MODELS ==================


class SiteGenerateResponse(BaseModel):
    """Response: Website generiert"""

    model_config = ConfigDict(extra="forbid")

    site_id: str
    generator: str
    pages_generated: int
    output_path: str
    preview_url: str | None = None
    timestamp: str


class SiteExportResponse(BaseModel):
    """Response: Website exportiert"""

    model_config = ConfigDict(extra="forbid")

    site_id: str
    format: str
    file_path: str
    file_size_bytes: int
    timestamp: str


class SiteDeployResponse(BaseModel):
    """Response: Website deployed"""

    model_config = ConfigDict(extra="forbid")

    site_id: str
    target: str
    deployment_url: str | None = None
    status: str
    timestamp: str


class SiteStructure(BaseModel):
    """Response: Site-Struktur"""

    model_config = ConfigDict(extra="forbid")

    site_id: str
    pages: list[dict[str, Any]]
    routes: list[str]
    assets: list[str]
    total_size_bytes: int


# ================== SECURITY ==================


async def verify_bearer_token(authorization: str | None = Header(None)) -> str:
    """Bearer Token validieren"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return token


# ================== DATA PERSISTENCE ==================


class DataStore:
    """Persistenz-Layer für Sites und Metadata"""

    @staticmethod
    def save_site_metadata(site_id: str, metadata: dict[str, Any]) -> None:
        """Speichere Site-Metadata"""
        metadata_file = SITES_DIR / f"{site_id}.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_site_metadata(site_id: str) -> dict[str, Any]:
        """Lade Site-Metadata"""
        metadata_file = SITES_DIR / f"{site_id}.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail=f"Site not found: {site_id}")

        with open(metadata_file, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def log_history(event_type: str, data: dict[str, Any]) -> None:
        """Append-only History Log"""
        entry = {"timestamp": datetime.now(UTC).isoformat(), "event": event_type, "data": data}
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ================== SITE GENERATOR ==================


class SiteGenerator:
    """Website-Generator (Haupt-Business-Logik)"""

    @staticmethod
    def generate_site(req: SiteGenerateRequest) -> SiteGenerateResponse:
        """Generiere Website aus Request"""
        site_id = str(uuid.uuid4())[:12]
        site_dir = OUTPUT_DIR / site_id
        site_dir.mkdir(parents=True, exist_ok=True)

        # Homepage identifizieren
        homepage = next((p for p in req.pages if p.is_homepage), req.pages[0])

        # HTML-Seiten generieren
        for page in req.pages:
            html_content = SiteGenerator._generate_page_html(
                page=page,
                branding=req.branding,
                navigation=req.navigation,
                navigation_type=req.navigation_type,
                custom_css=req.custom_css,
                custom_js=req.custom_js,
            )

            # Dateiname bestimmen
            if page.is_homepage:
                filename = "index.html"
            else:
                filename = f"{page.slug}.html"

            page_file = site_dir / filename
            with open(page_file, "w", encoding="utf-8") as f:
                f.write(html_content)

        # Metadata speichern
        metadata = {
            "site_id": site_id,
            "generator": req.generator.value,
            "template": req.template,
            "pages": [p.model_dump() for p in req.pages],
            "branding": req.branding.model_dump(),
            "created_at": datetime.now(UTC).isoformat(),
            "output_path": str(site_dir),
        }
        DataStore.save_site_metadata(site_id, metadata)

        # History Log
        DataStore.log_history(
            "generate_site", {"site_id": site_id, "pages_count": len(req.pages), "generator": req.generator.value}
        )

        return SiteGenerateResponse(
            site_id=site_id,
            generator=req.generator.value,
            pages_generated=len(req.pages),
            output_path=str(site_dir),
            preview_url=f"http://127.0.0.1:12362/preview/{site_id}/index.html",
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def _generate_page_html(
        page: PageDefinition,
        branding: SiteBranding,
        navigation: list[NavigationItem],
        navigation_type: NavigationType,
        custom_css: str | None,
        custom_js: str | None,
    ) -> str:
        """Generiere HTML für eine einzelne Seite"""

        # Navigation HTML
        nav_html = SiteGenerator._build_navigation_html(navigation, navigation_type)

        # Custom CSS/JS
        css_block = f"<style>{custom_css}</style>" if custom_css else ""
        js_block = f"<script>{custom_js}</script>" if custom_js else ""

        # Meta-Tags
        meta_description = page.meta_description or branding.tagline or ""
        meta_keywords = ", ".join(page.meta_keywords) if page.meta_keywords else ""

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title} - {branding.site_name}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{meta_keywords}">
    {f'<link rel="icon" href="{branding.favicon_url}">' if branding.favicon_url else ""}
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }}
        header {{ background: {branding.color_primary}; color: white; padding: 1rem 2rem; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }}
        .logo {{ font-size: 1.5rem; font-weight: bold; }}
        nav ul {{ list-style: none; display: flex; gap: 1.5rem; }}
        nav a {{ color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; transition: background 0.3s; }}
        nav a:hover {{ background: rgba(255,255,255,0.2); }}
        main {{ max-width: 1200px; margin: 2rem auto; padding: 0 2rem; min-height: 60vh; }}
        h1 {{ color: {branding.color_primary}; margin-bottom: 1rem; }}
        footer {{ background: #f8f9fa; padding: 2rem; text-align: center; margin-top: 3rem; border-top: 1px solid #dee2e6; }}
        .tagline {{ color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-top: 0.25rem; }}
    </style>
    {css_block}
</head>
<body>
    <header>
        <div class="header-content">
            <div>
                <div class="logo">{branding.site_name}</div>
                {f'<div class="tagline">{branding.tagline}</div>' if branding.tagline else ''}
            </div>
            {nav_html}
        </div>
    </header>

    <main>
        <h1>{page.title}</h1>
        <div class="content">
            {page.content}
        </div>
    </main>

    <footer>
        <p>&copy; {datetime.now().year} {branding.site_name}. Alle Rechte vorbehalten.</p>
    </footer>

    {js_block}
</body>
</html>"""
        return html

    @staticmethod
    def _build_navigation_html(navigation: list[NavigationItem], nav_type: NavigationType) -> str:
        """Baue Navigation HTML"""
        if not navigation:
            return ""

        nav_items = []
        for item in navigation:
            nav_items.append(f'<li><a href="{item.slug}.html">{item.label}</a></li>')

        return f"""<nav>
            <ul>
                {''.join(nav_items)}
            </ul>
        </nav>"""

    @staticmethod
    def export_site(req: SiteExportRequest) -> SiteExportResponse:
        """Exportiere Site als ZIP/TAR.GZ"""
        metadata = DataStore.load_site_metadata(req.site_id)
        site_dir = Path(metadata["output_path"])

        if not site_dir.exists():
            raise HTTPException(status_code=404, detail=f"Site directory not found: {site_dir}")

        # Export-Datei erstellen
        export_filename = f"{req.site_id}.{req.format.value}"
        export_path = OUTPUT_DIR / export_filename

        if req.format == ExportFormat.ZIP:
            with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in site_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(site_dir)
                        zipf.write(file_path, arcname)
        else:
            # TAR.GZ (via shutil)
            import tarfile

            with tarfile.open(export_path, "w:gz") as tar:
                tar.add(site_dir, arcname=req.site_id)

        file_size = export_path.stat().st_size

        # History Log
        DataStore.log_history(
            "export_site", {"site_id": req.site_id, "format": req.format.value, "file_size": file_size}
        )

        return SiteExportResponse(
            site_id=req.site_id,
            format=req.format.value,
            file_path=str(export_path),
            file_size_bytes=file_size,
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def deploy_site(req: SiteDeployRequest) -> SiteDeployResponse:
        """Deploy Site zu Target"""
        metadata = DataStore.load_site_metadata(req.site_id)
        site_dir = Path(metadata["output_path"])

        if not site_dir.exists():
            raise HTTPException(status_code=404, detail=f"Site directory not found: {site_dir}")

        deployment_url = None

        if req.target == DeploymentTarget.LOCAL:
            # Lokales Deployment (Kopieren)
            target_path = Path(req.target_path or "/tmp/sites") / req.site_id
            target_path.mkdir(parents=True, exist_ok=True)
            shutil.copytree(site_dir, target_path, dirs_exist_ok=True)
            deployment_url = f"file://{target_path}/index.html"

        elif req.target == DeploymentTarget.FTP:
            # FTP-Deployment (Mock - würde ftplib verwenden)
            deployment_url = f"ftp://{req.target_path or 'example.com'}/{req.site_id}"

        elif req.target == DeploymentTarget.S3:
            # S3-Deployment (Mock - würde boto3 verwenden)
            deployment_url = f"https://{req.site_id}.s3.amazonaws.com/index.html"

        elif req.target in [DeploymentTarget.NETLIFY, DeploymentTarget.VERCEL]:
            # Netlify/Vercel (Mock - würde API-Calls machen)
            deployment_url = f"https://{req.site_id}.{req.target.value}.app"

        # History Log (mit Secret-Masking)
        DataStore.log_history(
            "deploy_site",
            {
                "site_id": req.site_id,
                "target": req.target.value,
                "credentials_provided": bool(req.credentials),
                "deployment_url": deployment_url,
            },
        )

        return SiteDeployResponse(
            site_id=req.site_id,
            target=req.target.value,
            deployment_url=deployment_url,
            status="deployed",
            timestamp=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def get_site_structure(site_id: str) -> SiteStructure:
        """Hole Site-Struktur"""
        metadata = DataStore.load_site_metadata(site_id)
        site_dir = Path(metadata["output_path"])

        if not site_dir.exists():
            raise HTTPException(status_code=404, detail=f"Site directory not found: {site_dir}")

        pages = []
        routes = []
        assets = []
        total_size = 0

        for file_path in site_dir.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size

                relative_path = file_path.relative_to(site_dir)

                if file_path.suffix == ".html":
                    pages.append({"path": str(relative_path), "size": file_size})
                    routes.append("/" + str(relative_path))
                else:
                    assets.append(str(relative_path))

        return SiteStructure(site_id=site_id, pages=pages, routes=routes, assets=assets, total_size_bytes=total_size)


# ================== FASTAPI APP ==================

app = FastAPI(title=f"{SERVICE_NAME} - Homepage Creator Agent", version=VERSION, docs_url="/docs", redoc_url="/redoc")


@app.get("/")
async def root():
    """Root Endpoint"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": PORT,
        "status": "running",
        "endpoints": [
            "/health",
            "/site/generate",
            "/site/export",
            "/site/deploy",
            "/site/structure/{site_id}",
            "/command",
        ],
    }


@app.get("/health")
async def health():
    """Health Check (ohne Auth)"""
    uptime = (datetime.now(UTC) - START_TIME).total_seconds()

    # Zähle Sites
    total_sites = len(list(SITES_DIR.glob("*.json")))

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "port": PORT,
        "uptime_seconds": round(uptime, 2),
        "total_sites": total_sites,
    }


@app.post("/site/generate", response_model=SiteGenerateResponse)
async def generate_site(req: SiteGenerateRequest, token: str = Depends(verify_bearer_token)):
    """Generiere Website"""
    try:
        response = SiteGenerator.generate_site(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Site generation failed: {e!s}")


@app.post("/site/export", response_model=SiteExportResponse)
async def export_site(req: SiteExportRequest, token: str = Depends(verify_bearer_token)):
    """Exportiere Website als ZIP/TAR.GZ"""
    try:
        response = SiteGenerator.export_site(req)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e!s}")


@app.post("/site/deploy", response_model=SiteDeployResponse)
async def deploy_site(req: SiteDeployRequest, token: str = Depends(verify_bearer_token)):
    """Deploy Website zu Target"""
    try:
        response = SiteGenerator.deploy_site(req)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {e!s}")


@app.get("/site/structure/{site_id}", response_model=SiteStructure)
async def get_site_structure(site_id: str, token: str = Depends(verify_bearer_token)):
    """Hole Site-Struktur"""
    try:
        return SiteGenerator.get_site_structure(site_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get structure: {e!s}")


@app.get("/preview/{site_id}/{file_path:path}")
async def preview_file(site_id: str, file_path: str):
    """Preview: Statische Datei ausliefern (ohne Auth für Browser-Zugriff)"""
    try:
        metadata = DataStore.load_site_metadata(site_id)
        site_dir = Path(metadata["output_path"])
        file_full_path = site_dir / file_path

        if not file_full_path.exists() or not file_full_path.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Sicherheit: Path-Traversal verhindern
        if not file_full_path.resolve().is_relative_to(site_dir.resolve()):
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(file_full_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {e!s}")


@app.post("/command")
async def command(req: CommandRequest, token: str = Depends(verify_bearer_token)):
    """Option-2-Flow: Universeller Command-Endpoint"""
    action = req.action
    params = req.params

    try:
        if action == "generate_site":
            # Parse params in SiteGenerateRequest
            generate_req = SiteGenerateRequest(**params)
            response = SiteGenerator.generate_site(generate_req)
            return {"status": "success", "action": action, "result": response.model_dump()}

        elif action == "export_site":
            export_req = SiteExportRequest(**params)
            response = SiteGenerator.export_site(export_req)
            return {"status": "success", "action": action, "result": response.model_dump()}

        elif action == "deploy_site":
            deploy_req = SiteDeployRequest(**params)
            response = SiteGenerator.deploy_site(deploy_req)
            return {"status": "success", "action": action, "result": response.model_dump()}

        elif action == "get_structure":
            site_id = params.get("site_id")
            if not site_id:
                raise HTTPException(status_code=422, detail="site_id required")
            response = SiteGenerator.get_site_structure(site_id)
            return {"status": "success", "action": action, "result": response.model_dump()}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e!s}")


# ================== MAIN ==================

if __name__ == "__main__":
    print(f"[INFO] Starting {SERVICE_NAME} ({KUERZEL}) on port {PORT}...")
    print(f"[INFO] Data Directory: {DATA_DIR}")
    print(f"[INFO] Sites Directory: {SITES_DIR}")
    print(f"[INFO] Output Directory: {OUTPUT_DIR}")

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
