"""
Unit tests for shared persistence module.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import dataclass, asdict

from src.pkg.shared.persistence import (
    BaseDataStore,
    JSONDataStore,
    AuditLog,
)


@dataclass
class TestItem:
    """Test data class for store tests."""
    id: str
    name: str
    value: int


class TestItemStore(BaseDataStore[TestItem]):
    """Concrete implementation of BaseDataStore for testing."""
    
    def _serialize(self, item: TestItem) -> dict:
        return asdict(item)
    
    def _deserialize(self, data: dict) -> TestItem:
        return TestItem(**data)


class TestBaseDataStore:
    """Tests for BaseDataStore class."""
    
    def test_create_new_store(self):
        """Should create new store file."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            assert store_path.exists()
            assert len(store.data) == 0
    
    def test_add_item(self):
        """Should add item to store."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            item = TestItem(id="1", name="Test", value=42)
            store.add(item)
            
            assert len(store.data) == 1
            assert store.data[0].id == "1"
    
    def test_save_and_load(self):
        """Should persist data across save/load cycles."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            
            # Create and save
            store1 = TestItemStore(store_path)
            store1.load()
            store1.add(TestItem(id="1", name="Item1", value=10))
            store1.add(TestItem(id="2", name="Item2", value=20))
            
            # Load in new instance
            store2 = TestItemStore(store_path)
            store2.load()
            
            assert len(store2.data) == 2
            assert store2.data[0].id == "1"
            assert store2.data[1].id == "2"
    
    def test_find_item(self):
        """Should find item by predicate."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            store.add(TestItem(id="1", name="Alice", value=10))
            store.add(TestItem(id="2", name="Bob", value=20))
            
            found = store.find(lambda item: item.name == "Bob")
            assert found is not None
            assert found.id == "2"
    
    def test_find_all(self):
        """Should find all items matching predicate."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            store.add(TestItem(id="1", name="Alice", value=10))
            store.add(TestItem(id="2", name="Bob", value=20))
            store.add(TestItem(id="3", name="Charlie", value=10))
            
            found = store.find_all(lambda item: item.value == 10)
            assert len(found) == 2
            assert found[0].name == "Alice"
            assert found[1].name == "Charlie"
    
    def test_remove_items(self):
        """Should remove items matching predicate."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            store.add(TestItem(id="1", name="Alice", value=10))
            store.add(TestItem(id="2", name="Bob", value=20))
            
            removed = store.remove(lambda item: item.name == "Alice")
            
            assert removed is True
            assert len(store.data) == 1
            assert store.data[0].name == "Bob"
    
    def test_count(self):
        """Should return correct count."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = TestItemStore(store_path)
            store.load()
            
            assert store.count() == 0
            
            store.add(TestItem(id="1", name="Alice", value=10))
            assert store.count() == 1
            
            store.add(TestItem(id="2", name="Bob", value=20))
            assert store.count() == 2


class TestJSONDataStore:
    """Tests for JSONDataStore class."""
    
    def test_store_dictionaries(self):
        """Should store and load dictionaries."""
        with TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.json"
            store = JSONDataStore(store_path)
            store.load()
            
            store.add({"id": "1", "name": "Test"})
            store.add({"id": "2", "name": "Another"})
            
            # Reload
            store2 = JSONDataStore(store_path)
            store2.load()
            
            assert len(store2.data) == 2
            assert store2.data[0]["name"] == "Test"


class TestAuditLog:
    """Tests for AuditLog class."""
    
    def test_create_audit_log(self):
        """Should create audit log file."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit.jsonl"
            audit_log = AuditLog(log_path)
            
            audit_log.log(
                operation="CREATE",
                actor="test_user",
                resource_type="profile",
                resource_id="prof_1"
            )
            
            assert log_path.exists()
    
    def test_log_entry(self):
        """Should log entry with all fields."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit.jsonl"
            audit_log = AuditLog(log_path)
            
            audit_log.log(
                operation="CREATE",
                actor="test_user",
                resource_type="profile",
                resource_id="prof_1",
                result="success",
                details={"name": "John Doe"}
            )
            
            # Read back
            entries = audit_log.read_all()
            assert len(entries) == 1
            assert entries[0]["operation"] == "CREATE"
            assert entries[0]["actor"] == "test_user"
            assert entries[0]["details"]["name"] == "John Doe"
    
    def test_read_recent(self):
        """Should read recent entries with limit."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit.jsonl"
            audit_log = AuditLog(log_path)
            
            # Log multiple entries
            for i in range(10):
                audit_log.log(
                    operation=f"OP_{i}",
                    actor="test_user",
                    resource_type="test",
                    resource_id=str(i)
                )
            
            # Read only last 3
            recent = audit_log.read_recent(limit=3)
            assert len(recent) == 3
            assert recent[0]["operation"] == "OP_7"
            assert recent[2]["operation"] == "OP_9"
    
    def test_count_entries(self):
        """Should count total entries."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit.jsonl"
            audit_log = AuditLog(log_path)
            
            assert audit_log.count() == 0
            
            audit_log.log("OP1", "user", "type", "id")
            assert audit_log.count() == 1
            
            audit_log.log("OP2", "user", "type", "id")
            assert audit_log.count() == 2
    
    def test_append_only(self):
        """Should be append-only (no modification of existing entries)."""
        with TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "audit.jsonl"
            audit_log = AuditLog(log_path)
            
            audit_log.log("OP1", "user", "type", "id1")
            audit_log.log("OP2", "user", "type", "id2")
            
            # Entries should be preserved
            entries = audit_log.read_all()
            assert len(entries) == 2
            assert entries[0]["operation"] == "OP1"
            assert entries[1]["operation"] == "OP2"
