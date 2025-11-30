# 📱 Social Media Modules - PORTIER PAS-6.0
# All modules for opena12_social_media

from .social_core import SocialCore
from .scheduler import Scheduler
from .metrics import SocialMetrics, get_metrics
from .media_handler import MediaHandler

# Platform modules
from .platform_linkedin import LinkedInPlatform
from .platform_x import XPlatform
from .platform_facebook import FacebookPlatform
from .platform_instagram import InstagramPlatform

__version__ = "6.0.0"
__agent__ = "opena12_social_media"

__all__ = [
    "SocialCore",
    "Scheduler",
    "SocialMetrics",
    "get_metrics",
    "MediaHandler",
    "LinkedInPlatform",
    "XPlatform",
    "FacebookPlatform",
    "InstagramPlatform"
]
