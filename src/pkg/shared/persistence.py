"""
Shared Persistence Layer
Common data persistence utilities for JSON and JSONL storage.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime, timezone
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseDataStore(ABC, Generic[T]):
    """
    Abstract base class for data stores.
    
    Provides common interface for loading, saving, and managing data.
    Subclasses should implement _serialize and _deserialize methods.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize data store.
        
        Args:
            file_path: Path to the storage file
        """
        self.file_path = file_path
        self.data: List[T] = []
        
    @abstractmethod
    def _serialize(self, item: T) -> Dict[str, Any]:
        """Serialize an item to dictionary."""
        pass
    
    @abstractmethod
    def _deserialize(self, data: Dict[str, Any]) -> T:
        """Deserialize dictionary to item."""
        pass
    
    def load(self) -> List[T]:
        """
        Load data from JSON file.
        
        Returns:
            List of deserialized items
        """
        if not self.file_path.exists():
            self.data = []
            self.save()
            logger.info(f"Created new data store at {self.file_path}")
            return self.data
        
        try:
            with open(self.file_path, "r") as f:
                file_data = json.load(f)
                
                # Support both direct list and wrapped format
                if isinstance(file_data, list):
                    items = file_data
                elif isinstance(file_data, dict) and "data" in file_data:
                    items = file_data["data"]
                elif isinstance(file_data, dict) and "items" in file_data:
                    items = file_data["items"]
                else:
                    items = []
                
                self.data = [self._deserialize(item) for item in items]
            
            logger.info(f"Loaded {len(self.data)} items from {self.file_path}")
            return self.data
        
        except Exception as e:
            logger.error(f"Error loading data from {self.file_path}: {e}")
            self.data = []
            return self.data
    
    def save(self):
        """
        Save data to JSON file.
        """
        try:
            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create wrapped format with metadata
            file_data = {
                "data": [self._serialize(item) for item in self.data],
                "last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "count": len(self.data)
            }
            
            with open(self.file_path, "w") as f:
                json.dump(file_data, f, indent=2)
            
            logger.debug(f"Saved {len(self.data)} items to {self.file_path}")
        
        except Exception as e:
            logger.error(f"Error saving data to {self.file_path}: {e}")
    
    def add(self, item: T) -> T:
        """Add item to store and save."""
        self.data.append(item)
        self.save()
        return item
    
    def remove(self, predicate) -> bool:
        """Remove items matching predicate and save."""
        initial_len = len(self.data)
        self.data = [item for item in self.data if not predicate(item)]
        
        if len(self.data) < initial_len:
            self.save()
            return True
        return False
    
    def find(self, predicate) -> Optional[T]:
        """Find first item matching predicate."""
        for item in self.data:
            if predicate(item):
                return item
        return None
    
    def find_all(self, predicate) -> List[T]:
        """Find all items matching predicate."""
        return [item for item in self.data if predicate(item)]
    
    def count(self) -> int:
        """Get total count of items."""
        return len(self.data)


class JSONDataStore(BaseDataStore[Dict[str, Any]]):
    """
    Simple JSON data store for dictionary items.
    
    Useful for storing simple data structures without custom serialization.
    """
    
    def _serialize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return item
    
    def _deserialize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data


class AuditLog:
    """
    JSONL-based append-only audit log (WORM-compliant).
    
    Each entry is written as a single line of JSON, making it suitable
    for write-once-read-many (WORM) compliance and streaming.
    """
    
    def __init__(self, log_path: Path):
        """
        Initialize audit log.
        
        Args:
            log_path: Path to JSONL log file
        """
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(
        self,
        operation: str,
        actor: str,
        resource_type: str,
        resource_id: str,
        result: str = "success",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Append audit log entry.
        
        Args:
            operation: Operation performed (e.g., "CREATE", "UPDATE", "DELETE")
            actor: User/service that performed the operation
            resource_type: Type of resource affected (e.g., "profile", "campaign")
            resource_id: ID of the resource
            result: Result of operation (default: "success")
            details: Additional details as dictionary
            
        Example:
            >>> audit_log.log(
            ...     operation="CREATE_PROFILE",
            ...     actor="api_user",
            ...     resource_type="profile",
            ...     resource_id="prof_123",
            ...     result="success",
            ...     details={"name": "John Doe"}
            ... )
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "operation": operation,
            "actor": actor,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "result": result,
            "details": details or {}
        }
        
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            logger.debug(f"Audit log: {operation} by {actor} → {result}")
        except Exception as e:
            logger.error(f"Error writing audit log: {e}")
    
    def read_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Read recent audit log entries.
        
        Args:
            limit: Maximum number of entries to return (from end of file)
            
        Returns:
            List of audit log entries (most recent last)
        """
        if not self.log_path.exists():
            return []
        
        entries = []
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
        
        return entries
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all audit log entries.
        
        Warning: Can be memory-intensive for large logs.
        Consider using read_recent() or streaming for large files.
        
        Returns:
            List of all audit log entries
        """
        if not self.log_path.exists():
            return []
        
        entries = []
        try:
            with open(self.log_path, "r") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading audit log: {e}")
        
        return entries
    
    def count(self) -> int:
        """
        Count total audit log entries.
        
        Returns:
            Number of entries in the log
        """
        if not self.log_path.exists():
            return 0
        
        try:
            with open(self.log_path, "r") as f:
                return sum(1 for line in f if line.strip())
        except Exception as e:
            logger.error(f"Error counting audit log entries: {e}")
            return 0
