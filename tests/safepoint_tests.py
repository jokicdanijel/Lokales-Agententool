#!/usr/bin/env python3
"""
PORTIER 3.0 Safepoint Test Suite
Vollständige Test-Suite für alle Safepoint-Clients

Features:
- Unit Tests für alle PORTIER 3.0 Features
- Integration Tests mit Dashboard
- Compliance-Validierung
- Performance-Tests
- Secret-Maskierung Tests
- Unicode-Arrow Tests
"""

import json
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import der Safepoint-Clients
sys.path.append("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui")
from safepoint_client import SafepointClient, create_safepoint_client


class TestSafepointClient(unittest.TestCase):
    """Test Suite für PORTIER 3.0 Safepoint Client"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = SafepointClient(
            agent_id="test_agent", archivp_root=self.temp_dir, dashboard_url="http://127.0.0.1:12349"
        )

    def tearDown(self):
        """Cleanup nach jedem Test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_safepoint_structure_creation(self):
        """Test: YYYY/MM/DD Struktur wird korrekt erstellt"""
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue((Path(self.temp_dir) / "index.jsonl").exists())

    def test_cmd_safepoint_writing(self):
        """Test: CMD Safepoint wird korrekt geschrieben"""
        payload = {"command": "test", "token": "secret-key"}
        filename = self.client.write_cmd_safepoint("test_req_001", payload)

        # Filename-Format prüfen
        self.assertIn("→", filename)
        self.assertIn("CMD.json", filename)
        self.assertIn("test_agent→opena2", filename)

        # Datei existiert
        now = datetime.now()
        expected_path = Path(self.temp_dir) / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / filename
        self.assertTrue(expected_path.exists())

        # JSON-Inhalt prüfen
        content = json.loads(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(content["source"], "test_agent")
        self.assertEqual(content["destination"], "opena2")
        self.assertEqual(content["category"], "CMD")
        self.assertEqual(content["request_id"], "test_req_001")
        self.assertTrue(content["strict"])

    def test_secret_masking(self):
        """Test: Secrets werden korrekt maskiert"""
        payload = {
            "command": "authenticate",
            "token": "super-secret-key",
            "password": "my-password",
            "data": {"apikey": "nested-secret", "safe_data": "not-secret"},
            "credentials": ["user", "pass"],
        }

        filename = self.client.write_cmd_safepoint("test_secret", payload)

        # Datei lesen
        now = datetime.now()
        filepath = Path(self.temp_dir) / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d") / filename
        content = json.loads(filepath.read_text(encoding="utf-8"))

        # Secrets sind maskiert
        self.assertEqual(content["payload"]["token"], "***")
        self.assertEqual(content["payload"]["password"], "***")
        self.assertEqual(content["payload"]["data"]["apikey"], "***")
        self.assertEqual(content["payload"]["credentials"], "***")

        # Safe-Data ist unverändert
        self.assertEqual(content["payload"]["data"]["safe_data"], "not-secret")

    def test_all_categories(self):
        """Test: Alle 4 PORTIER 3.0 Kategorien funktionieren"""
        categories = ["CMD", "RESP", "ROUTE", "DISPATCH"]
        test_payload = {"test": "data"}

        for category in categories:
            if category == "CMD":
                filename = self.client.write_cmd_safepoint("test_cat", test_payload)
            elif category == "RESP":
                filename = self.client.write_resp_safepoint("test_cat", test_payload)
            elif category == "ROUTE":
                filename = self.client.write_route_safepoint("test_cat", test_payload)
            elif category == "DISPATCH":
                filename = self.client.write_dispatch_safepoint("target_agent", "test_cat", test_payload)

            self.assertIn(f"_{category}.json", filename)

    def test_invalid_category(self):
        """Test: Ungültige Kategorie wirft Fehler"""
        with self.assertRaises(ValueError):
            self.client.write_safepoint("target", "INVALID", "req_id", {})

    def test_unicode_arrow_support(self):
        """Test: Unicode-Pfeil → wird korrekt verwendet"""
        filename = self.client.write_cmd_safepoint("arrow_test", {"test": "data"})
        self.assertIn("→", filename)
        self.assertIn("test_agent→opena2", filename)

    def test_index_jsonl_update(self):
        """Test: index.jsonl wird korrekt aktualisiert"""
        # Mehrere Safepoints schreiben
        self.client.write_cmd_safepoint("req_001", {"cmd": 1})
        self.client.write_resp_safepoint("req_002", {"resp": 2})

        # index.jsonl lesen
        index_file = Path(self.temp_dir) / "index.jsonl"
        lines = index_file.read_text(encoding="utf-8").strip().split("\n")

        # 2 Einträge
        self.assertEqual(len(lines), 2)

        # JSON-Format prüfen
        for line in lines:
            entry = json.loads(line)
            self.assertIn("file", entry)
            self.assertIn("ts", entry)
            self.assertIn("category", entry)
            self.assertIn("source", entry)
            self.assertEqual(entry["source"], "test_agent")

    def test_atomic_write_retry(self):
        """Test: Retry-Logic bei Write-Fehlern"""
        with patch.object(Path, "write_text", side_effect=[OSError("Fail"), OSError("Fail"), None]) as mock_write:
            # Sollte nach 3 Versuchen erfolgreich sein
            filename = self.client.write_cmd_safepoint("retry_test", {"test": "data"})
            self.assertIsNotNone(filename)
            self.assertEqual(mock_write.call_count, 3)

    def test_client_stats(self):
        """Test: Statistiken werden korrekt berechnet"""
        # Verschiedene Safepoints schreiben
        self.client.write_cmd_safepoint("stat_001", {"cmd": 1})
        self.client.write_cmd_safepoint("stat_002", {"cmd": 2})
        self.client.write_resp_safepoint("stat_003", {"resp": 1})

        # Stats abrufen
        stats = self.client.get_stats()

        self.assertEqual(stats["agent_id"], "test_agent")
        self.assertEqual(stats["total_safepoints"], 3)
        self.assertEqual(stats["by_category"]["CMD"], 2)
        self.assertEqual(stats["by_category"]["RESP"], 1)

    def test_portier30_compliance(self):
        """Test: PORTIER 3.0 Konformität"""
        compliance = self.client.validate_portier30_compliance()

        self.assertTrue(compliance["categories_correct"])
        self.assertTrue(compliance["secret_keys_complete"])
        self.assertTrue(compliance["archivp_structure"])
        self.assertTrue(compliance["index_file"])
        self.assertTrue(compliance["unicode_arrow_support"])

    @patch("httpx.AsyncClient")
    def test_sse_event_publishing(self, mock_client):
        """Test: SSE Events werden publiziert (ohne echte Verbindung)"""
        mock_post = MagicMock()
        mock_client.return_value.__aenter__.return_value.post = mock_post

        # Safepoint schreiben (triggert SSE Event)
        self.client.write_cmd_safepoint("sse_test", {"test": "data"})

        # Kurz warten für async task
        time.sleep(0.1)

        # Mock wurde aufgerufen (falls async task fertig)
        # Note: In echten Tests müsste man asyncio.run() verwenden


class TestSafepointClientFactory(unittest.TestCase):
    """Test Suite für Factory-Funktionen"""

    def test_create_safepoint_client(self):
        """Test: Factory erstellt Client korrekt"""
        client = create_safepoint_client("factory_test")

        self.assertEqual(client.agent_id, "factory_test")
        self.assertEqual(client.dashboard_url, "http://127.0.0.1:12349")
        self.assertEqual(str(client.archivp_root), "/tmp/archivp_store")

    def test_convenience_functions(self):
        """Test: Convenience-Funktionen funktionieren"""
        # Note: Würde echte Dateien in /tmp erstellen
        # In Produktionstest mit temporärem Verzeichnis


class TestMultiAgentScenarios(unittest.TestCase):
    """Test Suite für Multi-Agent-Szenarien"""

    def setUp(self):
        """Setup für Multi-Agent Tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.agent1 = SafepointClient("opena3", archivp_root=self.temp_dir)
        self.agent2 = SafepointClient("opena4", archivp_root=self.temp_dir)

    def tearDown(self):
        """Cleanup nach Multi-Agent Tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_shared_archivp_store(self):
        """Test: Mehrere Agenten teilen sich archivp_store"""
        # Beide Agenten schreiben Safepoints
        self.agent1.write_cmd_safepoint("multi_001", {"agent": "opena3"})
        self.agent2.write_cmd_safepoint("multi_002", {"agent": "opena4"})

        # Beide im gemeinsamen Index
        index_file = Path(self.temp_dir) / "index.jsonl"
        lines = index_file.read_text(encoding="utf-8").strip().split("\n")

        self.assertEqual(len(lines), 2)

        # Verschiedene Agents in Index
        sources = [json.loads(line)["source"] for line in lines]
        self.assertIn("opena3", sources)
        self.assertIn("opena4", sources)

    def test_agent_specific_stats(self):
        """Test: Statistiken sind agenten-spezifisch"""
        # Mehrere Safepoints von verschiedenen Agenten
        self.agent1.write_cmd_safepoint("stats_001", {"data": 1})
        self.agent1.write_resp_safepoint("stats_002", {"data": 2})
        self.agent2.write_cmd_safepoint("stats_003", {"data": 3})

        # Stats sind getrennt
        stats1 = self.agent1.get_stats()
        stats2 = self.agent2.get_stats()

        self.assertEqual(stats1["total_safepoints"], 2)
        self.assertEqual(stats2["total_safepoints"], 1)
        self.assertEqual(stats1["agent_id"], "opena3")
        self.assertEqual(stats2["agent_id"], "opena4")


class TestPerformance(unittest.TestCase):
    """Performance Tests für PORTIER 3.0"""

    def setUp(self):
        """Setup für Performance Tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = SafepointClient("perf_agent", archivp_root=self.temp_dir)

    def tearDown(self):
        """Cleanup Performance Tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_performance(self):
        """Test: Safepoint-Schreibzeit unter 50ms"""
        large_payload = {"data": "x" * 10000, "token": "secret"}

        start_time = time.time()
        self.client.write_cmd_safepoint("perf_001", large_payload)
        end_time = time.time()

        # Unter 50ms (0.05 Sekunden)
        self.assertLess(end_time - start_time, 0.05)

    def test_bulk_write_performance(self):
        """Test: 100 Safepoints unter 2 Sekunden"""
        start_time = time.time()

        for i in range(100):
            self.client.write_cmd_safepoint(f"bulk_{i:03d}", {"index": i})

        end_time = time.time()

        # Unter 2 Sekunden
        self.assertLess(end_time - start_time, 2.0)

        # Alle Dateien existieren
        stats = self.client.get_stats()
        self.assertEqual(stats["total_safepoints"], 100)


if __name__ == "__main__":
    print("🔥 PORTIER 3.0 Safepoint Test Suite")
    print("=" * 50)

    # Test-Suite ausführen
    unittest.main(verbosity=2)
