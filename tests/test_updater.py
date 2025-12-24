from knowledge.dedup import DedupIndex
from knowledge.metrics import clear, get_metrics_text
from knowledge.updater import IngestManager
from knowledge.write_queue import WriteQueue


def make_doc(i):
    return {
        "id": f"d{i}",
        "text": f"hello {i}",
        "meta": {"n": i},
        "source": "unit",
        "created_at": "2025-12-22T10:00:00Z",
        "schema_version": 1,
    }


def test_ingest_accepts_and_skips(tmp_path):
    clear()
    dedup_file = tmp_path / "dedup.txt"
    index_file = tmp_path / "index.jsonl"

    dedup = DedupIndex(str(dedup_file))
    wq = WriteQueue()
    wq.start()
    ing = IngestManager(dedup, wq, str(index_file))

    docs = [make_doc(i) for i in range(3)]
    res = ing.ingest(docs)
    assert res["accepted"] == 3
    assert res["committed"] == 3

    # ingest same docs again -> all skipped
    res2 = ing.ingest(docs)
    assert res2["accepted"] == 0
    assert res2["skipped"] == 3

    wq.stop()

    text = get_metrics_text()
    assert "kb_dedup_skipped_total" in text
    assert "ingest_committed_docs_total" in text


def test_ingest_rejects_invalid(tmp_path):
    clear()
    dedup = DedupIndex()
    wq = WriteQueue()
    wq.start()
    ing = IngestManager(dedup, wq, str(tmp_path / "index.jsonl"))

    bad = {"id": "b1", "text": "x", "meta": {}}  # missing required fields
    res = ing.ingest([bad])
    assert res["rejected"] == 1
    assert res["committed"] == 0
    wq.stop()
