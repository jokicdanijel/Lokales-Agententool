# 📚 Research Paper Management System

Ein umfassendes System zur Verwaltung akademischer Papers mit arXiv-Integration, Tagging, Kategorisierung und AI-gestützter Analyse.

**Status:** 🚀 In Entwicklung
**Version:** 0.1.0
**Datum:** 2025-11-25

---

## ✨ Features

### 🔍 Paper Discovery & Management
- ✅ arXiv API Integration - Direkter Zugriff auf Millionen Papers
- ✅ Automatische Metadaten-Extraktion (Titel, Autoren, Abstract, etc.)
- ✅ arXiv ID Parser - Automatische Erkennung von Paper-IDs
- ✅ Advanced Search - Kategorie, Autor, Datum, Keywords

### 📁 Organisation & Tagging
- ✅ Custom Tags & Labels
- ✅ Kategorisierung (Physics, CS, Math, Bio, etc.)
- ✅ Favoriten & Lesezeichen
- ✅ Collections & Ordner

### 💾 Persistenz
- ✅ SQLite Datenbank
- ✅ PDF-Download & -Speicherung
- ✅ Offline-Zugriff
- ✅ Backup & Export (JSON, CSV)

### 🤖 AI-Features (mit Qwen3-Coder)
- ✅ Automatische Zusammenfassungen
- ✅ Keyword-Extraktion
- ✅ Ähnliche Papers suchen
- ✅ Citation Network Analysis

### 🌐 API & UI
- ✅ RESTful API (Flask)
- ✅ Web Dashboard (HTML/JavaScript)
- ✅ JSON-Export
- ✅ Volltext-Search

---

## 🚀 Quick Start

### Installation

```bash
cd research_paper_manager
pip install -r requirements.txt
```

### Server starten

```bash
python app/main.py
```

Server läuft auf: `http://localhost:5002`

### Web-Dashboard

```
http://localhost:5002/dashboard
```

---

## 📋 Projektstruktur

```
research_paper_manager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask App Entry Point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── papers.py          # Paper CRUD Endpoints
│   │   ├── search.py          # Search Endpoints
│   │   └── arxiv.py           # arXiv Integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── paper.py           # SQLAlchemy Models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── arxiv_service.py   # arXiv API Wrapper
│   │   ├── search_service.py  # Search Logic
│   │   └── ai_service.py      # AI/Qwen3 Integration
│   └── db/
│       ├── __init__.py
│       ├── database.py        # SQLite Setup
│       └── schema.sql         # Database Schema
├── web/
│   ├── index.html            # Dashboard HTML
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js            # Frontend Logic
├── docs/
│   ├── API.md               # API Documentation
│   ├── SETUP.md             # Setup Guide
│   └── ARXIV_GUIDE.md       # arXiv Integration
├── requirements.txt
└── README.md
```

---

## 📖 Dokumentation

- **[API Reference](docs/API.md)** - Alle Endpoints
- **[Setup Guide](docs/SETUP.md)** - Installation & Config
- **[arXiv Integration](docs/ARXIV_GUIDE.md)** - Paper fetching
- **[Database Schema](app/db/schema.sql)** - Datenbank-Design

---

## 🔌 API Endpoints

### Papers

```
GET    /api/papers              # Alle Papers abrufen
POST   /api/papers              # Neues Paper hinzufügen
GET    /api/papers/<id>         # Paper Details
PUT    /api/papers/<id>         # Paper aktualisieren
DELETE /api/papers/<id>         # Paper löschen
```

### Search

```
GET    /api/search?q=quantum&category=physics
GET    /api/arxiv/search?query=machine%20learning
GET    /api/papers/by-author?author=Einstein
```

### arXiv Integration

```
POST   /api/arxiv/fetch         # Paper von arXiv importieren
GET    /api/arxiv/info/<arxiv_id>  # arXiv Paper Info
POST   /api/arxiv/download/<arxiv_id>  # PDF runterladen
```

---

## 💾 Datenbank-Schema

```sql
papers
├── id              (INTEGER PRIMARY KEY)
├── arxiv_id        (TEXT UNIQUE)
├── title           (TEXT)
├── authors         (TEXT)
├── abstract        (TEXT)
├── category        (TEXT)
├── url             (TEXT)
├── pdf_url         (TEXT)
├── published_date  (DATE)
├── created_at      (TIMESTAMP)
├── updated_at      (TIMESTAMP)
└── metadata        (JSON)

tags
├── id
├── paper_id (FK)
├── tag_name
└── created_at

collections
├── id
├── name
├── description
└── created_at

collection_papers
├── collection_id (FK)
├── paper_id (FK)
└── added_at
```

---

## 🤖 Qwen3-Coder Integration

Das System unterstützt AI-gestützte Analyse mit Qwen3-Coder:

```python
from app.services.ai_service import AIService

ai = AIService(model="Qwen3-Coder-30B-A3B-Instruct")

# Zusammenfassung generieren
summary = ai.summarize_paper(paper_text)

# Keywords extrahieren
keywords = ai.extract_keywords(abstract)

# Ähnliche Papers finden
similar = ai.find_similar_papers(paper_id)
```

---

## 🔍 arXiv Integration

Automatische Verbindung mit arXiv API:

```python
from app.services.arxiv_service import ArxivService

arxiv = ArxivService()

# Paper suchen
results = arxiv.search(
    query="machine learning",
    category="cs.AI",
    max_results=50
)

# Spezifisches Paper laden
paper = arxiv.fetch_paper("2505.09388")

# PDF runterladen
pdf_path = arxiv.download_pdf("2505.09388")
```

---

## 📊 Beispiel: Paper hinzufügen

### Via API

```bash
curl -X POST http://localhost:5002/api/papers \
  -H "Content-Type: application/json" \
  -d '{
    "arxiv_id": "2505.09388",
    "title": "Qwen3 Technical Report",
    "authors": ["Qwen Team"],
    "category": "cs.CL",
    "abstract": "..."
  }'
```

### Via Python

```python
from app.services.arxiv_service import ArxivService
from app.api.papers import add_paper

arxiv = ArxivService()
paper_info = arxiv.fetch_paper("2505.09388")
add_paper(paper_info)
```

---

## 🛠️ Konfiguration

### Environment Variables

```bash
ARXIV_API_URL=https://export.arxiv.org/api/query
DB_PATH=./research_papers.db
AI_MODEL=Qwen3-Coder-30B-A3B-Instruct
AI_API_URL=http://localhost:8000/v1
```

### Config-Datei (`config.yaml`)

```yaml
arxiv:
  api_url: https://export.arxiv.org/api/query
  max_results: 100
  timeout: 30

database:
  type: sqlite
  path: ./research_papers.db

ai:
  enabled: true
  model: Qwen3-Coder-30B-A3B-Instruct
  api_url: http://localhost:8000/v1

web:
  host: 0.0.0.0
  port: 5002
  debug: false
```

---

## 📦 Dependencies

```
Flask==3.0.0
SQLAlchemy==2.0.0
requests==2.31.0
feedparser==6.0.10
python-dotenv==1.0.0
openai==1.3.0  # Für Qwen3-Coder Integration
```

---

## 🧪 Testing

```bash
# Unit Tests
python -m pytest tests/ -v

# Integration Tests
python -m pytest tests/integration/ -v

# API Tests
python -m pytest tests/api/ -v
```

---

## 🔐 Sicherheit

- ✅ Bearer Token Authentication
- ✅ Input Validation
- ✅ SQL Injection Prevention (SQLAlchemy ORM)
- ✅ Rate Limiting (optional)
- ✅ CORS Configuration

---

## 📝 Beispiel-Workflows

### Workflow 1: Tägliche Paper-Briefs

```python
# Neue Papers von heute fetchen
papers = arxiv.search(
    query="machine learning",
    date_from=datetime.today()
)

# Zu Collection hinzufügen
for paper in papers:
    add_to_collection(paper, "Daily Digest")
    summary = ai.summarize(paper)
    send_notification(summary)
```

### Workflow 2: Literature Review

```python
# Papers nach Thema suchen
papers = search_papers(
    category="cs.AI",
    keywords=["neural networks", "transformers"],
    year=2024
)

# Exportieren für Überprüfung
export_papers(papers, format="bibtex")

# AI-gestützte Analyse
analysis = ai.analyze_collection(papers)
```

---

## 🎯 Roadmap

- [ ] v0.1.0 - Basis-Features (Dezember 2025)
- [ ] v0.2.0 - AI Integration (Januar 2026)
- [ ] v0.3.0 - Advanced Search (Februar 2026)
- [ ] v0.4.0 - Collaboration Features (März 2026)
- [ ] v1.0.0 - Production Ready (April 2026)

---

## 🤝 Integration mit bestehenden Systemen

### OpenWebUI Integration

```python
# Paper als Tool in OpenWebUI verwenden
tools = [
    {
        "name": "search_papers",
        "description": "Suche nach akademischen Papers",
        "endpoint": "http://localhost:5002/api/search"
    }
]
```

### Browser Agent Tool Server

```python
# Papers als externe Ressource bereitstellen
tools_manifest = {
    "name": "Research Paper Manager",
    "endpoint": "http://192.168.0.70:5002",
    "capabilities": ["search", "fetch", "summarize"]
}
```

---

## 📞 Support & Kontakt

- **Issues:** GitHub Issues
- **Dokumentation:** `/docs`
- **Email:** jokicdanijel@gmail.com

---

## 📄 Lizenz

MIT License - Frei verwendbar

---

**Zitation (Qwen3):**

```bibtex
@misc{qwen3technicalreport,
      title={Qwen3 Technical Report},
      author={Qwen Team},
      year={2025},
      eprint={2505.09388},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.09388}
}
```

---

**Letztes Update:** 2025-11-25
**Status:** 🚀 Aktive Entwicklung
