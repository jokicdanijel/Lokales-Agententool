# 🤖 AI Unlock Engine - PORTIER PAS-6.0
# OpenAI-powered Security Analysis for Unlock Master

import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class AIUnlockEngine:
    """
    AI-powered security analysis engine

    Features:
    - Permission structure analysis
    - Security recommendations
    - Anomaly detection
    - Permission suggestions
    """

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY_OPENA11", os.getenv("OPENAI_API_KEY", ""))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None

        # Statistics
        self.stats = {"analyses_completed": 0, "recommendations_generated": 0, "last_analysis": None}

    async def initialize(self):
        """Initialize OpenAI client"""
        if self.openai_api_key:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.openai_api_key)
                logger.info("✅ AI Unlock Engine initialized with OpenAI")
            except ImportError:
                logger.warning("⚠️ OpenAI library not installed")
        else:
            logger.warning("⚠️ OpenAI API key not configured - using mock mode")

    def is_connected(self) -> bool:
        """Check if AI engine is connected"""
        return self.client is not None

    async def analyze_permissions(self, permissions: dict[str, list], query: str = None) -> dict[str, Any]:
        """
        Analyze permission structure with AI

        Args:
            permissions: Current permission data
            query: Optional specific analysis query

        Returns:
            Analysis result
        """
        self.stats["last_analysis"] = datetime.now().isoformat()

        # Build analysis prompt
        perm_summary = self._summarize_permissions(permissions)

        prompt = f"""Analysiere die folgende RBAC-Berechtigungsstruktur:

{perm_summary}

{f'Spezifische Frage: {query}' if query else 'Gib eine allgemeine Sicherheitsanalyse.'}

Berücksichtige:
1. Übermäßig breite Berechtigungen (Wildcards)
2. Potenzielle Privilege Escalation Pfade
3. Least Privilege Prinzip Verletzungen
4. Empfehlungen zur Verbesserung

Antworte auf Deutsch in strukturierter Form."""

        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Du bist ein Sicherheitsexperte für RBAC-Systeme."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=1500,
                )

                self.stats["analyses_completed"] += 1

                return {
                    "status": "success",
                    "analysis": response.choices[0].message.content,
                    "model": self.model,
                    "permissions_analyzed": len(permissions),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                return {"status": "error", "error": str(e)}

        # Mock response
        self.stats["analyses_completed"] += 1
        return {
            "status": "success",
            "analysis": self._mock_analysis(permissions),
            "model": "mock",
            "permissions_analyzed": len(permissions),
            "timestamp": datetime.now().isoformat(),
        }

    async def recommend_permissions(self, subject: str, context: str, current_permissions: list) -> dict[str, Any]:
        """
        Generate permission recommendations for a subject

        Args:
            subject: User or entity ID
            context: Context about the user's role/needs
            current_permissions: Existing permissions

        Returns:
            Recommendations
        """
        prompt = f"""Für den Benutzer "{subject}" mit folgendem Kontext:
{context}

Aktuelle Berechtigungen:
{current_permissions}

Empfehle sinnvolle Berechtigungen basierend auf dem Least Privilege Prinzip.
Format: JSON-Array mit {{resource, action, reason}}"""

        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Du bist ein RBAC-Experte. Antworte mit JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )

                self.stats["recommendations_generated"] += 1

                return {
                    "status": "success",
                    "recommendations": response.choices[0].message.content,
                    "subject": subject,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Recommendation generation failed: {e}")
                return {"status": "error", "error": str(e)}

        # Mock recommendations
        return {
            "status": "success",
            "recommendations": [
                {"resource": "/api/data", "action": "read", "reason": "Grundlegender Datenzugriff"},
                {"resource": "/api/profile", "action": "write", "reason": "Eigenes Profil bearbeiten"},
            ],
            "subject": subject,
            "model": "mock",
            "timestamp": datetime.now().isoformat(),
        }

    async def security_scan(self, permissions: dict[str, list]) -> dict[str, Any]:
        """
        Perform comprehensive security scan

        Args:
            permissions: All permissions

        Returns:
            Scan results with findings
        """
        findings = []
        risk_score = 0

        for subject, perms in permissions.items():
            for perm in perms:
                resource = perm.get("resource", "")
                action = perm.get("action", "")

                # Check for wildcard permissions
                if resource == "*":
                    findings.append(
                        {
                            "severity": "high",
                            "type": "wildcard_resource",
                            "subject": subject,
                            "description": f"Subject '{subject}' hat Zugriff auf ALLE Ressourcen",
                        }
                    )
                    risk_score += 30

                if action == "*":
                    findings.append(
                        {
                            "severity": "high",
                            "type": "wildcard_action",
                            "subject": subject,
                            "resource": resource,
                            "description": f"Subject '{subject}' hat ALLE Aktionen auf '{resource}'",
                        }
                    )
                    risk_score += 25

                # Check for admin permissions
                if action == "admin" or "/admin" in resource:
                    findings.append(
                        {
                            "severity": "medium",
                            "type": "admin_access",
                            "subject": subject,
                            "description": f"Subject '{subject}' hat Admin-Zugriff",
                        }
                    )
                    risk_score += 15

                # Check for expired permissions (should be cleaned)
                expires = perm.get("expires", 0)
                if expires > 0 and expires < datetime.now().timestamp():
                    findings.append(
                        {
                            "severity": "low",
                            "type": "expired_permission",
                            "subject": subject,
                            "description": "Abgelaufene Berechtigung sollte entfernt werden",
                        }
                    )
                    risk_score += 5

        # Normalize risk score (0-100)
        risk_score = min(100, risk_score)

        return {
            "status": "success",
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "findings_count": len(findings),
            "findings": findings,
            "recommendations": self._generate_recommendations(findings),
            "scanned_subjects": len(permissions),
            "scanned_permissions": sum(len(p) for p in permissions.values()),
            "timestamp": datetime.now().isoformat(),
        }

    def _summarize_permissions(self, permissions: dict[str, list]) -> str:
        """Create text summary of permissions"""
        lines = []
        for subject, perms in permissions.items():
            lines.append(f"\nSubject: {subject}")
            for perm in perms:
                lines.append(f"  - {perm.get('action', '?')} on {perm.get('resource', '?')}")
        return "\n".join(lines) if lines else "Keine Berechtigungen vorhanden."

    def _mock_analysis(self, permissions: dict) -> str:
        """Generate mock analysis"""
        subject_count = len(permissions)
        perm_count = sum(len(p) for p in permissions.values())

        return f"""## Sicherheitsanalyse

### Übersicht
- **Subjects:** {subject_count}
- **Berechtigungen:** {perm_count}

### Empfehlungen
1. Überprüfen Sie regelmäßig ungenutzte Berechtigungen
2. Vermeiden Sie Wildcard-Berechtigungen (*) wo möglich
3. Implementieren Sie zeitbasierte Berechtigungen für temporären Zugriff
4. Führen Sie regelmäßige Audits durch

### Nächste Schritte
- Least Privilege Prinzip anwenden
- Berechtigungsgruppen/Rollen definieren
- Audit-Logs regelmäßig prüfen"""

    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score"""
        if score < 20:
            return "low"
        elif score < 50:
            return "medium"
        elif score < 80:
            return "high"
        return "critical"

    def _generate_recommendations(self, findings: list) -> list[str]:
        """Generate recommendations from findings"""
        recs = set()

        for finding in findings:
            if finding["type"] == "wildcard_resource":
                recs.add("Ersetzen Sie Wildcard-Ressourcen durch spezifische Pfade")
            elif finding["type"] == "wildcard_action":
                recs.add("Beschränken Sie Aktionen auf das notwendige Minimum")
            elif finding["type"] == "admin_access":
                recs.add("Überprüfen Sie Admin-Berechtigungen auf Notwendigkeit")
            elif finding["type"] == "expired_permission":
                recs.add("Bereinigen Sie abgelaufene Berechtigungen")

        return list(recs)

    def get_stats(self) -> dict[str, Any]:
        """Get AI engine statistics"""
        return {
            "engine": "openai",
            "model": self.model,
            "connected": self.is_connected(),
            "statistics": self.stats.copy(),
        }
