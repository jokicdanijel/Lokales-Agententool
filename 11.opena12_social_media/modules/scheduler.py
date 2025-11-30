# 📱 Scheduler Module - PORTIER PAS-6.0
# Post Scheduling & Queue Management

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class ScheduledPost:
    """Scheduled post data class"""
    job_id: str
    platforms: List[str]
    text: str
    scheduled_at: str
    hashtags: List[str] = field(default_factory=list)
    media: List[str] = field(default_factory=list)
    status: str = "scheduled"
    created_at: str = ""
    executed_at: Optional[str] = None
    result: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Scheduler:
    """Post Scheduler with Queue Management"""
    
    def __init__(self, core=None):
        self.core = core
        self.queue: List[ScheduledPost] = []
        self.history: List[ScheduledPost] = []
        
        # Storage path
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file = self.data_dir / "scheduler_queue.json"
        
        # Load existing queue
        self._load_queue()
        
        logger.info(f"✅ Scheduler initialized with {len(self.queue)} queued posts")
    
    def _load_queue(self):
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r") as f:
                    data = json.load(f)
                    self.queue = [
                        ScheduledPost(**item) for item in data.get("queue", [])
                    ]
                    self.history = [
                        ScheduledPost(**item) for item in data.get("history", [])[-50:]
                    ]
            except Exception as e:
                logger.error(f"Error loading queue: {e}")
                self.queue = []
    
    def _save_queue(self):
        """Save queue to file"""
        try:
            data = {
                "queue": [p.to_dict() for p in self.queue],
                "history": [p.to_dict() for p in self.history[-50:]],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.queue_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving queue: {e}")
    
    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        import time
        return f"job_{int(time.time() * 1000000)}"
    
    def schedule(self, platforms: List[str], text: str, when: str,
                hashtags: Optional[List[str]] = None,
                media: Optional[List[str]] = None) -> Dict[str, Any]:
        """Schedule a post for future publishing"""
        
        if not platforms:
            return {"status": "error", "message": "No platforms specified"}
        
        if not text:
            return {"status": "error", "message": "No text provided"}
        
        if not when:
            return {"status": "error", "message": "No schedule time provided"}
        
        # Validate scheduled time
        try:
            scheduled_dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
        except ValueError as e:
            return {"status": "error", "message": f"Invalid datetime format: {e}"}
        
        job_id = self._generate_job_id()
        
        post = ScheduledPost(
            job_id=job_id,
            platforms=platforms,
            text=text,
            scheduled_at=when,
            hashtags=hashtags or [],
            media=media or [],
            status="scheduled",
            created_at=datetime.now().isoformat()
        )
        
        self.queue.append(post)
        self._save_queue()
        
        logger.info(f"📅 Scheduled post {job_id} for {when}")
        
        return {
            "status": "success",
            "message": f"Post scheduled for {when}",
            "job_id": job_id,
            "platforms": platforms,
            "scheduled_at": when
        }
    
    def cancel(self, job_id: str) -> Dict[str, Any]:
        """Cancel a scheduled post"""
        for i, post in enumerate(self.queue):
            if post.job_id == job_id:
                post.status = "cancelled"
                self.history.append(post)
                del self.queue[i]
                self._save_queue()
                
                logger.info(f"🚫 Cancelled scheduled post {job_id}")
                
                return {
                    "status": "success",
                    "message": f"Post {job_id} cancelled",
                    "job_id": job_id
                }
        
        return {"status": "error", "message": f"Job {job_id} not found"}
    
    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get scheduled post by ID"""
        for post in self.queue:
            if post.job_id == job_id:
                return post.to_dict()
        
        # Check history
        for post in self.history:
            if post.job_id == job_id:
                return post.to_dict()
        
        return None
    
    def count(self) -> int:
        """Get total queue count"""
        return len(self.queue)
    
    def pending_count(self) -> int:
        """Get pending posts count"""
        return len([p for p in self.queue if p.status == "scheduled"])
    
    def dump(self) -> List[Dict[str, Any]]:
        """Dump all queued posts"""
        return [p.to_dict() for p in self.queue]
    
    def get_ready_posts(self) -> List[ScheduledPost]:
        """Get posts ready for publishing"""
        now = datetime.now()
        ready = []
        
        for post in self.queue:
            if post.status == "scheduled":
                try:
                    scheduled = datetime.fromisoformat(
                        post.scheduled_at.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                    
                    if scheduled <= now:
                        ready.append(post)
                except Exception as e:
                    logger.error(f"Error parsing schedule time: {e}")
        
        return ready
    
    async def process_ready_posts(self) -> List[Dict[str, Any]]:
        """Process all ready posts"""
        if not self.core:
            return []
        
        ready_posts = self.get_ready_posts()
        results = []
        
        for post in ready_posts:
            try:
                # Execute post
                result = await self.core.post_now(
                    platforms=post.platforms,
                    text=post.text,
                    hashtags=post.hashtags,
                    media=post.media
                )
                
                # Update post status
                post.status = "executed"
                post.executed_at = datetime.now().isoformat()
                post.result = result
                
                # Move to history
                self.queue.remove(post)
                self.history.append(post)
                
                results.append({
                    "job_id": post.job_id,
                    "status": "executed",
                    "result": result
                })
                
                logger.info(f"✅ Executed scheduled post {post.job_id}")
                
            except Exception as e:
                logger.error(f"Error executing post {post.job_id}: {e}")
                post.status = "failed"
                post.result = {"error": str(e)}
                results.append({
                    "job_id": post.job_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        self._save_queue()
        return results
    
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get execution history"""
        return [p.to_dict() for p in self.history[-limit:]]
