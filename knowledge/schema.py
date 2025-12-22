import json
from typing import Dict, Any


class SchemaViolation(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class DocumentSchema:
    REQUIRED = ["id", "text", "meta", "source", "created_at", "schema_version"]
    DEFAULT_MAX_TEXT = 100_000  # chars
    DEFAULT_MAX_META = 10_000   # bytes

    @classmethod
    def validate(cls, doc: Dict[str, Any], max_text_chars: int = None, max_meta_bytes: int = None) -> None:
        if max_text_chars is None:
            max_text_chars = cls.DEFAULT_MAX_TEXT
        if max_meta_bytes is None:
            max_meta_bytes = cls.DEFAULT_MAX_META

        # required fields
        for f in cls.REQUIRED:
            if f not in doc:
                raise SchemaViolation(f"missing_required_field:{f}")

        # field types
        if not isinstance(doc.get('text'), str):
            raise SchemaViolation('invalid_text_type')
        if not isinstance(doc.get('meta'), dict):
            raise SchemaViolation('invalid_meta_type')

        # length limits
        if len(doc.get('text', '')) > max_text_chars:
            raise SchemaViolation('text_too_long')
        meta_bytes = len(json.dumps(doc.get('meta', {})).encode('utf-8'))
        if meta_bytes > max_meta_bytes:
            raise SchemaViolation('meta_too_large')

        # schema_version
        if not isinstance(doc.get('schema_version'), (int, str)):
            raise SchemaViolation('invalid_schema_version')

        # if we reach here, doc passes validation
        return None
