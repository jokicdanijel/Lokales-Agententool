# 📞 Telephony Agent 6.0 - Modules Package
# PORTIER PAS-6.0 Compliant

from .telephony_core import TelephonyCore
from .telephony_api import TelephonyAPI
from .ai_voice_engine import AIVoiceEngine
from .speech_to_text import SpeechToText
from .metrics import TelephonyMetrics, get_metrics

__version__ = "6.0.0"
__agent__ = "opena9_telephone"

__all__ = [
    "TelephonyCore",
    "TelephonyAPI", 
    "AIVoiceEngine",
    "SpeechToText",
    "TelephonyMetrics",
    "get_metrics"
]