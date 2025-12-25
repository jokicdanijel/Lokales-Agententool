# 📱 Social Core Module - PORTIER PAS-6.0
# Central Social Media Operations Engine

import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Platform character limits
PLATFORM_LIMITS = {"linkedin": 3000, "x": 280, "twitter": 280, "facebook": 63206, "instagram": 2200}


class SocialCore:
    """Core Social Media Engine"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY_OPENA12", os.getenv("OPENAI_API_KEY", ""))
        self._logs: list[dict[str, Any]] = []

        # Initialize platform engines
        self.engines: dict[str, Any] = {}
        self._init_platforms()

        logger.info("✅ SocialCore initialized")

    def _init_platforms(self):
        """Initialize platform engines"""
        try:
            from .platform_facebook import FacebookPlatform
            from .platform_instagram import InstagramPlatform
            from .platform_linkedin import LinkedInPlatform
            from .platform_x import XPlatform

            self.engines = {
                "linkedin": LinkedInPlatform(),
                "x": XPlatform(),
                "facebook": FacebookPlatform(),
                "instagram": InstagramPlatform(),
            }
        except ImportError as e:
            logger.warning(f"Platform import warning: {e}")
            # Create mock engines
            self.engines = {
                "linkedin": MockPlatform("linkedin"),
                "x": MockPlatform("x"),
                "facebook": MockPlatform("facebook"),
                "instagram": MockPlatform("instagram"),
            }

    def platforms(self) -> list[str]:
        """Get list of supported platforms"""
        return list(self.engines.keys())

    def platforms_info(self) -> list[dict[str, Any]]:
        """Get detailed platform info"""
        return [
            {"name": name, "character_limit": PLATFORM_LIMITS.get(name, 0), "status": "connected"}
            for name in self.engines.keys()
        ]

    def get_limit(self, platform: str) -> int:
        """Get character limit for platform"""
        return PLATFORM_LIMITS.get(platform.lower(), 0)

    def get_all_limits(self) -> dict[str, int]:
        """Get all character limits"""
        return PLATFORM_LIMITS.copy()

    async def post_now(
        self, platforms: list[str], text: str, hashtags: list[str] | None = None, media: list[str] | None = None
    ) -> dict[str, Any]:
        """Post immediately to specified platforms"""

        if not platforms:
            return {"status": "error", "message": "No platforms specified"}

        if not text:
            return {"status": "error", "message": "No text provided"}

        results = {}
        errors = {}

        # Add hashtags to text if provided
        full_text = text
        if hashtags:
            hashtag_str = " " + " ".join(f"#{tag}" for tag in hashtags)
            full_text = text + hashtag_str

        for platform in platforms:
            engine = self.engines.get(platform.lower())

            if not engine:
                errors[platform] = "Platform not supported"
                continue

            # Check character limit
            limit = PLATFORM_LIMITS.get(platform.lower(), 0)
            if limit > 0 and len(full_text) > limit:
                errors[platform] = f"Text exceeds {limit} character limit ({len(full_text)})"
                continue

            try:
                result = await engine.publish(full_text, hashtags, media)
                results[platform] = result
            except Exception as e:
                logger.error(f"Error posting to {platform}: {e}")
                errors[platform] = str(e)

        # Log the operation
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "post",
            "platforms": platforms,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "results": results,
            "errors": errors,
        }
        self._logs.append(log_entry)

        # Keep only last 100 logs
        if len(self._logs) > 100:
            self._logs = self._logs[-100:]

        return {
            "status": "success" if results else "failed",
            "posted_to": list(results.keys()),
            "results": results,
            "errors": errors if errors else None,
            "timestamp": datetime.now().isoformat(),
        }

    async def generate_text(self, topic: str) -> dict[str, Any]:
        """Generate post text using AI"""
        if not self.openai_api_key:
            # Mock response without API
            return {
                "status": "success",
                "generated_text": f"🎯 {topic}\n\nDies ist ein automatisch generierter Beitrag zum Thema '{topic}'. Unser Team arbeitet ständig an innovativen Lösungen.\n\n#Innovation #Digital #Business",
                "model": "mock",
                "topic": topic,
            }

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.openai_api_key)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Social Media Experte. Erstelle professionelle, ansprechende Posts für Business-Netzwerke. Halte den Text prägnant und füge relevante Hashtags hinzu.",
                    },
                    {"role": "user", "content": f"Erstelle einen Social Media Post zum Thema: {topic}"},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            generated = response.choices[0].message.content

            return {
                "status": "success",
                "generated_text": generated,
                "model": "gpt-4o-mini",
                "topic": topic,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
            }

        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return {"status": "error", "message": str(e), "topic": topic}

    async def generate_hashtags(self, topic: str) -> dict[str, Any]:
        """Generate relevant hashtags for a topic"""
        if not self.openai_api_key:
            # Mock hashtags
            return {
                "status": "success",
                "hashtags": ["Business", "Innovation", "Digital", "Tech", "Growth"],
                "topic": topic,
            }

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.openai_api_key)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Du generierst relevante Hashtags für Social Media Posts. Gib nur die Hashtags zurück, ohne # davor, getrennt durch Kommas.",
                    },
                    {"role": "user", "content": f"Generiere 5-10 relevante Hashtags für: {topic}"},
                ],
                max_tokens=100,
                temperature=0.5,
            )

            hashtag_text = response.choices[0].message.content
            hashtags = [h.strip().replace("#", "") for h in hashtag_text.split(",")]

            return {"status": "success", "hashtags": hashtags, "topic": topic}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def optimize_post(self, text: str, platform: str) -> dict[str, Any]:
        """Optimize post for specific platform"""
        limit = PLATFORM_LIMITS.get(platform.lower(), 0)

        if not self.openai_api_key:
            # Simple truncation
            if limit > 0 and len(text) > limit:
                return {
                    "status": "success",
                    "optimized_text": text[: limit - 3] + "...",
                    "original_length": len(text),
                    "optimized_length": limit,
                    "platform": platform,
                }
            return {"status": "success", "optimized_text": text, "original_length": len(text), "platform": platform}

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.openai_api_key)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"Optimiere den folgenden Text für {platform}. Maximale Länge: {limit} Zeichen. Behalte die Kernaussage bei.",
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=limit // 2,
            )

            optimized = response.choices[0].message.content

            return {
                "status": "success",
                "optimized_text": optimized,
                "original_length": len(text),
                "optimized_length": len(optimized),
                "platform": platform,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def analyze_engagement(self, post_id: str | None = None) -> dict[str, Any]:
        """Analyze engagement (mock implementation)"""
        return {
            "status": "success",
            "post_id": post_id or "mock",
            "engagement": {"likes": 42, "comments": 7, "shares": 3, "impressions": 1250, "engagement_rate": 4.16},
            "note": "Mock data - connect real APIs for actual metrics",
        }

    def logs(self) -> list[dict[str, Any]]:
        """Get recent activity logs"""
        return self._logs[-20:]


class MockPlatform:
    """Mock platform for testing"""

    def __init__(self, name: str):
        self.name = name

    async def publish(
        self, text: str, hashtags: list[str] | None = None, media: list[str] | None = None
    ) -> dict[str, Any]:
        return {
            "platform": self.name,
            "status": "posted",
            "url": f"https://{self.name}.com/post/mock123",
            "text_length": len(text),
            "hashtags": hashtags or [],
            "media_uploaded": bool(media),
            "timestamp": datetime.now().isoformat(),
        }
