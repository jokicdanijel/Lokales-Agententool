"""Knowledge DB utilities package"""

from .cache_store import CacheStore
from .dedup import DedupIndex, content_sha256
from .enhanced_cache import EmbeddingSignature, EnhancedQueryCache, RetrievalSignature
from .index_integrity import IndexIntegrityManager
from .metrics import clear, get_metrics_text, inc_counter
from .schema import DocumentSchema, SchemaViolation
from .write_queue import WriteQueue

__all__ = [
    "EnhancedQueryCache",
    "EmbeddingSignature",
    "RetrievalSignature",
    "CacheStore",
    "WriteQueue",
    "IndexIntegrityManager",
    "DedupIndex",
    "content_sha256",
    "DocumentSchema",
    "SchemaViolation",
    "inc_counter",
    "get_metrics_text",
    "clear",
]
