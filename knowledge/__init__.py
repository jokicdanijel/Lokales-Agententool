"""Knowledge DB utilities package"""
from .enhanced_cache import EnhancedQueryCache, EmbeddingSignature, RetrievalSignature
from .cache_store import CacheStore
from .write_queue import WriteQueue
from .index_integrity import IndexIntegrityManager
from .dedup import DedupIndex, content_sha256
from .schema import DocumentSchema, SchemaViolation
from .metrics import inc_counter, get_metrics_text, clear

__all__ = [
    'EnhancedQueryCache', 'EmbeddingSignature', 'RetrievalSignature',
    'CacheStore', 'WriteQueue', 'IndexIntegrityManager', 'DedupIndex', 'content_sha256',
    'DocumentSchema', 'SchemaViolation', 'inc_counter', 'get_metrics_text', 'clear'
]
