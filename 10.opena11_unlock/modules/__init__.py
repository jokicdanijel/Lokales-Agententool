# 🔐 Unlock Master Modules - PORTIER PAS-6.0
# All modules for opena11_unlock

from .rbac_engine import RBACEngine
from .permission_store import PermissionStore
from .audit_log import AuditLog
from .metrics import UnlockMetrics, get_metrics
from .ai_unlock_engine import AIUnlockEngine

__version__ = "6.0.0"
__agent__ = "opena11_unlock"

__all__ = [
    "RBACEngine",
    "PermissionStore",
    "AuditLog",
    "UnlockMetrics",
    "get_metrics",
    "AIUnlockEngine"
]
