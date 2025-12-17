# 🔐 Permission Store - PORTIER PAS-6.0
# In-Memory Permission Store with Persistence

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class PermissionStore:
    """
    Permission Store for RBAC
    
    Features:
    - In-memory storage with JSON persistence
    - Subject-based permission grouping
    - Expiration support
    - Atomic operations
    """
    
    def __init__(self, persist_path: str = None):
        """Initialize permission store"""
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.persist_path = persist_path or os.getenv(
            "PERMISSION_STORE_PATH",
            "data/permissions.json"
        )
        self._lock = asyncio.Lock()
        
        logger.info(f"✅ Permission Store initialized (path: {self.persist_path})")
    
    async def load(self):
        """Load permissions from persistent storage"""
        try:
            path = Path(self.persist_path)
            if path.exists():
                async with self._lock:
                    with open(path, 'r') as f:
                        self.data = json.load(f)
                logger.info(f"📂 Loaded {self.count()} permissions from {path}")
            else:
                logger.info("No existing permissions file - starting fresh")
        except Exception as e:
            logger.error(f"Failed to load permissions: {e}")
    
    async def persist(self):
        """Persist permissions to storage"""
        try:
            path = Path(self.persist_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with self._lock:
                with open(path, 'w') as f:
                    json.dump(self.data, f, indent=2)
            
            logger.info(f"💾 Persisted {self.count()} permissions to {path}")
        except Exception as e:
            logger.error(f"Failed to persist permissions: {e}")
    
    async def grant(self, subject: str, resource: str, action: str, 
                   expires: int = 0) -> Dict[str, Any]:
        """
        Grant permission to subject
        
        Args:
            subject: User or entity ID
            resource: Resource path or identifier
            action: Permission action
            expires: Expiration timestamp (0 = never)
        
        Returns:
            Grant result
        """
        async with self._lock:
            if subject not in self.data:
                self.data[subject] = []
            
            # Check for duplicate
            for perm in self.data[subject]:
                if perm["resource"] == resource and perm["action"] == action:
                    # Update expiration
                    perm["expires"] = expires
                    perm["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    logger.info(f"🔄 Updated permission: {subject} -> {action} on {resource}")
                    return {
                        "status": "updated",
                        "subject": subject,
                        "resource": resource,
                        "action": action
                    }
            
            # Add new permission
            permission = {
                "resource": resource,
                "action": action,
                "expires": expires,
                "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            
            self.data[subject].append(permission)
            
            logger.info(f"✅ Granted: {subject} -> {action} on {resource}")
            
            return {
                "status": "granted",
                "subject": subject,
                "resource": resource,
                "action": action,
                "expires": expires
            }
    
    async def revoke(self, subject: str, resource: str = None, 
                    action: str = None) -> Dict[str, Any]:
        """
        Revoke permission from subject
        
        Args:
            subject: User or entity ID
            resource: Resource (optional - if None, matches all)
            action: Action (optional - if None, matches all)
        
        Returns:
            Revoke result
        """
        async with self._lock:
            if subject not in self.data:
                return {"removed": 0, "status": "subject_not_found"}
            
            before_count = len(self.data[subject])
            
            # Filter out matching permissions
            self.data[subject] = [
                p for p in self.data[subject]
                if not self._matches_revoke(p, resource, action)
            ]
            
            removed = before_count - len(self.data[subject])
            
            # Clean up empty subjects
            if not self.data[subject]:
                del self.data[subject]
            
            logger.info(f"🗑️ Revoked {removed} permissions from {subject}")
            
            return {
                "status": "revoked",
                "removed": removed,
                "subject": subject
            }
    
    def _matches_revoke(self, perm: Dict, resource: str, action: str) -> bool:
        """Check if permission matches revoke criteria"""
        resource_match = resource is None or perm["resource"] == resource
        action_match = action is None or perm["action"] == action
        return resource_match and action_match
    
    async def clear_subject(self, subject: str) -> Dict[str, Any]:
        """Remove all permissions for a subject"""
        async with self._lock:
            if subject in self.data:
                count = len(self.data[subject])
                del self.data[subject]
                logger.info(f"🧹 Cleared {count} permissions for {subject}")
                return {"status": "cleared", "removed": count}
            return {"status": "not_found", "removed": 0}
    
    def get(self, subject: str) -> List[Dict[str, Any]]:
        """Get permissions for a subject"""
        return self.data.get(subject, [])
    
    def dump(self) -> Dict[str, List[Dict[str, Any]]]:
        """Dump all permissions"""
        return self.data.copy()
    
    def count(self) -> int:
        """Count total permissions"""
        return sum(len(perms) for perms in self.data.values())
    
    def subject_count(self) -> int:
        """Count unique subjects"""
        return len(self.data)
    
    def summary(self) -> Dict[str, Any]:
        """Get permission summary"""
        actions = {}
        resources = set()
        
        for subject, perms in self.data.items():
            for perm in perms:
                action = perm.get("action", "unknown")
                actions[action] = actions.get(action, 0) + 1
                resources.add(perm.get("resource", "unknown"))
        
        return {
            "total_permissions": self.count(),
            "total_subjects": self.subject_count(),
            "unique_resources": len(resources),
            "actions_breakdown": actions,
            "top_resources": list(resources)[:10]
        }
    
    def search(self, resource_pattern: str = None, action: str = None) -> List[Dict[str, Any]]:
        """Search permissions by criteria"""
        results = []
        
        for subject, perms in self.data.items():
            for perm in perms:
                matches = True
                
                if resource_pattern:
                    if not perm.get("resource", "").startswith(resource_pattern):
                        matches = False
                
                if action and perm.get("action") != action:
                    matches = False
                
                if matches:
                    results.append({
                        "subject": subject,
                        **perm
                    })
        
        return results
