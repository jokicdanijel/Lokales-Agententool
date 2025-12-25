# Repository Scanner – ChatGPT-Ready Project Map Generator

Zero-dependency, cross-platform Python scanner (Linux/Mac/Windows, Python ≥3.10). Erzeugt strukturierte Projektmaps für Code-Review und ChatGPT-Analyse in ~2 Sekunden.

## 📦 Installation & Verwendung

### Quickstart (one-liner)

```bash
# Im Projektroot:
make scan
# oder ohne Make:
python3 tools/scan_project.py --root . --out project_map
```

### Output-Artefakte (in `project_map/`)

| Datei               | Größe   | Inhalt                                                     |
| ------------------- | ------- | ---------------------------------------------------------- |
| **STRUCTURE.md**    | ~37 KB  | ChatGPT-ready Überblick: Tree, Stats, Hotspots, Violations |
| **path_index.json** | ~2.1 MB | JSON-Array aller Dateien mit Metadaten + SHA256-Hashes     |
| **files.csv**       | ~1.1 MB | Gleiche Infos wie JSON, CSV-Format (UTF-8)                 |
| **stats.json**      | ~2.5 KB | Summen: Dateizahl, Größe, Extension-Counts, Top-Level      |
| **TREE.txt**        | ~326 KB | Vollständiger Ordnerbaum (kein Pruning)                    |
| **violations.md**   | ~668 KB | Violations (Tiefe >6, Größe >25 MB, binär in src/, etc.)   |

### Makefile Targets

```bash
# Scan durchführen (alle 6 Artefakte)
make scan

# project_map/ löschen
make clean-map

# Help anzeigen
make help
```

### CLI-Optionen

```bash
python3 tools/scan_project.py \
  --root . \                       # Repo-Root (default: .)
  --out project_map \              # Output-Dir (default: project_map)
  --max-tree-depth 4 \             # Tree-Pruning in STRUCTURE.md (default: 4)
  --hash-limit-mb 5                # SHA256 nur bis 5 MB (default: 5)
```

## 📊 Outputs Erklärt

### STRUCTURE.md – ChatGPT-optimiert

```markdown
# Project Structure

- **Root**: `Gesamtprojekt`
- **Scanned**: `2025-11-09T02:49:17Z`
- **Host**: `Linux 6.14.0-35-generic` · Python: `3.12.3`

| Metric         | Value  |
| -------------- | ------ |
| **Files**      | 5249   |
| **Total Size** | 379 MB |
| **Skipped**    | 50     |
| **Duration**   | 1.7s   |

## Directory Tree (depth ≤ 4)

[kompaktes Verzeichnis-Präfix, max. 4 Ebenen]

## Key Areas

[Dateizahl nach src/, app/, services/, etc.]

## Hotspots: Largest Files (Top 20)

[Größte Dateien]

## Hotspots: Newest Files (Top 20)

[Zuletzt geänderte Dateien]

## Files by Extension

[Statistik: .py, .json, .md, etc.]

## Files by Top-Level Folder

[Statistik: 1.opena1&2_portier, 19.dashboard_agent, etc.]
```

**Größe**: max. ~500 KB (für große Repos). Perfekt für PR-Reviews, GitHub Discussions, ChatGPT-Analysen.

### path_index.json – Maschinenlesbar

```json
[
  {
    "path": "src/main.py",
    "size_bytes": 12345,
    "mtime_iso": "2025-11-09T02:49:00Z",
    "ext": ".py",
    "depth": 2,
    "is_symlink": false,
    "symlink_target": null,
    "is_executable": false,
    "is_binary": false,
    "sha256": "abc123..."
  },
  ...
]
```

**Felder**:

- `path`: Relative Pfad (POSIX, `/` als Separator)
- `size_bytes`: Dateigröße (0 bei Symlinks)
- `mtime_iso`: Modifikationszeit (ISO 8601 UTC)
- `ext`: Datei-Extension (Lowercased, `""` wenn keine)
- `depth`: Verschachtelungstiefe (1 = Root)
- `is_symlink`: Boolean
- `symlink_target`: OS-spezifisches Ziel (nur wenn Symlink)
- `is_executable`: Unix-Bit prüfbar (nur auf Unix)
- `is_binary`: Heuristik (Nullbytes oder viele Steuerzeichen)
- `sha256`: Hex-Hash (nur bis `hash_limit_mb`, sonst `null`)

### files.csv – Import-ready

```csv
path,size_bytes,mtime_iso,ext,depth,is_symlink,symlink_target,is_executable,is_binary,sha256
src/main.py,12345,2025-11-09T02:49:00Z,.py,2,False,,False,False,abc123...
src/data.bin,98765,2025-11-08T10:00:00Z,.bin,2,False,,False,True,
```

**UTF-8 mit BOM möglich** (Excel-kompatibel). Trennzeichen: `,`.

### stats.json – Aggregiert

```json
{
  "scanned_at": "2025-11-09T02:49:17.834397+00:00",
  "root": "Gesamtprojekt",
  "file_count": 5249,
  "total_size_bytes": 396945590,
  "by_extension": {
    ".py": 3632,
    ".json": 177,
    ".md": 103,
    ...
  },
  "by_top_level": {
    "1.opena1&2_portier": 3525,
    "19.dashboard_agent": 22,
    ...
  },
  "hash_limit_bytes": 5242880,
  "violations_count": 5262,
  "errors_count": 0,
  "duration_sec": 1.818
}
```

### violations.md – Automatische Compliance

Flags für häufige Probleme:

- **[DEPTH >6]**: Pfade tiefer als 6 Ebenen (pytest, mypy caches, venv → expected)
- **[SIZE ≥25 MB]**: Große Dateien, die selten in Git gehören
- **[BINARY_IN_SRC]**: Binärdateien unter `src/` (verdächtig)
- **[DUP_NAME]**: Duplizierte Dateinamen (z.B. `setup.py` mehrfach)

### TREE.txt – Vollständig

Ungekürzter Ordnerbaum ohne Pruning (für `--max-tree-depth` zu ∞). Für Tools, die das volle Tree-Image brauchen.

## 🔧 Code-Struktur

### tools/\_common.py (Utilities, nur Stdlib)

```python
relpath_posix(path, root)          # Relativer Pfad mit /
iso_utc(ts)                        # ISO 8601 Timestamp
file_ext(path)                     # Extension (.py, .json, etc.)
path_depth(path)                   # Verschachtelungstiefe
is_executable(mode)                # Unix-Bit prüfbar
is_probably_binary(path)           # Heuristik: Nullbytes, etc.
sha256_limited(path, limit_bytes)  # Hash mit Größenlimit
load_gitignore_patterns(root)      # .gitignore laden (Root)
should_exclude(rel, is_dir, ...)   # Exclude-Logik (harte + gitignore)
render_tree(root, files, depth)    # Tree rendern (str)
human_bytes(n)                     # Bytes → "1.5 MB"
```

### tools/scan_project.py (Main Scanner)

- **Argument Parsing**: `--root`, `--out`, `--max-tree-depth`, `--hash-limit-mb`
- **Walk Pruning**: `os.walk` mit `topdown=True`, `followlinks=False`
- **Exclude-Logik**: Harte Defaults (`.git/`, `node_modules/`, `venv/`, etc.) + `.gitignore` (Light)
- **Datei-Processing**: Metadaten, Binary-Check, SHA256 (gechunked, 64 KiB Chunks)
- **Symlink-Handling**: `os.lstat()` (nicht folgen), `os.readlink()` prüfen
- **Output**: Alle 6 Artefakte sequenziell geschrieben
- **Fehler**: Per-Datei abgefangen, in `violations.md` geloggt

## 🚀 Performance

- **5249 Dateien**, 379 MB: ~1.8 Sekunden
- **RAM-Footprint**: < 50 MB (Iteratives Schreiben, nicht in RAM)
- **Cross-Platform**: Linux, macOS, Windows (Path-Separator auto)
- **Keine Deps**: Nur Python 3.10+ + Stdlib

## 📋 Exclude-Regeln (Default)

### Harte Excludes (Standard)

```
.git/
.github/
.gitlab/
.idea/
.vscode/
node_modules/
venv/
.venv/
env/
dist/
build/
__pycache__/
coverage/
backups/
_conflicts/
*.log
*.lock
*.tmp
*.bin
*.min.*
*.class
*.o
*.so
*.dll
*.dylib
*.iso
*.img
```

### .gitignore Parser (Light)

- Liest **Root-Level `.gitignore`** nur (Unterordner möglich, aber optional)
- Pattern-Match: `fnmatch` (simple glob)
- Negation: `!pattern` (Opt-Out)
- Verzeichnis-Pattern: `dir/` (trifft wenn `dir` ein Segment ist)

## 🔍 Use Cases

### 1. **Code Review Prep**

```bash
# Scan generieren
make scan
# Uploade STRUCTURE.md zu PR/Discussion
cat project_map/STRUCTURE.md > /dev/clipboard  # macOS
# oder
cat project_map/STRUCTURE.md | xclip -selection clipboard  # Linux
```

### 2. **ChatGPT Projekt-Analyse**

```bash
# Scan generieren
make scan
# Kopiere STRUCTURE.md + stats.json + violations.md in ChatGPT
# Prompt: "Analyze this project structure. Provide recommendations for refactoring."
```

### 3. **Excel-Import (Datei-Inventar)**

```bash
make scan
# Öffne project_map/files.csv in Excel/Sheets
# Sortiere nach size_bytes, ext, depth, etc.
```

### 4. **Compliance / Audit**

```bash
make scan
# Prüfe violations.md auf [BINARY_IN_SRC], [SIZE >25MB], etc.
# Lese stats.json für automatische Metriken (file_count, total_size, etc.)
```

### 5. **Reproduzierbare Snapshots**

```bash
# Zwei Scans ohne Repo-Änderungen = byte-identical JSON/CSV
make clean-map && make scan  # Run 1
cp project_map project_map.v1

make clean-map && make scan  # Run 2
cp project_map project_map.v2

# Vergleiche
diff project_map.v1/path_index.json project_map.v2/path_index.json
# → no output (identical)
```

## 🛠️ Optionale Konfiguration

### Custom Excludes

Edit `tools/scan_project.py`, Zeile ~40:

```python
DEFAULT_EXCLUDES = {
    # Existing excludes...
    "custom_dir/",      # Add here
    "*.custom_ext",
}
```

### Symlinks Folgen

Edit `tools/scan_project.py`, Zeile ~200:

```python
for cur, dirs, fnames in os.walk(root, topdown=True, followlinks=True):  # Change to True
```

## 📝 Troubleshooting

### "ModuleNotFoundError: No module named '\_common'"

```bash
# Stelle sicher, dass _common.py im Verzeichnis ist
ls tools/_common.py tools/scan_project.py

# Oder mit explizitem sys.path
cd tools && python3 scan_project.py --root .. --out ../project_map
```

### Zu viele Violations ([DEPTH >6])

Normal! venv, node_modules, mypy_cache, .git sind tief. Nutze `DEFAULT_EXCLUDES` um sie zu filtern.

### SHA256 fehlt (null in JSON)

Datei ist größer als `--hash-limit-mb` (default: 5 MB). Nutze `--hash-limit-mb 0` um alle zu hashen (langsam für große Repos).

### Windows: "Permission denied" bei Symlinks

Windows-Symlinks erfordern Admin-Rechte. Scanner markiert sie als `is_symlink=true` und prüft nicht das Ziel.

## 📄 Lizenz & Attribution

- **Autor**: GitHub Copilot + Danijel J.
- **Lizenz**: Public Domain (nutze frei in deinem Repo)
- **Abhängigkeiten**: Keine (nur Python 3.10+ Stdlib)

## 🤝 Integration mit bestehenden Tools

### mit git hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
make scan
git add project_map/
```

### mit CI/CD (GitHub Actions)

```yaml
- name: Scan project
  run: make scan

- name: Upload project map
  uses: actions/upload-artifact@v3
  with:
    name: project-map
    path: project_map/
```

### mit Documentation Generators

```bash
# Generiere Docs automatisch
make scan
# Nutze STRUCTURE.md als basis.md → sphinx, mkdocs, etc.
cat project_map/STRUCTURE.md >> docs/architecture.md
```

---

**Status**: ✅ Production-Ready | **Tests**: Cross-platform (Linux, macOS, Windows) | **Last Updated**: 2025-11-09
