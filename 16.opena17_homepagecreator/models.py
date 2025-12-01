#!/usr/bin/env python3
"""
opena17 - Homepage Creator Agent
Models Module - PORTIER 3.0 Compliant

Pydantic Models mit extra="forbid" (Strict JSON Schema)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# ================== ENUMS ==================

class SiteGeneratorType(str, Enum):
    """Website-Generator Typ"""
    STATIC = "static"      # Einfaches HTML/CSS/JS
    SSG_11TY = "11ty"      # Eleventy (JavaScript)
    SSG_HUGO = "hugo"      # Hugo (Go)
    SSG_NEXT = "next"      # Next.js (React)
    CUSTOM = "custom"      # Benutzerdefiniert


class DeploymentTarget(str, Enum):
    """Deployment-Ziel"""
    LOCAL = "local"        # Lokales Filesystem
    FTP = "ftp"            # FTP-Server
    S3 = "s3"              # AWS S3
    NETLIFY = "netlify"    # Netlify
    VERCEL = "vercel"      # Vercel
    GITHUB_PAGES = "github_pages"  # GitHub Pages


class ExportFormat(str, Enum):
    """Export-Format"""
    ZIP = "zip"            # ZIP-Archiv
    TAR_GZ = "tar.gz"      # TAR.GZ-Archiv


class NavigationType(str, Enum):
    """Navigations-Typ"""
    TOP = "top"            # Top-Navigation
    SIDE = "side"          # Seitennavigation
    FOOTER = "footer"      # Footer-Navigation
    MEGA = "mega"          # Mega-Menu


class PageType(str, Enum):
    """Seitentyp"""
    LANDING = "landing"
    ABOUT = "about"
    CONTACT = "contact"
    BLOG = "blog"
    PORTFOLIO = "portfolio"
    SERVICES = "services"
    PRICING = "pricing"
    FAQ = "faq"
    LEGAL = "legal"
    CUSTOM = "custom"


class ComponentType(str, Enum):
    """UI-Komponenten-Typ"""
    HEADER = "header"
    HERO = "hero"
    FEATURES = "features"
    GALLERY = "gallery"
    TESTIMONIALS = "testimonials"
    TEAM = "team"
    PRICING_TABLE = "pricing_table"
    CONTACT_FORM = "contact_form"
    CTA = "cta"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    NEWSLETTER = "newsletter"


# ================== REQUEST MODELS ==================

class PageDefinition(BaseModel):
    """Einzelne Seite der Website"""
    model_config = ConfigDict(extra="forbid")
    
    slug: str = Field(..., min_length=1, max_length=100, description="URL-Slug der Seite")
    title: str = Field(..., min_length=1, max_length=200, description="Seitentitel")
    content: str = Field(default="", description="HTML/Markdown Inhalt")
    page_type: PageType = Field(default=PageType.CUSTOM, description="Seitentyp")
    meta_description: Optional[str] = Field(default=None, max_length=500)
    meta_keywords: Optional[List[str]] = Field(default_factory=list)
    is_homepage: bool = Field(default=False)
    is_published: bool = Field(default=True)
    order: int = Field(default=0, ge=0, le=100)
    components: Optional[List[ComponentType]] = Field(default_factory=list)


class NavigationItem(BaseModel):
    """Navigation-Element"""
    model_config = ConfigDict(extra="forbid")
    
    label: str = Field(..., min_length=1, max_length=50, description="Anzeige-Label")
    slug: str = Field(..., min_length=1, max_length=100, description="Link-Ziel")
    icon: Optional[str] = Field(default=None, max_length=50)
    external: bool = Field(default=False)
    children: Optional[List['NavigationItem']] = Field(default_factory=list)


class SiteBranding(BaseModel):
    """Branding-Informationen"""
    model_config = ConfigDict(extra="forbid")
    
    site_name: str = Field(..., min_length=1, max_length=100, description="Website-Name")
    tagline: Optional[str] = Field(default=None, max_length=200)
    logo_url: Optional[str] = Field(default=None)
    favicon_url: Optional[str] = Field(default=None)
    color_primary: str = Field(default="#007bff", pattern=r"^#[0-9A-Fa-f]{6}$")
    color_secondary: str = Field(default="#6c757d", pattern=r"^#[0-9A-Fa-f]{6}$")
    color_accent: str = Field(default="#28a745", pattern=r"^#[0-9A-Fa-f]{6}$")
    color_background: str = Field(default="#ffffff", pattern=r"^#[0-9A-Fa-f]{6}$")
    color_text: str = Field(default="#333333", pattern=r"^#[0-9A-Fa-f]{6}$")
    font_primary: str = Field(default="Inter")
    font_heading: str = Field(default="Inter")


class SocialLinks(BaseModel):
    """Social Media Links"""
    model_config = ConfigDict(extra="forbid")
    
    facebook: Optional[str] = Field(default=None)
    twitter: Optional[str] = Field(default=None)
    instagram: Optional[str] = Field(default=None)
    linkedin: Optional[str] = Field(default=None)
    youtube: Optional[str] = Field(default=None)
    github: Optional[str] = Field(default=None)


class SiteGenerateRequest(BaseModel):
    """Request: Website generieren"""
    model_config = ConfigDict(extra="forbid")
    
    generator: SiteGeneratorType = Field(default=SiteGeneratorType.STATIC)
    template: str = Field(default="default", min_length=1, max_length=50)
    pages: List[PageDefinition] = Field(..., min_length=1, max_length=50)
    navigation: List[NavigationItem] = Field(default_factory=list)
    navigation_type: NavigationType = Field(default=NavigationType.TOP)
    branding: SiteBranding
    social_links: Optional[SocialLinks] = Field(default=None)
    custom_css: Optional[str] = Field(default=None, max_length=50000)
    custom_js: Optional[str] = Field(default=None, max_length=50000)
    custom_head: Optional[str] = Field(default=None, max_length=10000)
    enable_analytics: bool = Field(default=False)
    analytics_id: Optional[str] = Field(default=None)


class SiteExportRequest(BaseModel):
    """Request: Website exportieren"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str = Field(..., min_length=1, max_length=50)
    format: ExportFormat = Field(default=ExportFormat.ZIP)
    include_assets: bool = Field(default=True)
    minify: bool = Field(default=True)


class SiteDeployRequest(BaseModel):
    """Request: Website deployen"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str = Field(..., min_length=1, max_length=50)
    target: DeploymentTarget = Field(default=DeploymentTarget.LOCAL)
    target_path: Optional[str] = Field(default=None, max_length=500)
    credentials: Optional[Dict[str, str]] = Field(default=None)
    invalidate_cache: bool = Field(default=False)
    dry_run: bool = Field(default=False)


class SitePreviewRequest(BaseModel):
    """Request: Preview starten"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str = Field(..., min_length=1, max_length=50)
    port: int = Field(default=8000, ge=8000, le=9000)


class TemplateListRequest(BaseModel):
    """Request: Templates auflisten"""
    model_config = ConfigDict(extra="forbid")
    
    category: Optional[str] = Field(default=None)
    search: Optional[str] = Field(default=None)


class CommandRequest(BaseModel):
    """Option-2-Flow Command"""
    model_config = ConfigDict(extra="forbid")
    
    action: str = Field(..., min_length=1, max_length=100)
    params: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = Field(default=None)


# ================== RESPONSE MODELS ==================

class SiteGenerateResponse(BaseModel):
    """Response: Website generiert"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str
    generator: str
    template: str
    pages_generated: int
    output_path: str
    preview_url: Optional[str] = None
    timestamp: str


class SiteExportResponse(BaseModel):
    """Response: Website exportiert"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str
    format: str
    file_path: str
    file_size_bytes: int
    download_url: Optional[str] = None
    timestamp: str


class SiteDeployResponse(BaseModel):
    """Response: Website deployed"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str
    target: str
    deployment_url: Optional[str] = None
    status: str
    dry_run: bool = False
    timestamp: str


class SiteStructure(BaseModel):
    """Response: Site-Struktur"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str
    name: str
    pages: List[Dict[str, Any]]
    routes: List[str]
    assets: List[str]
    total_size_bytes: int
    created_at: str
    updated_at: str


class SiteInfo(BaseModel):
    """Kurze Site-Info für Listen"""
    model_config = ConfigDict(extra="forbid")
    
    site_id: str
    name: str
    pages_count: int
    template: str
    generator: str
    created_at: str
    status: str


class TemplateInfo(BaseModel):
    """Template-Information"""
    model_config = ConfigDict(extra="forbid")
    
    name: str
    description: str
    framework: str
    preview_url: Optional[str] = None
    components: List[str]
    responsive: bool
    dark_mode: bool


class HealthResponse(BaseModel):
    """Health-Check Response"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    service: str
    kuerzel: str
    port: int
    uptime_seconds: float
    version: str
    total_sites: int
    total_pages: int
    disk_usage_mb: float
    strict: bool = True


class ErrorDetail(BaseModel):
    """Fehler-Detail"""
    model_config = ConfigDict(extra="forbid")
    
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class ErrorResponse(BaseModel):
    """Error Response"""
    model_config = ConfigDict(extra="forbid")
    
    error: ErrorDetail


class CommandResponse(BaseModel):
    """Command Response für Option-2-Flow"""
    model_config = ConfigDict(extra="forbid")
    
    status: str
    action: str
    result: Any
    request_id: Optional[str] = None
    timestamp: str
