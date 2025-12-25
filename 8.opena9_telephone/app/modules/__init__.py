# 📞 Telephony Agent 6.0 - Modules Package
# PORTIER PAS-6.0 Compliant

from .ai_voice_engine import AIVoiceEngine
from .metrics import TelephonyMetrics, get_metrics
from .speech_to_text import SpeechToText
from .telephony_api import TelephonyAPI
from .telephony_core import TelephonyCore

__version__ = "6.0.0"
__agent__ = "opena9_telephone"

__all__ = ["TelephonyCore", "TelephonyAPI", "AIVoiceEngine", "SpeechToText", "TelephonyMetrics", "get_metrics"]
