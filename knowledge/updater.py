from typing import List, Dict, Any
from .schema import DocumentSchema, SchemaViolation
from .dedup import content_sha256, DedupIndex
from .write_queue import WriteQueue
from .index_integrity import IndexIntegrityManager
from .metrics import inc_counter


class IngestManager:
    def __init__(self, dedup: DedupIndex, write_queue: WriteQueue, index_path: str):
        self.dedup = dedup
        self.wq = write_queue
        self.index_path = index_path

    def _commit_docs(self, docs: List[Dict[str, Any]]) -> int:
        # Actual commit runs in single-writer context
        for doc in docs:
            # append to index with checksum
            IndexIntegrityManager.append_line(self.index_path, doc)
        inc_counter('ingest_committed_docs_total')
        return len(docs)

    def ingest(self, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate, dedupe and submit commit job; returns summary."""
        accepted = []
        rejected = []
        skipped = []

        for doc in docs:
            try:
                DocumentSchema.validate(doc)
            except SchemaViolation as e:
                rejected.append({'doc': doc, 'reason': e.reason})
                inc_counter('kb_schema_reject_total')
                continue

            h = content_sha256(doc.get('text', ''))
            if self.dedup.seen(h):
                skipped.append(doc)
                inc_counter('kb_dedup_skipped_total')
                continue

            # mark as seen and accept
            self.dedup.add(h)
            accepted.append(doc)

        if accepted:
            fut = self.wq.submit(self._commit_docs, accepted)
            # block for commit result for now; in real flow could be async
            result = fut.result()
            inc_counter('kb_ingest_jobs_total')
        else:
            result = 0

        return {'accepted': len(accepted), 'rejected': len(rejected), 'skipped': len(skipped), 'committed': result}
