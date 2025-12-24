# 📱 Media Handler Module - PORTIER PAS-6.0
# Image & Video Processing for Social Media

import base64
import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MediaHandler:
    """Media Upload & Processing Handler"""

    def __init__(self):
        """Initialize media handler"""
        self.media_dir = Path("media")
        self.media_dir.mkdir(exist_ok=True)

        self.supported_images = ["jpg", "jpeg", "png", "gif", "webp"]
        self.supported_videos = ["mp4", "mov", "avi", "webm"]

        self.stats = {"uploads": 0, "total_size_bytes": 0, "media_types": {}}

        # Platform-specific requirements
        self.platform_specs = {
            "linkedin": {
                "image": ["jpg", "jpeg", "png", "gif"],
                "video": ["mp4", "mov"],
                "max_image_size_mb": 8,
                "max_video_size_mb": 200,
            },
            "x": {
                "image": ["jpg", "jpeg", "png", "gif", "webp"],
                "video": ["mp4", "mov"],
                "max_image_size_mb": 5,
                "max_video_size_mb": 512,
            },
            "facebook": {
                "image": ["jpg", "jpeg", "png", "gif", "bmp"],
                "video": ["mp4", "mov", "avi"],
                "max_image_size_mb": 4,
                "max_video_size_mb": 4096,
            },
            "instagram": {
                "image": ["jpg", "jpeg", "png"],
                "video": ["mp4", "mov"],
                "max_image_size_mb": 8,
                "max_video_size_mb": 100,
                "aspect_ratios": ["1:1", "4:5", "1.91:1"],
            },
        }

        logger.info("✅ MediaHandler initialized")

    def validate_media(self, file_path: str, platform: str) -> dict[str, Any]:
        """Validate media file for platform requirements"""
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}

            # Get file extension
            ext = os.path.splitext(file_path)[1][1:].lower()

            # Check if platform is supported
            if platform not in self.platform_specs:
                return {"valid": False, "error": f"Platform '{platform}' not supported"}

            spec = self.platform_specs[platform]

            # Check file type
            if ext not in spec["image"] and ext not in spec["video"]:
                return {"valid": False, "error": f"File format '{ext}' not supported for {platform}"}

            # Check file size
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            media_type = "image" if ext in spec["image"] else "video"
            max_size_key = f"max_{media_type}_size_mb"

            if size_mb > spec[max_size_key]:
                return {"valid": False, "error": f"File too large: {size_mb:.2f}MB (max: {spec[max_size_key]}MB)"}

            return {"valid": True, "media_type": media_type, "format": ext, "size_mb": round(size_mb, 2)}

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {"valid": False, "error": str(e)}

    async def save_media(self, file_data: bytes, filename: str) -> dict[str, Any]:
        """Save media file to disk"""
        try:
            # Generate unique ID
            unique_id = hashlib.sha256(file_data).hexdigest()[:16]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Get extension
            ext = os.path.splitext(filename)[1].lower() or ".bin"
            stored_filename = f"{timestamp}_{unique_id}{ext}"
            file_path = self.media_dir / stored_filename

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_data)

            size_mb = len(file_data) / (1024 * 1024)
            self.stats["uploads"] += 1
            self.stats["total_size_bytes"] += len(file_data)

            media_type = "image" if ext[1:] in self.supported_images else "video"

            return {
                "status": "success",
                "media_id": unique_id,
                "filename": stored_filename,
                "path": str(file_path),
                "type": media_type,
                "format": ext[1:],
                "size_bytes": len(file_data),
                "size_mb": round(size_mb, 2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to save media: {e}")
            return {"status": "error", "error": str(e)}

    async def process_base64(self, base64_data: str, filename: str) -> dict[str, Any]:
        """Process base64 encoded media"""
        try:
            # Remove data URL prefix if present
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]

            file_data = base64.b64decode(base64_data)
            return await self.save_media(file_data, filename)

        except Exception as e:
            logger.error(f"Failed to process base64: {e}")
            return {"status": "error", "error": str(e)}

    async def get_media(self, media_id: str) -> dict[str, Any] | None:
        """Retrieve media information"""
        try:
            # Search for file with media_id in name
            for file_path in self.media_dir.glob(f"*{media_id}*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    ext = file_path.suffix[1:]

                    return {
                        "media_id": media_id,
                        "filename": file_path.name,
                        "path": str(file_path),
                        "type": "image" if ext in self.supported_images else "video",
                        "format": ext,
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }

            return None

        except Exception as e:
            logger.error(f"Failed to get media: {e}")
            return None

    async def delete_media(self, media_id: str) -> dict[str, Any]:
        """Delete media file"""
        try:
            # Search and delete file
            for file_path in self.media_dir.glob(f"*{media_id}*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Deleted media: {media_id}")
                    return {"status": "success", "media_id": media_id, "deleted": True}

            return {"status": "error", "error": "Media not found"}

        except Exception as e:
            logger.error(f"Failed to delete media: {e}")
            return {"status": "error", "error": str(e)}

    async def resize_image(self, media_id: str, width: int, height: int) -> dict[str, Any]:
        """Resize image (placeholder - requires PIL/Pillow)"""
        try:
            media = await self.get_media(media_id)
            if not media:
                return {"status": "error", "error": "Media not found"}

            if media["type"] != "image":
                return {"status": "error", "error": "Can only resize images"}

            # TODO: Implement actual resizing with PIL/Pillow
            logger.warning("Image resizing not yet implemented - requires PIL/Pillow")

            return {
                "status": "success",
                "media_id": media_id,
                "message": "Resize operation queued (not yet implemented)",
                "target_size": f"{width}x{height}",
            }

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return {"status": "error", "error": str(e)}

    def get_stats(self) -> dict[str, Any]:
        """Get media handler statistics"""
        return {
            "uploads": self.stats["uploads"],
            "total_size_mb": round(self.stats["total_size_bytes"] / (1024 * 1024), 2),
            "media_directory": str(self.media_dir),
            "supported_images": self.supported_images,
            "supported_videos": self.supported_videos,
            "platforms": list(self.platform_specs.keys()),
        }
