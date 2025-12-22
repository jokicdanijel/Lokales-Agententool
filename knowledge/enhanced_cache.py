from dataclasses import dataclass, asdict
import json
import hashlib
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class EmbeddingSignature:
    model: str
    dims: int
    version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"model": self.model, "dims": self.dims, "version": self.version}


@dataclass(frozen=True)
class RetrievalSignature:
    top_k: int
    filters: Optional[Dict[str, Any]] = None
    metric: Optional[str] = None
    reranker: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"top_k": self.top_k, "filters": self.filters or {}, "metric": self.metric, "reranker": self.reranker}


class EnhancedQueryCache:
    """Utility for generating robust cache keys for retrieval queries.

    The key encodes: normalized query, namespace/tenant/collection, build_id,
    embedding signature, retrieval signature. The output is a short stable key
    prefixed with namespace and tenant/collection for human readability.
    """

    @staticmethod
    def normalize_query(query: str) -> str:
        if query is None:
            return ""
        # simple normalization: strip, lowercase, collapse whitespace
        q = " ".join(query.strip().split())
        return q.lower()

    @staticmethod
    def _canonical_json(obj: Any) -> str:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _sha256_hex(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    @classmethod
    def make_key(
        cls,
        query: str,
        namespace: str = "kb",
        build_id: str = "unknown",
        embedding_sig: Optional[EmbeddingSignature] = None,
        retrieval_sig: Optional[RetrievalSignature] = None,
        tenant_id: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> str:
        norm_q = cls.normalize_query(query)

        payload = {
            "q": norm_q,
            "build_id": build_id,
            "embedding": embedding_sig.to_dict() if embedding_sig else {},
            "retrieval": retrieval_sig.to_dict() if retrieval_sig else {},
        }

        # include namespace/tenant/collection in the human prefix
        prefix_parts = [namespace]
        prefix_parts.append(tenant_id or "-")
        prefix_parts.append(collection or "-")
        prefix = ":".join(prefix_parts)

        canonical = cls._canonical_json(payload)
        digest = cls._sha256_hex(canonical)

        return f"{prefix}:{digest}"
