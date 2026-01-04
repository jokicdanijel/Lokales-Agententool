# scripts/

**Gate System (PORTIER 3.0) – Deterministische Baseline-Validierung & Agent-Discovery**

Stand: 4. Januar 2026

## 📋 Überblick

Zwei komplementäre Python-Scripts für **Enterprise-Hart Validierung** im CI/CD:

### 1. validate_baseline.py – Schema-Validierung (SSoT)

Validiert `system_baseline.yaml` gegen strenge Anforderungen:

```bash
python3 scripts/validate_baseline.py
# Output: artifacts/Baseline_validation.json
# Exit: 0 (OK) | 1 (FAIL)
```

**Prüft:**
- ✅ Exakt 21 Agents (opena1..opena21)
- ✅ Port-Eindeutigkeit
- ✅ Port-Range (12344–12399)
- ✅ Verbotene Ports (8080)
- ✅ Folder-Existenz
- ✅ Deterministische Sortierung

### 2. discover_agents.py – Kontext-aware Port-Discovery

Scannt Repository rekursiv und findet Port-Referenzen:

```bash
python3 scripts/discover_agents.py
# Output: artifacts/Agent_discovery.json
# Exit: 0 (OK) | 1 (FAIL)
```

**Features:**
- 🔍 **Kontext-aware Scanning**:
  - `.md/.txt` → Nur verbotene Ports (Doku-Noise vermeiden)
  - Code/Config → Binding-Patterns (PORT=, --port, host_port:, :port)
- ✅ **Port-Validierung** gegen Baseline
- 📊 **Metadaten-Extraktion** (Name, Role, Visibility)

### Legacy Helper Scripts

- `compose_all.sh` — Docker Compose Builder
- `validate_portier.sh` — Basic Health Checks
- Weitere Legacy Scripts für Portier 2.x

## 🚀 CI/CD Integration

Gate-Workflow in `.github/workflows/baseline-discovery-gate.yml`:

```yaml
- name: Validate Baseline
  run: python3 scripts/validate_baseline.py

- name: Discover Agents
  run: python3 scripts/discover_agents.py
```

**Fail-Fast:** Jeder Fehler blockiert den PR.

## 📚 Dokumentation

Siehe `docs/` für Details:
- `docs/GESETZ-README_PORTIER3_0.txt` — Binding Anforderungen
- `docs/PORTIER_REPOSITORY_STRUCTURE.md` — Repo-Layout
- `docs/PORTIER_3.0_SYSTEM_ARCHITECTURE.md` — System-Architektur

- Start ohne Build:
  ```bash
  ./scripts/compose_all.sh --no-build
  ```

Hinweise:
- Dieses Skript erwartet, dass `docker` und `docker compose` im PATH verfügbar sind.
- Es prüft auf vorhandene `docker-compose.yml` / `docker-compose.yaml` Dateien im Subprojekt.

Lizenz: Selbes Projekt-Lizenzmodell wie Repository.
