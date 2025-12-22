from knowledge.dedup import content_sha256, DedupIndex
import tempfile


def test_content_sha256_normalizes_whitespace():
    a = "This   is  a test\n"
    b = "This is a    test"
    assert content_sha256(a) == content_sha256(b)


def test_dedup_add_and_seen(tmp_path):
    d = DedupIndex()
    h = content_sha256("hello world")
    assert not d.seen(h)
    assert d.add(h) is True
    assert d.seen(h) is True
    assert d.add(h) is False


def test_dedup_persistence(tmp_path):
    path = tmp_path / "dedup.txt"
    d1 = DedupIndex(str(path))
    h = content_sha256("persist me")
    assert d1.add(h) is True
    # new instance should load existing
    d2 = DedupIndex(str(path))
    assert d2.seen(h) is True
    assert d2.size() == 1
