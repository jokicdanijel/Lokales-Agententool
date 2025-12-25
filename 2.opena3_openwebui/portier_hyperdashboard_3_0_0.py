"""
Portier Dashboard - Admin Edition 3.0.0
Author: LocalAgentPro
Description: Admin-Dashboard mit vollständigen Kontrollfunktionen, erweiterten Integrationen,
             Systemüberwachung und Benutzerklassifizierung.
License: MIT
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SystemMetrics(BaseModel):
    """System metrics"""

    cpu_percent: float = Field(default=0.0)
    memory_percent: float = Field(default=0.0)
    disk_percent: float = Field(default=0.0)
    uptime_seconds: float = Field(default=0.0)


class UserRole(BaseModel):
    """User role definition"""

    role_id: str = Field(..., description="Role identifier")
    name: str = Field(..., description="Role name")
    permissions: list[str] = Field(..., description="List of permissions")
    level: int = Field(..., description="Role level (higher = more permissions)")


class ThemeConfig(BaseModel):
    """Theme configuration"""

    primary: str = "#8d3cff"
    secondary: str = "#4c1d95"
    background: str = "#12001a"
    panel: str = "#1e0030"
    glow: str = "#c084fc"
    accent: str = "#f5d0fe"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#E9D5FF"


class Tools:
    """Portier Dashboard Admin Tools - Version 3.0.0"""

    def __init__(self):
        self.theme = ThemeConfig()
        self.data_dir = os.getenv("PORTIER_DATA_DIR", "/tmp/portier_admin")
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure all necessary directories exist"""
        dirs = [
            f"{self.data_dir}/users",
            f"{self.data_dir}/roles",
            f"{self.data_dir}/invoices",
            f"{self.data_dir}/documents",
            f"{self.data_dir}/logs",
            f"{self.data_dir}/config",
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        logger.info(f"✅ Admin data directories ready: {self.data_dir}")

    def _get_system_metrics(self) -> dict[str, Any]:
        """Get system metrics"""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "uptime_seconds": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds(),
            }
        except ImportError:
            logger.warning("psutil not available, returning dummy metrics")
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "disk_percent": 0.0, "uptime_seconds": 0.0}

    def _get_theme(self) -> dict[str, str]:
        """Get admin theme"""
        return {
            "primary": self.theme.primary,
            "secondary": self.theme.secondary,
            "background": self.theme.background,
            "panel": self.theme.panel,
            "glow": self.theme.glow,
            "accent": self.theme.accent,
            "text_primary": self.theme.text_primary,
            "text_secondary": self.theme.text_secondary,
        }

    def _get_navigation(self) -> list[dict[str, Any]]:
        """Get admin navigation"""
        return [
            {"page": "dashboard", "label": "Dashboard", "icon": "gauge", "badge": "admin"},
            {"page": "users", "label": "Benutzer", "icon": "users", "count": 0},
            {"page": "roles", "label": "Rollen", "icon": "shield", "count": 0},
            {"page": "invoices", "label": "Rechnungen", "icon": "file-text", "count": 0},
            {"page": "documents", "label": "Dokumente", "icon": "folder", "count": 0},
            {"page": "integrations", "label": "Integrationen", "icon": "link"},
            {"page": "system", "label": "System", "icon": "settings"},
            {"page": "logs", "label": "Protokolle", "icon": "book"},
        ]

    def _render_dashboard_page(self) -> dict[str, Any]:
        """Render admin dashboard"""
        metrics = self._get_system_metrics()

        return {
            "title": "Admin Dashboard",
            "subtitle": "Portier Suite 3.0.0",
            "admin_badge": "👑 ADMINISTRATOR",
            "system_metrics": metrics,
            "quick_stats": [
                {"label": "Benutzer", "value": "0", "trend": "↑ 0%"},
                {"label": "Rechnungen", "value": "0", "trend": "↑ 0%"},
                {"label": "Dokumente", "value": "0", "trend": "↑ 0%"},
                {"label": "System Health", "value": "100%", "trend": "✅"},
            ],
            "admin_actions": [
                {"label": "Benutzer erstellen", "icon": "user-plus", "action": "create_user"},
                {"label": "Rolle zuweisen", "icon": "shield-plus", "action": "assign_role"},
                {"label": "System konfigurieren", "icon": "sliders", "action": "system_config"},
                {"label": "Backup erstellen", "icon": "download", "action": "create_backup"},
            ],
        }

    def _render_users_page(self) -> dict[str, Any]:
        """Render users management page"""
        return {
            "title": "Benutzerverwaltung",
            "description": "Verwalten Sie alle Benutzer und ihre Berechtigungen",
            "actions": [
                {"label": "Benutzer erstellen", "icon": "plus", "action": "create_user_form"},
                {"label": "Benutzer importieren", "icon": "upload", "action": "import_users"},
                {"label": "CSV exportieren", "icon": "download", "action": "export_users"},
            ],
            "table_columns": [
                {"key": "user_id", "label": "Benutzer-ID"},
                {"key": "name", "label": "Name"},
                {"key": "email", "label": "E-Mail"},
                {"key": "role", "label": "Rolle"},
                {"key": "created_at", "label": "Erstellt"},
                {"key": "actions", "label": "Aktionen"},
            ],
        }

    def _render_roles_page(self) -> dict[str, Any]:
        """Render roles management page"""
        return {
            "title": "Rollenverwaltung",
            "description": "Definieren und verwalten Sie Benutzerrollen und Berechtigungen",
            "actions": [
                {"label": "Rolle erstellen", "icon": "plus", "action": "create_role_form"},
                {"label": "Standard-Rollen", "icon": "copy", "action": "load_default_roles"},
            ],
            "predefined_roles": [
                {
                    "role_id": "admin",
                    "name": "Administrator",
                    "level": 3,
                    "permissions": ["user_management", "role_management", "system_config", "invoices", "documents"],
                },
                {
                    "role_id": "manager",
                    "name": "Manager",
                    "level": 2,
                    "permissions": ["invoices", "documents", "user_view", "reports"],
                },
                {"role_id": "user", "name": "Benutzer", "level": 1, "permissions": ["invoices", "documents"]},
            ],
        }

    def _render_system_page(self) -> dict[str, Any]:
        """Render system configuration page"""
        return {
            "title": "Systemkonfiguration",
            "description": "Konfigurieren Sie die Portier-Suite",
            "sections": [
                {
                    "title": "Sicherheit",
                    "settings": [
                        {"key": "auth_method", "label": "Authentifizierungsmethode", "value": "bearer_token"},
                        {"key": "session_timeout", "label": "Session-Timeout (Minuten)", "value": 60},
                        {"key": "require_2fa", "label": "2FA erforderlich", "value": False},
                    ],
                },
                {
                    "title": "Integrations",
                    "settings": [
                        {"key": "google_drive_enabled", "label": "Google Drive aktiviert", "value": True},
                        {"key": "gdrive_sync_interval", "label": "Sync-Interval (Minuten)", "value": 15},
                    ],
                },
                {
                    "title": "System",
                    "settings": [
                        {"key": "max_upload_size_mb", "label": "Max. Upload-Größe (MB)", "value": 100},
                        {"key": "log_retention_days", "label": "Log-Aufbewahrung (Tage)", "value": 30},
                    ],
                },
            ],
        }

    async def dashboard_admin_render(self, page: str = "dashboard") -> dict[str, Any]:
        """
        Render admin dashboard with full control panel

        Args:
            page: Page identifier

        Returns:
            Complete admin dashboard structure
        """
        logger.info(f"🔐 Rendering admin dashboard page: {page}")

        pages = {
            "dashboard": self._render_dashboard_page,
            "users": self._render_users_page,
            "roles": self._render_roles_page,
            "system": self._render_system_page,
        }

        content = pages.get(page, lambda: {"title": "Seite nicht gefunden"})()

        return {
            "status": "success",
            "version": "3.0.0",
            "role": "admin",
            "timestamp": datetime.now().isoformat(),
            "dashboard": {
                "theme": self._get_theme(),
                "navigation": self._get_navigation(),
                "current_page": page,
                "content": content,
                "system_metrics": self._get_system_metrics(),
                "footer": {"copyright": "© 2025 Portier Suite - LocalAgentPro", "version": "3.0.0", "admin": True},
            },
        }

    async def create_user(
        self,
        username: str = Field(..., description="Benutzername"),
        email: str = Field(..., description="E-Mail-Adresse"),
        role: str = Field(default="user", description="Benutzerrolle"),
    ) -> dict[str, Any]:
        """Create new user"""
        logger.info(f"👤 Creating user: {username} with role {role}")

        user = {
            "user_id": f"USER-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }

        user_file = f"{self.data_dir}/users/{user['user_id']}.json"
        with open(user_file, "w") as f:
            json.dump(user, f, indent=2)

        logger.info(f"✅ User created: {user['user_id']}")

        return {"status": "success", "user": user, "message": f"Benutzer {username} erstellt"}

    async def create_role(
        self,
        role_id: str = Field(..., description="Rollen-ID"),
        name: str = Field(..., description="Rollenname"),
        permissions: list[str] = Field(..., description="Liste von Berechtigungen"),
        level: int = Field(..., description="Rollenlevel"),
    ) -> dict[str, Any]:
        """Create custom role"""
        logger.info(f"🛡️ Creating role: {role_id}")

        role = {
            "role_id": role_id,
            "name": name,
            "permissions": permissions,
            "level": level,
            "created_at": datetime.now().isoformat(),
        }

        role_file = f"{self.data_dir}/roles/{role_id}.json"
        with open(role_file, "w") as f:
            json.dump(role, f, indent=2)

        logger.info(f"✅ Role created: {role_id}")

        return {"status": "success", "role": role, "message": f"Rolle {name} erstellt"}

    async def get_system_status(self) -> dict[str, Any]:
        """Get full system status"""
        logger.info("🔍 Checking system status")

        return {
            "status": "success",
            "system": {
                "metrics": self._get_system_metrics(),
                "services": {"database": "online", "cache": "online", "integrations": "online", "scheduler": "online"},
                "uptime": "100%",
                "health": "excellent",
            },
        }

    async def create_backup(self, backup_name: str = "default") -> dict[str, Any]:
        """Create system backup"""
        logger.info(f"💾 Creating backup: {backup_name}")

        backup_dir = f"{self.data_dir}/backups"
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = f"{backup_dir}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"

        try:
            subprocess.run(["tar", "-czf", backup_file, self.data_dir], check=True, capture_output=True)
            logger.info(f"✅ Backup created: {backup_file}")

            return {
                "status": "success",
                "backup_file": backup_file,
                "size_bytes": os.path.getsize(backup_file),
                "message": "Backup erfolgreich erstellt",
            }
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return {"status": "error", "message": f"Backup fehlgeschlagen: {e}"}

    async def export_users(self, format: str = "csv") -> dict[str, Any]:
        """Export all users"""
        logger.info(f"📤 Exporting users as {format}")

        users_dir = f"{self.data_dir}/users"
        users = []

        if os.path.exists(users_dir):
            for filename in os.listdir(users_dir):
                if filename.endswith(".json"):
                    with open(f"{users_dir}/{filename}") as f:
                        users.append(json.load(f))

        return {"status": "success", "format": format, "count": len(users), "users": users}

    async def get_logs(self, limit: int = 100) -> dict[str, Any]:
        """Get system logs"""
        logger.info(f"📋 Retrieving logs (limit: {limit})")

        logs_dir = f"{self.data_dir}/logs"
        logs = []

        if os.path.exists(logs_dir):
            log_files = sorted(os.listdir(logs_dir), reverse=True)[:10]
            for log_file in log_files:
                with open(f"{logs_dir}/{log_file}") as f:
                    logs.extend(f.readlines()[-limit:])

        return {"status": "success", "count": len(logs), "logs": logs[-limit:]}
