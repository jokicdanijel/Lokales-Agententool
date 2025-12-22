import pytest

from knowledge.schema import DocumentSchema, SchemaViolation


def test_valid_doc_passes():
    doc = {
        "id": "doc1",
        "text": "hello",
        "meta": {"source": "unit"},
        "source": "unit-test",
        "created_at": "2025-12-22T10:00:00Z",
        "schema_version": 1,
    }
    DocumentSchema.validate(doc)


def test_missing_field_raises():
    doc = {
        "id": "doc1",
        "text": "hello",
        "meta": {},
        "source": "unit-test",
        # missing created_at, schema_version
    }
    with pytest.raises(SchemaViolation):
        DocumentSchema.validate(doc)


def test_text_too_long_raises():
    doc = {
        "id": "doc1",
        "text": "x" * 200000,
        "meta": {},
        "source": "unit-test",
        "created_at": "2025-12-22T10:00:00Z",
        "schema_version": 1,
    }
    with pytest.raises(SchemaViolation) as e:
        DocumentSchema.validate(doc, max_text_chars=1000)
    assert "text_too_long" in str(e.value)
