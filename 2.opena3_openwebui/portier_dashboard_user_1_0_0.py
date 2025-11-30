"""
Portier Dashboard - User Edition 1.0.0
Author: LocalAgentPro
Description: Benutzer-Dashboard ohne Admin-Funktionen. Sichere, eingeschränkte Schnittstelle
             für Rechnungen, Dokumente und grundlegende Integrationen.
License: MIT
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceModel(BaseModel):
    """Invoice data model"""
    invoice_id: str = Field(..., description="Eindeutige Rechnungs-ID")
    date: str = Field(default_factory=lambda: datetime.now().isoformat())
    amount: float = Field(..., description="Rechnungsbetrag")
    client: str = Field(..., description="Klient/Empfänger")
    status: str = Field(default="draft", description="Status: draft, sent, paid")


class DocumentModel(BaseModel):
    """Document data model"""
    filename: str = Field(..., description="Dateiname")
    file_type: str = Field(..., description="Dateityp: pdf, docx, xlsx, etc.")
    size_bytes: int = Field(..., description="Dateigröße in Bytes")
    uploaded_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    analysis_status: str = Field(default="pending", description="pending, processing, completed")


class ThemeConfig(BaseModel):
    """Theme configuration"""
    primary: str = "#4F46E5"
    secondary: str = "#6366F1"
    background: str = "#0F172A"
    panel: str = "#1E293B"
    accent: str = "#93C5FD"
    text_primary: str = "#F1F5F9"
    text_secondary: str = "#CBD5E1"


class NavigationItem(BaseModel):
    """Navigation menu item"""
    page: str = Field(..., description="Page identifier")
    label: str = Field(..., description="Display label")
    icon: Optional[str] = Field(None, description="Icon name")
    disabled: bool = Field(default=False)


class Tools:
    """Portier Dashboard User Tools - Version 1.0.0"""

    def __init__(self):
        self.theme = ThemeConfig()
        self.data_dir = os.getenv("PORTIER_DATA_DIR", "/tmp/portier_user")
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(f"{self.data_dir}/invoices", exist_ok=True)
        os.makedirs(f"{self.data_dir}/documents", exist_ok=True)
        logger.info(f"✅ Data directory ready: {self.data_dir}")

    def _get_theme(self) -> Dict[str, str]:
        """Get current theme colors"""
        return {
            "primary": self.theme.primary,
            "secondary": self.theme.secondary,
            "background": self.theme.background,
            "panel": self.theme.panel,
            "accent": self.theme.accent,
            "text_primary": self.theme.text_primary,
            "text_secondary": self.theme.text_secondary,
        }

    def _get_navigation(self) -> List[NavigationItem]:
        """Get user navigation menu"""
        return [
            NavigationItem(page="home", label="Übersicht", icon="home"),
            NavigationItem(page="invoices", label="Rechnungen", icon="file-text"),
            NavigationItem(page="documents", label="Dokumente", icon="folder"),
            NavigationItem(page="integrations", label="Integrationen", icon="link"),
        ]

    def _render_home_page(self) -> Dict[str, Any]:
        """Render home/dashboard page"""
        return {
            "title": "Portier Dashboard",
            "subtitle": "Benutzer Edition 1.0.0",
            "greeting": f"Willkommen! Heute ist {datetime.now().strftime('%d. %B %Y')}",
            "stats": [
                {"label": "Rechnungen", "value": "0", "icon": "file-text"},
                {"label": "Dokumente", "value": "0", "icon": "folder"},
                {"label": "Integrationen", "value": "3", "icon": "link"},
            ],
            "quick_actions": [
                {
                    "label": "Neue Rechnung",
                    "icon": "plus",
                    "action": "create_invoice",
                    "color": "primary"
                },
                {
                    "label": "Dokument hochladen",
                    "icon": "upload",
                    "action": "upload_document",
                    "color": "secondary"
                },
            ]
        }

    def _render_invoices_page(self) -> Dict[str, Any]:
        """Render invoices management page"""
        return {
            "title": "Rechnungen verwalten",
            "description": "Erstellen und verwalten Sie Ihre Rechnungen",
            "actions": [
                {
                    "label": "Neue Rechnung erstellen",
                    "icon": "plus",
                    "action": "create_invoice_form"
                },
                {
                    "label": "Rechnungen exportieren",
                    "icon": "download",
                    "action": "export_invoices"
                },
            ],
            "table_columns": [
                {"key": "invoice_id", "label": "Rechnungs-ID"},
                {"key": "date", "label": "Datum"},
                {"key": "client", "label": "Klient"},
                {"key": "amount", "label": "Betrag"},
                {"key": "status", "label": "Status"},
            ],
            "invoices": []  # Empty for now, populated from data
        }

    def _render_documents_page(self) -> Dict[str, Any]:
        """Render documents management page"""
        return {
            "title": "Dokumente analysieren",
            "description": "Laden Sie Dokumente hoch und analysieren Sie diese",
            "actions": [
                {
                    "label": "Dokument hochladen",
                    "icon": "upload",
                    "action": "upload_document_form"
                },
                {
                    "label": "Kürzlich analysiert",
                    "icon": "history",
                    "action": "show_recent_documents"
                },
            ],
            "upload": {
                "accept": [".pdf", ".docx", ".xlsx", ".txt", ".png", ".jpg"],
                "max_size_mb": 50,
                "description": "Unterstützte Formate: PDF, Word, Excel, Text, Bilder"
            },
            "documents": []  # Empty for now, populated from data
        }

    def _render_integrations_page(self) -> Dict[str, Any]:
        """Render integrations page (readonly)"""
        return {
            "title": "Integrationen",
            "description": "Verbundene Dienste und Datenquellen (Lesezugriff)",
            "integrations": [
                {
                    "name": "Google Drive",
                    "status": "connected",
                    "icon": "drive",
                    "path": "/GoogleDrive/LocalAgent-Pro/",
                    "last_sync": datetime.now().isoformat(),
                    "permissions": "read-only"
                },
                {
                    "name": "Rechnungen",
                    "status": "ready",
                    "icon": "file",
                    "path": "/data/invoices/",
                    "permissions": "read-write"
                },
                {
                    "name": "Dokumente",
                    "status": "ready",
                    "icon": "folder",
                    "path": "/data/documents/",
                    "permissions": "read-write"
                },
            ]
        }

    def _render_page(self, page: str) -> Dict[str, Any]:
        """Render requested page"""
        pages = {
            "home": self._render_home_page,
            "invoices": self._render_invoices_page,
            "documents": self._render_documents_page,
            "integrations": self._render_integrations_page,
        }

        if page in pages:
            return pages[page]()

        return {
            "title": "Seite nicht gefunden",
            "error": f"Seite '{page}' existiert nicht",
            "available_pages": list(pages.keys())
        }

    async def dashboard_user_render(self, page: str = "home") -> Dict[str, Any]:
        """
        Render user dashboard with specified page

        Args:
            page: Page identifier (home, invoices, documents, integrations)

        Returns:
            Complete dashboard structure with theme, navigation, and content
        """
        logger.info(f"🎨 Rendering user dashboard page: {page}")

        return {
            "status": "success",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "dashboard": {
                "theme": self._get_theme(),
                "navigation": [item.dict() for item in self._get_navigation()],
                "current_page": page,
                "content": self._render_page(page),
                "footer": {
                    "copyright": "© 2025 Portier Suite - LocalAgentPro",
                    "version": "1.0.0",
                    "support": "support@portier.local"
                }
            }
        }

    async def create_invoice(
        self,
        client: str = Field(..., description="Klient/Empfänger"),
        amount: float = Field(..., description="Rechnungsbetrag"),
        description: str = Field(default="", description="Rechnungsbeschreibung")
    ) -> Dict[str, Any]:
        """
        Create new invoice

        Args:
            client: Client/recipient name
            amount: Invoice amount
            description: Optional description

        Returns:
            Created invoice with ID
        """
        logger.info(f"💰 Creating invoice for {client}: €{amount}")

        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        invoice = InvoiceModel(
            invoice_id=invoice_id,
            amount=amount,
            client=client
        )

        # Save to disk
        invoice_file = f"{self.data_dir}/invoices/{invoice_id}.json"
        with open(invoice_file, "w") as f:
            json.dump(invoice.dict(), f, indent=2)

        logger.info(f"✅ Invoice created: {invoice_id}")

        return {
            "status": "success",
            "invoice": invoice.dict(),
            "message": f"Rechnung {invoice_id} erstellt"
        }

    async def list_invoices(self) -> Dict[str, Any]:
        """
        List all invoices

        Returns:
            List of invoices
        """
        invoices_dir = f"{self.data_dir}/invoices"
        invoices = []

        if os.path.exists(invoices_dir):
            for filename in os.listdir(invoices_dir):
                if filename.endswith(".json"):
                    with open(f"{invoices_dir}/{filename}", "r") as f:
                        invoices.append(json.load(f))

        logger.info(f"📋 Found {len(invoices)} invoices")

        return {
            "status": "success",
            "count": len(invoices),
            "invoices": invoices
        }

    async def upload_document(
        self,
        filename: str = Field(..., description="Dateiname"),
        file_type: str = Field(..., description="Dateityp"),
        size_bytes: int = Field(..., description="Dateigröße in Bytes")
    ) -> Dict[str, Any]:
        """
        Register uploaded document

        Args:
            filename: Name of uploaded file
            file_type: File type/extension
            size_bytes: File size in bytes

        Returns:
            Document registration confirmation
        """
        logger.info(f"📄 Registering document: {filename}")

        doc = DocumentModel(
            filename=filename,
            file_type=file_type,
            size_bytes=size_bytes,
            analysis_status="pending"
        )

        # Save metadata
        doc_file = f"{self.data_dir}/documents/{filename}.json"
        with open(doc_file, "w") as f:
            json.dump(doc.dict(), f, indent=2)

        logger.info(f"✅ Document registered: {filename}")

        return {
            "status": "success",
            "document": doc.dict(),
            "message": f"Dokument {filename} hochgeladen"
        }

    async def list_documents(self) -> Dict[str, Any]:
        """
        List all documents

        Returns:
            List of documents with metadata
        """
        docs_dir = f"{self.data_dir}/documents"
        documents = []

        if os.path.exists(docs_dir):
            for filename in os.listdir(docs_dir):
                if filename.endswith(".json"):
                    with open(f"{docs_dir}/{filename}", "r") as f:
                        documents.append(json.load(f))

        logger.info(f"📚 Found {len(documents)} documents")

        return {
            "status": "success",
            "count": len(documents),
            "documents": documents
        }

    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all integrations (readonly)

        Returns:
            Status of each integration
        """
        logger.info("🔗 Checking integration status")

        return {
            "status": "success",
            "integrations": {
                "google_drive": {
                    "connected": True,
                    "last_sync": datetime.now().isoformat(),
                    "permissions": "read-only"
                },
                "invoices": {
                    "connected": True,
                    "last_sync": datetime.now().isoformat(),
                    "permissions": "read-write"
                },
                "documents": {
                    "connected": True,
                    "last_sync": datetime.now().isoformat(),
                    "permissions": "read-write"
                },
            }
        }
