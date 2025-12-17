# 🔐 WORM Audit Log - PORTIER PAS-6.0
# Write-Once-Read-Many Audit Log for Security Compliance

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class AuditLog:
    """
    WORM (Write-Once-Read-Many) Audit Log
    
    Features:
    - Append-only logging (immutable records)
    - JSON-L format for easy parsing
    - SHA-256 hash chain for integrity verification
    - Automatic persistence
    - Event type filtering
    """
    
    def __init__(self, log_path: str = None):
        """Initialize audit log"""
        self.log_path = log_path or os.getenv(
            "AUDIT_LOG_PATH",
            "data/audit.jsonl"
        )
        self.entries: List[Dict[str, Any]] = []
        self.last_hash: str = "genesis"
        self._lock = asyncio.Lock()
        self._counter = 0
        
        # Load existing entries
        self._load_existing()
        
        logger.info(f"✅ WORM Audit Log initialized ({len(self.entries)} existing entries)")
    
    def _load_existing(self):
        """Load existing audit entries"""
        try:
            path = Path(self.log_path)
            if path.exists():
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line)
                            self.entries.append(entry)
                            self.last_hash = entry.get("hash", self.last_hash)
                            self._counter = max(self._counter, entry.get("sequence", 0))
                logger.info(f"📂 Loaded {len(self.entries)} audit entries")
        except Exception as e:
            logger.error(f"Failed to load audit log: {e}")
    
    async def log(self, event: str, payload: Dict[str, Any], 
                 result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Log an audit event (WORM - cannot be modified once written)
        
        Args:
            event: Event type (grant, revoke, check, error, etc.)
            payload: Event payload/parameters
            result: Optional result data
        
        Returns:
            The logged entry
        """
        async with self._lock:
            self._counter += 1
            
            # Build entry
            entry = {
                "sequence": self._counter,
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "event": event,
                "payload": payload,
                "result": result,
                "previous_hash": self.last_hash
            }
            
            # Calculate hash for integrity chain
            entry_str = json.dumps(entry, sort_keys=True)
            entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()
            self.last_hash = entry["hash"]
            
            # Append to in-memory log
            self.entries.append(entry)
            
            # Append to file (WORM - write-once)
            await self._append_to_file(entry)
            
            logger.debug(f"📝 Audit: {event} (seq: {self._counter})")
            
            return entry
    
    async def _append_to_file(self, entry: Dict[str, Any]):
        """Append entry to audit file"""
        try:
            path = Path(self.log_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to append audit entry: {e}")
    
    async def persist(self):
        """Ensure all entries are persisted"""
        # Already persisting in real-time via append
        logger.info(f"💾 Audit log persisted ({len(self.entries)} entries)")
    
    def read(self, limit: int = 100, event_type: str = None, 
             start_sequence: int = None) -> List[Dict[str, Any]]:
        """
        Read audit entries
        
        Args:
            limit: Maximum entries to return
            event_type: Filter by event type
            start_sequence: Start from sequence number
        
        Returns:
            List of audit entries (newest first)
        """
        filtered = self.entries
        
        # Filter by event type
        if event_type:
            filtered = [e for e in filtered if e.get("event") == event_type]
        
        # Filter by sequence
        if start_sequence:
            filtered = [e for e in filtered if e.get("sequence", 0) >= start_sequence]
        
        # Return newest first, limited
        return list(reversed(filtered))[:limit]
    
    def count(self) -> int:
        """Count total audit entries"""
        return len(self.entries)
    
    def last_event(self) -> Optional[Dict[str, Any]]:
        """Get most recent event"""
        if self.entries:
            return self.entries[-1]
        return None
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify hash chain integrity
        
        Returns:
            Verification result
        """
        if not self.entries:
            return {"status": "empty", "verified": True}
        
        previous_hash = "genesis"
        broken_at = None
        
        for i, entry in enumerate(self.entries):
            # Verify previous hash link
            if entry.get("previous_hash") != previous_hash:
                broken_at = i
                break
            
            # Verify entry hash
            entry_copy = entry.copy()
            stored_hash = entry_copy.pop("hash", None)
            entry_str = json.dumps(entry_copy, sort_keys=True)
            calculated_hash = hashlib.sha256(entry_str.encode()).hexdigest()
            
            if stored_hash != calculated_hash:
                broken_at = i
                break
            
            previous_hash = stored_hash
        
        if broken_at is not None:
            return {
                "status": "integrity_broken",
                "verified": False,
                "broken_at_sequence": self.entries[broken_at].get("sequence"),
                "total_entries": len(self.entries)
            }
        
        return {
            "status": "verified",
            "verified": True,
            "total_entries": len(self.entries),
            "last_hash": self.last_hash
        }
    
    def get_event_stats(self) -> Dict[str, int]:
        """Get statistics by event type"""
        stats = {}
        for entry in self.entries:
            event = entry.get("event", "unknown")
            stats[event] = stats.get(event, 0) + 1
        return stats
    
    def search(self, subject: str = None, resource: str = None,
               from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """Search audit entries"""
        results = []
        
        for entry in self.entries:
            payload = entry.get("payload", {})
            
            # Filter by subject
            if subject and payload.get("subject") != subject:
                continue
            
            # Filter by resource
            if resource and payload.get("resource") != resource:
                continue
            
            # Filter by date range
            timestamp = entry.get("timestamp", "")
            if from_date and timestamp < from_date:
                continue
            if to_date and timestamp > to_date:
                continue
            
            results.append(entry)
        
        return results
