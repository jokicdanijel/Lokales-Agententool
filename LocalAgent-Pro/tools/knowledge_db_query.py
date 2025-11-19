#!/usr/bin/env python3
"""
LocalAgent-Pro Knowledge DB Query Tool für opena1 (ELION Koordinator)

Dieses Tool ermöglicht opena1, die LocalAgent-Pro Knowledge DB abzufragen,
um Runtime-Status, Konfigurationen und Quick-Check-Commands zu erhalten.

Verwendung:
    from tools.knowledge_db_query import KnowledgeDBQuery
    
    kb = KnowledgeDBQuery()
    status = kb.get_runtime_status()
    metrics = kb.get_metrics_count()
    health_cmd = kb.get_quick_check_command('health_check')
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


class KnowledgeDBQuery:
    """Query-Interface für LocalAgent-Pro Knowledge Database."""
    
    def __init__(self, knowledge_db_path: Optional[Path] = None):
        """
        Initialisiert Knowledge DB Query Tool.
        
        Args:
            knowledge_db_path: Pfad zur JSON-Datei (default: auto-detect)
        """
        if knowledge_db_path:
            self.db_path = Path(knowledge_db_path)
        else:
            # Auto-detect: Suche config/localagent_knowledge_db.json
            script_dir = Path(__file__).parent.resolve()
            repo_root = script_dir.parent
            self.db_path = repo_root / "config" / "localagent_knowledge_db.json"
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Knowledge DB not found: {self.db_path}")
        
        self.data = self._load_db()
    
    def _load_db(self) -> Dict[str, Any]:
        """Lädt Knowledge DB aus JSON-Datei."""
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def reload(self) -> None:
        """Lädt Knowledge DB neu (für Live-Updates)."""
        self.data = self._load_db()
    
    # ========== Runtime-Queries ==========
    
    def get_runtime_status(self) -> str:
        """Gibt aktuellen Runtime-Status zurück (ok/error/unknown)."""
        return self.data.get("localagent_pro", {}).get("runtime", {}).get("status", "unknown")
    
    def get_model(self) -> str:
        """Gibt verwendetes LLM-Modell zurück."""
        return self.data.get("localagent_pro", {}).get("runtime", {}).get("model", "unknown")
    
    def is_sandbox_enabled(self) -> bool:
        """Prüft, ob Sandbox-Modus aktiv ist."""
        return self.data.get("localagent_pro", {}).get("runtime", {}).get("sandbox_enabled", False)
    
    def get_sandbox_path(self) -> str:
        """Gibt Sandbox-Pfad zurück."""
        return self.data.get("localagent_pro", {}).get("runtime", {}).get("sandbox_path", "")
    
    def get_health_raw(self) -> Dict[str, Any]:
        """Gibt kompletten Health-Response zurück."""
        return self.data.get("localagent_pro", {}).get("runtime", {}).get("health_raw", {})
    
    # ========== Config-Queries ==========
    
    def get_config_files(self) -> List[Dict[str, str]]:
        """Gibt Liste aller Config-Dateien zurück."""
        return self.data.get("localagent_pro", {}).get("config_files", [])
    
    def get_config_file_by_role(self, role: str) -> Optional[Dict[str, str]]:
        """
        Findet Config-Datei nach Rolle.
        
        Args:
            role: z.B. 'primary_runtime_config', 'grafana_dashboard', etc.
        
        Returns:
            Dict mit path, role, description oder None
        """
        configs = self.get_config_files()
        for config in configs:
            if config.get("role") == role:
                return config
        return None
    
    # ========== Monitoring-Queries ==========
    
    def get_metrics_endpoint(self) -> str:
        """Gibt Metrics-Endpoint URL zurück."""
        return self.data.get("localagent_pro", {}).get("monitoring", {}).get("metrics_endpoint", "")
    
    def get_metrics_count(self) -> int:
        """Gibt Anzahl verfügbarer Metriken zurück."""
        return self.data.get("localagent_pro", {}).get("monitoring", {}).get("metrics_count_observed", 0)
    
    def get_prometheus_job_name(self) -> str:
        """Gibt Prometheus Job-Name zurück."""
        return self.data.get("localagent_pro", {}).get("monitoring", {}).get("prometheus", {}).get("job_name", "")
    
    def get_prometheus_target_status(self) -> str:
        """Gibt Prometheus Target Health zurück (up/down/unknown)."""
        return self.data.get("localagent_pro", {}).get("monitoring", {}).get("prometheus", {}).get("target_status", "unknown")
    
    def is_prometheus_healthy(self) -> bool:
        """Prüft, ob Prometheus Target 'up' ist."""
        return self.get_prometheus_target_status() == "up"
    
    # ========== ELION Integration Queries ==========
    
    def get_agent_id(self) -> str:
        """Gibt ELION Agent-ID zurück (opena21)."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("agent_id", "")
    
    def get_agent_port(self) -> int:
        """Gibt ELION Agent-Port zurück (12364)."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("port", 0)
    
    def get_upstream_endpoint(self) -> str:
        """Gibt LocalAgent-Pro API-Endpoint zurück."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("upstream_endpoint", "")
    
    def get_coordinator(self) -> str:
        """Gibt ELION Koordinator zurück (opena1)."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("orchestration", {}).get("coordinator", "")
    
    def get_archivator(self) -> str:
        """Gibt ELION Archivator zurück (opena2)."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("orchestration", {}).get("archivator", "")
    
    def writes_safepoints_directly(self) -> bool:
        """Prüft, ob LocalAgent-Pro direkt Safepoints schreibt (sollte False sein)."""
        return self.data.get("localagent_pro", {}).get("integration", {}).get("elion", {}).get("safety_model", {}).get("writes_safepoints_directly", False)
    
    # ========== Quick-Check Commands ==========
    
    def get_quick_check_command(self, check_type: str) -> Optional[str]:
        """
        Gibt Quick-Check Command zurück.
        
        Args:
            check_type: 'health_check', 'metrics_count', 'prometheus_health', 'process_check'
        
        Returns:
            Shell-Command als String oder None
        """
        cmd_map = {
            "health_check": "health_check_cmd",
            "metrics_count": "metrics_count_cmd",
            "prometheus_health": "prometheus_health_cmd",
            "process_check": "process_check_cmd"
        }
        
        cmd_key = cmd_map.get(check_type)
        if cmd_key:
            return self.data.get("localagent_pro", {}).get("quick_checks", {}).get(cmd_key)
        return None
    
    def run_quick_check(self, check_type: str, timeout: int = 10) -> Optional[str]:
        """
        Führt Quick-Check Command aus und gibt Output zurück.
        
        Args:
            check_type: 'health_check', 'metrics_count', 'prometheus_health', 'process_check'
            timeout: Timeout in Sekunden
        
        Returns:
            Command-Output oder None bei Fehler
        """
        cmd = self.get_quick_check_command(check_type)
        if not cmd:
            return None
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    # ========== Utility Methods ==========
    
    def get_full_data(self) -> Dict[str, Any]:
        """Gibt komplette Knowledge DB zurück."""
        return self.data
    
    def to_json(self, indent: int = 2) -> str:
        """Exportiert Knowledge DB als formatierten JSON-String."""
        return json.dumps(self.data, indent=indent, ensure_ascii=False)
    
    def validate(self) -> Dict[str, bool]:
        """
        Validiert Knowledge DB Schema.
        
        Returns:
            Dict mit Validierungs-Ergebnissen für jede Sektion
        """
        validation = {
            "runtime": "runtime" in self.data.get("localagent_pro", {}),
            "config_files": "config_files" in self.data.get("localagent_pro", {}),
            "monitoring": "monitoring" in self.data.get("localagent_pro", {}),
            "integration": "integration" in self.data.get("localagent_pro", {}),
            "quick_checks": "quick_checks" in self.data.get("localagent_pro", {}),
            "meta": "meta" in self.data.get("localagent_pro", {})
        }
        
        validation["all_valid"] = all(validation.values())
        return validation


# ========== CLI Interface (für direkte Nutzung) ==========

def main():
    """CLI-Interface für Knowledge DB Query Tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query LocalAgent-Pro Knowledge DB")
    parser.add_argument("--status", action="store_true", help="Get runtime status")
    parser.add_argument("--model", action="store_true", help="Get LLM model")
    parser.add_argument("--sandbox", action="store_true", help="Check if sandbox is enabled")
    parser.add_argument("--metrics", action="store_true", help="Get metrics count")
    parser.add_argument("--prometheus", action="store_true", help="Get Prometheus target status")
    parser.add_argument("--agent-id", action="store_true", help="Get ELION agent ID")
    parser.add_argument("--coordinator", action="store_true", help="Get ELION coordinator")
    parser.add_argument("--quick-check", choices=["health_check", "metrics_count", "prometheus_health", "process_check"], help="Run quick check command")
    parser.add_argument("--validate", action="store_true", help="Validate Knowledge DB schema")
    parser.add_argument("--json", action="store_true", help="Output full DB as JSON")
    
    args = parser.parse_args()
    
    try:
        kb = KnowledgeDBQuery()
        
        if args.status:
            print(f"Runtime Status: {kb.get_runtime_status()}")
        
        if args.model:
            print(f"Model: {kb.get_model()}")
        
        if args.sandbox:
            print(f"Sandbox Enabled: {kb.is_sandbox_enabled()}")
            print(f"Sandbox Path: {kb.get_sandbox_path()}")
        
        if args.metrics:
            print(f"Metrics Count: {kb.get_metrics_count()}")
        
        if args.prometheus:
            status = kb.get_prometheus_target_status()
            healthy = "✅" if kb.is_prometheus_healthy() else "❌"
            print(f"Prometheus Target: {status} {healthy}")
        
        if args.agent_id:
            print(f"ELION Agent ID: {kb.get_agent_id()}")
            print(f"ELION Port: {kb.get_agent_port()}")
        
        if args.coordinator:
            print(f"Coordinator: {kb.get_coordinator()}")
            print(f"Archivator: {kb.get_archivator()}")
        
        if args.quick_check:
            print(f"Running {args.quick_check}...")
            output = kb.run_quick_check(args.quick_check)
            if output:
                print(output)
            else:
                print("⚠️ Check failed or timed out")
        
        if args.validate:
            validation = kb.validate()
            print("Knowledge DB Validation:")
            for key, valid in validation.items():
                status = "✅" if valid else "❌"
                print(f"  {status} {key}")
        
        if args.json:
            print(kb.to_json())
        
        # Wenn keine Argumente: Zeige Zusammenfassung
        if not any(vars(args).values()):
            print("LocalAgent-Pro Knowledge DB Summary:")
            print(f"  Status: {kb.get_runtime_status()}")
            print(f"  Model: {kb.get_model()}")
            print(f"  Sandbox: {kb.is_sandbox_enabled()}")
            print(f"  Metrics: {kb.get_metrics_count()}")
            print(f"  Prometheus: {kb.get_prometheus_target_status()}")
            print(f"  Agent: {kb.get_agent_id()} (Port {kb.get_agent_port()})")
            print(f"\nUse --help for more options")
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
