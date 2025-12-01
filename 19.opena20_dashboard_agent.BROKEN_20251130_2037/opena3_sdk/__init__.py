"""
OpenA3 SDK für PORTIER 3.0

Python Client Library für OpenWebUI Agent V2
Kompatibel mit Option-2-Flow und Bearer Authentication

Version: 2.0.0
Build: 2025-11-29
PORTIER Compliance: 3.0
"""

__version__ = "2.0.0"
__author__ = "PORTIER 3.0 Team"
__license__ = "Enterprise"

from .client import OpenA3Client
from .models import CMDRequest, ChatRequest, HealthResponse

__all__ = ["OpenA3Client", "CMDRequest", "ChatRequest", "HealthResponse"]