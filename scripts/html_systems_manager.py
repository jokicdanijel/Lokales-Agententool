#!/usr/bin/env python3
"""
HTML Systems Management Script
Koordination aller HTML-bezogenen Workflows über opena21 Workflow Engine

Verwendung:
    python3 html_systems_manager.py discover     # Entdecke alle HTML-Systeme
    python3 html_systems_manager.py assess      # Bewerte HTML-Qualität
    python3 html_systems_manager.py optimize    # Optimiere HTML-Systeme
    python3 html_systems_manager.py deploy      # Deploye neue HTML-Systeme
    python3 html_systems_manager.py monitor     # Setup Monitoring & Maintenance
    python3 html_systems_manager.py integrate   # Vollständige Integration
    python3 html_systems_manager.py full-cycle  # Kompletter Workflow
"""

import asyncio
import os
import sys
from typing import Any

import httpx

# Konfiguration - ELION Hyper-Dashboard 2.0 kompatibel
WORKFLOW_ENGINE_URL = "http://127.0.0.1:12363"  # opena21 auf korrektem Port
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-faf8-485b-afa4-078357cf5313")  # Fallback Token
DASHBOARD_URL = "http://127.0.0.1:12349"  # opena20 Dashboard

# HTML Workflow Definitionen - ELION Hyper-Dashboard 2.0 kompatibel
HTML_WORKFLOWS = {
    "discover": {
        "name": "html_systems_discovery",
        "description": "🔍 Entdeckung aller online HTML-Systeme",
        "estimated_duration": "2 Minuten",
        "agents_involved": ["opena6", "opena17", "opena18"],
        "endpoint": "/api/workflows/html-systems-discovery",
    },
    "assess": {
        "name": "html_quality_assessment",
        "description": "📊 Bewertung aller HTML-Systeme",
        "estimated_duration": "3 Minuten",
        "agents_involved": ["opena6", "opena17", "opena20"],
        "endpoint": "/api/workflows/html-quality-assessment",
    },
    "optimize": {
        "name": "html_system_optimization",
        "description": "⚡ Automatische Verbesserung der HTML-Systeme",
        "estimated_duration": "3 Minuten",
        "agents_involved": ["opena17", "opena6", "opena20"],
        "endpoint": "/api/workflows/html-system-optimization",
    },
    "deploy": {
        "name": "html_deployment_pipeline",
        "description": "🚀 Erstellung und Deployment neuer HTML-Systeme",
        "estimated_duration": "3.5 Minuten",
        "agents_involved": ["opena17", "opena18", "opena20", "opena6"],
        "endpoint": "/api/workflows/html-deployment-pipeline",
    },
    "monitor": {
        "name": "html_monitoring_maintenance",
        "description": "🔧 Kontinuierliche Überwachung und Wartung",
        "estimated_duration": "2 Minuten",
        "agents_involved": ["opena20", "opena6", "opena17"],
        "endpoint": "/api/workflows/html-monitoring-maintenance",
    },
    "integrate": {
        "name": "html_integration_orchestration",
        "description": "🔗 Vollständige System-Integration",
        "estimated_duration": "4 Minuten",
        "agents_involved": ["opena18", "opena17", "opena20", "opena6"],
        "endpoint": "/api/workflows/html-integration-orchestration",
    },
    "self-cleaning": {
        "name": "html_self_cleaning_integration",
        "description": "🧹 Self-Cleaning System Integration",
        "estimated_duration": "2 Minuten",
        "agents_involved": ["opena20"],
        "endpoint": "/api/self_cleaning/status",
    },
}


class HTMLSystemsManager:
    """Manager für alle HTML-System Workflows - ELION Hyper-Dashboard 2.0 Integration"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
        self.headers = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}
        self.dashboard_healthy = False
        self.self_cleaning_healthy = False

    async def check_system_health(self) -> dict[str, bool]:
        """Prüfe Verfügbarkeit aller System-Komponenten"""
        health_status = {"dashboard": False, "self_cleaning": False, "workflow_engine": False}

        # Dashboard Health Check
        try:
            response = await self.client.get(f"{DASHBOARD_URL}/health")
            health_status["dashboard"] = response.status_code == 200
            self.dashboard_healthy = health_status["dashboard"]
        except Exception as e:
            print(f"❌ Dashboard nicht erreichbar: {e}")

        # Self-Cleaning System Health Check
        try:
            response = await self.client.get(f"{DASHBOARD_URL}/api/self_cleaning/health", headers=self.headers)
            health_status["self_cleaning"] = response.status_code == 200
            self.self_cleaning_healthy = health_status["self_cleaning"]
        except Exception as e:
            print(f"❌ Self-Cleaning System nicht erreichbar: {e}")

        # Workflow Engine Health Check (falls verfügbar)
        try:
            response = await self.client.get(f"{WORKFLOW_ENGINE_URL}/health")
            health_status["workflow_engine"] = response.status_code == 200
        except Exception as e:
            print(f"❌ Workflow Engine nicht erreichbar: {e}")

        return health_status

    async def list_available_workflows(self) -> list[dict[str, Any]]:
        """Liste alle verfügbaren HTML-Workflows"""
        try:
            response = await self.client.get(f"{WORKFLOW_ENGINE_URL}/workflows/list", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                html_workflows = [w for w in data.get("workflows", []) if w["name"].startswith("html_")]
                return html_workflows
            return []
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Workflows: {e}")
            return []

    async def execute_workflow(self, workflow_name: str, inputs: dict[str, Any] = None) -> dict[str, Any]:
        """Führe einen HTML-Workflow über Dashboard-API aus"""
        if workflow_name not in HTML_WORKFLOWS:
            raise ValueError(f"Unbekannter Workflow: {workflow_name}")

        workflow_config = HTML_WORKFLOWS[workflow_name]

        print(f"🚀 Starte Workflow: {workflow_config['description']}")
        print(f"⏱️  Geschätzte Dauer: {workflow_config['estimated_duration']}")
        print(f"🤖 Beteiligte Agenten: {', '.join(workflow_config['agents_involved'])}")
        print()

        # Self-Cleaning Workflow - direkt über Self-Cleaning API
        if workflow_name == "self-cleaning":
            return await self._execute_self_cleaning_workflow()

        # Andere Workflows über Dashboard API
        endpoint = workflow_config.get("endpoint", f"/api/workflows/{workflow_name}")
        payload = {
            "workflow_name": workflow_config["name"],
            "inputs": inputs or {},
            "mode": "sync",
            "agents": workflow_config["agents_involved"],
        }

        try:
            # Versuche Dashboard API zuerst
            response = await self.client.post(f"{DASHBOARD_URL}{endpoint}", headers=self.headers, json=payload)

            if response.status_code == 200:
                result = response.json()

                print("✅ Workflow erfolgreich über Dashboard API")
                print(f"📊 Status: {result.get('status', 'unknown')}")
                print(f"🔄 Workflow ID: {result.get('workflow_id', 'N/A')}")

                return result
            else:
                # Fallback: Direkte Workflow Engine (falls verfügbar)
                return await self._fallback_workflow_execution(workflow_config, payload)

        except Exception as e:
            print(f"❌ Fehler bei Workflow-Ausführung: {e}")
            return {"error": str(e)}

    async def _execute_self_cleaning_workflow(self) -> dict[str, Any]:
        """Führe Self-Cleaning Workflow aus"""
        try:
            # Self-Cleaning Status abrufen
            status_response = await self.client.get(f"{DASHBOARD_URL}/api/self_cleaning/status", headers=self.headers)

            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Self-Cleaning Status: {status_data.get('status', 'unknown')}")
                print(f"📊 Health Score: {status_data.get('health_score', 'N/A')}")

                # Trigger Scan wenn nötig
                if status_data.get("health_score", 0) < 80:
                    scan_response = await self.client.post(
                        f"{DASHBOARD_URL}/api/self_cleaning/scan", headers=self.headers
                    )
                    if scan_response.status_code == 200:
                        print("🔍 System-Scan gestartet")

                return status_data
            else:
                return {"error": f"Self-Cleaning API HTTP {status_response.status_code}"}

        except Exception as e:
            return {"error": f"Self-Cleaning Workflow Fehler: {e}"}

    async def _fallback_workflow_execution(
        self, workflow_config: dict[str, Any], payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Fallback: Direkte Workflow Engine Execution"""
        try:
            response = await self.client.post(
                f"{WORKFLOW_ENGINE_URL}/workflows/execute", headers=self.headers, json=payload
            )

            if response.status_code == 200:
                result = response.json()
                execution_result = result.get("execution", {})

                print("✅ Workflow erfolgreich über Workflow Engine")
                print(f"📊 Status: {execution_result.get('state', 'unknown')}")
                print(f"🔄 Steps abgeschlossen: {execution_result.get('steps_completed', 0)}")

                return execution_result
            else:
                print(f"❌ Workflow fehlgeschlagen: HTTP {response.status_code}")
                return {"error": response.text}

        except Exception as e:
            print(f"❌ Fallback Workflow-Ausführung fehlgeschlagen: {e}")
            return {"error": str(e)}

    async def monitor_workflow_execution(self, workflow_id: str) -> dict[str, Any]:
        """Überwache die Ausführung eines Workflows"""
        try:
            response = await self.client.get(f"{WORKFLOW_ENGINE_URL}/workflows/{workflow_id}", headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    async def get_workflow_statistics(self) -> dict[str, Any]:
        """Hole Statistiken für HTML-Workflows"""
        try:
            response = await self.client.get(f"{WORKFLOW_ENGINE_URL}/workflows/executions", headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                html_executions = [
                    ex for ex in data.get("executions", []) if ex.get("workflow_name", "").startswith("html_")
                ]

                stats = {
                    "total_html_workflows": len(html_executions),
                    "successful": len([ex for ex in html_executions if ex.get("state") == "completed"]),
                    "failed": len([ex for ex in html_executions if ex.get("state") == "failed"]),
                    "recent_executions": html_executions[-5:] if html_executions else [],
                }

                return stats
            return {}

        except Exception as e:
            return {"error": str(e)}

    async def run_full_html_cycle(self) -> list[dict[str, Any]]:
        """Führe den kompletten HTML-Management-Zyklus aus"""
        print("🔄 Starte vollständigen HTML-Management-Zyklus...")
        print("=" * 60)

        results = []
        workflow_sequence = ["discover", "assess", "optimize", "deploy", "monitor", "integrate"]

        for i, workflow in enumerate(workflow_sequence, 1):
            print(f"\n📋 Phase {i}/{len(workflow_sequence)}: {workflow}")
            print("-" * 40)

            result = await self.execute_workflow(workflow)
            results.append({"phase": i, "workflow": workflow, "result": result})

            # Kurze Pause zwischen Workflows
            if i < len(workflow_sequence):
                print("⏸️  Kurze Pause vor nächster Phase...")
                await asyncio.sleep(5)

        print("\n" + "=" * 60)
        print("🎉 Vollständiger HTML-Management-Zyklus abgeschlossen!")

        # Zusammenfassung
        successful = len([r for r in results if "error" not in r["result"]])
        print(f"📊 Erfolgreiche Phasen: {successful}/{len(results)}")

        return results

    def print_usage_help(self):
        """Drucke Hilfe zur Verwendung"""
        print("🌐 HTML Systems Management")
        print("=" * 40)
        print("Verfügbare Kommandos:")
        print()

        for cmd, config in HTML_WORKFLOWS.items():
            print(f"  {cmd:<12} - {config['description']}")
            print(f"  {'':>12}   Dauer: {config['estimated_duration']}")
            print(f"  {'':>12}   Agenten: {', '.join(config['agents_involved'])}")
            print()

        print("  self-cleaning - Self-Cleaning System Integration")
        print("  full-cycle   - Führe alle Workflows nacheinander aus")
        print("  status       - Zeige Workflow-Statistiken")
        print("  help         - Zeige diese Hilfe")
        print()
        print("Beispiele:")
        print("  python3 html_systems_manager.py discover")
        print("  python3 html_systems_manager.py self-cleaning")
        print("  python3 html_systems_manager.py full-cycle")


async def main():
    """Hauptfunktion"""
    manager = HTMLSystemsManager()

    # Prüfe System-Verfügbarkeit
    health_status = await manager.check_system_health()

    print("🏥 System Health Check:")
    for component, status in health_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component}: {'OK' if status else 'OFFLINE'}")
    print()

    if not health_status["dashboard"]:
        print("❌ Dashboard ist nicht verfügbar!")
        print("💡 Starte das System mit: bin/ops.sh start")
        return 1

    # Kommandozeilen-Argument verarbeiten
    if len(sys.argv) < 2:
        manager.print_usage_help()
        return 0

    command = sys.argv[1].lower()

    try:
        if command == "help":
            manager.print_usage_help()

        elif command == "status":
            print("📊 HTML Workflow Statistiken")
            print("-" * 30)
            stats = await manager.get_workflow_statistics()

            if "error" in stats:
                print(f"❌ Fehler: {stats['error']}")
            else:
                print(f"Gesamt HTML-Workflows: {stats.get('total_html_workflows', 0)}")
                print(f"Erfolgreich: {stats.get('successful', 0)}")
                print(f"Fehlgeschlagen: {stats.get('failed', 0)}")

                recent = stats.get("recent_executions", [])
                if recent:
                    print(f"\nLetzte {len(recent)} Ausführungen:")
                    for ex in recent:
                        print(f"  - {ex.get('workflow_name', 'N/A')}: {ex.get('state', 'unknown')}")

        elif command == "full-cycle":
            results = await manager.run_full_html_cycle()

            # Detaillierte Zusammenfassung
            print("\n📋 Detaillierte Ergebnisse:")
            for result in results:
                status = "✅ Erfolg" if "error" not in result["result"] else "❌ Fehler"
                print(f"  Phase {result['phase']} ({result['workflow']}): {status}")

        elif command in HTML_WORKFLOWS:
            await manager.execute_workflow(command)

        else:
            print(f"❌ Unbekanntes Kommando: {command}")
            manager.print_usage_help()
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Abgebrochen durch Benutzer")
        return 1
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1
    finally:
        await manager.client.aclose()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
