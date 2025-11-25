# 🚀 Research Paper Manager - Setup Guide

Complete installation and configuration guide.

---

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual Environment (recommended)
- ~500MB disk space (for database and PDFs)

---

## ⚡ Quick Start (5 minutes)

### 1. Clone/Extract Project

```bash
cd research_paper_manager
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Server

```bash
python app/main.py
```

### 5. Access Dashboard

Open browser: `http://localhost:5002/dashboard`

---

## 🔧 Installation Details

### Step-by-Step Installation

#### 1. Create Project Directory

```bash
mkdir research_paper_manager
cd research_paper_manager
```

#### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Installed packages:
- Flask 3.0.0 - Web framework
- SQLAlchemy 2.0.0 - ORM
- requests 2.31.0 - HTTP client
- feedparser 6.0.10 - RSS/Atom parser
- python-dotenv 1.0.0 - Environment variables

#### 4. Configure Environment

Create `.env` file:

```env
# Database
DB_PATH=./research_papers.db

# arXiv API
ARXIV_API_URL=https://export.arxiv.org/api/query

# Server
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 5. Initialize Database

```bash
python -c "from app.db.database import init_db; init_db()"
```

This creates the SQLite database with tables:
- `papers` - Paper metadata
- `tags` - Paper tags
- `collections` - Paper collections
- `collection_papers` - Many-to-many association

#### 6. Start Server

```bash
python app/main.py
```

Output:
```
🚀 Research Paper Manager starting...
📚 Database: ./research_papers.db
🌐 API: http://localhost:5002/api
📖 Dashboard: http://localhost:5002/dashboard
```

---

## 🌐 Running on Different Ports

### Change Port in Environment

```bash
export FLASK_PORT=5003
python app/main.py
```

Or modify `app/main.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
```

---

## 📁 Configuration Files

### `.env` - Environment Variables

```env
# Database Configuration
DB_PATH=./research_papers.db
DB_TYPE=sqlite  # or postgresql

# arXiv API
ARXIV_API_URL=https://export.arxiv.org/api/query
ARXIV_TIMEOUT=30
ARXIV_MAX_RESULTS=100

# AI Features
AI_ENABLED=true
AI_MODEL=Qwen3-Coder-30B-A3B-Instruct
AI_API_URL=http://localhost:8000/v1

# Server
FLASK_ENV=production
FLASK_DEBUG=False
SERVER_HOST=0.0.0.0
SERVER_PORT=5002

# Storage
PAPERS_STORAGE_PATH=./papers
PDF_STORAGE_PATH=./papers/pdfs
```

### `config.yaml` - Advanced Configuration

```yaml
database:
  type: sqlite
  path: ./research_papers.db
  pool_size: 10
  max_overflow: 20

arxiv:
  api_url: https://export.arxiv.org/api/query
  timeout: 30
  max_results: 100
  retry_attempts: 3

ai:
  enabled: true
  model: Qwen3-Coder-30B-A3B-Instruct
  api_url: http://localhost:8000/v1
  temperature: 0.7
  max_tokens: 1000

web:
  host: 0.0.0.0
  port: 5002
  debug: false
  cors_origins: ["*"]

storage:
  papers_dir: ./papers
  pdfs_dir: ./papers/pdfs
  max_pdf_size_mb: 100
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Initialize database
RUN python -c "from app.db.database import init_db; init_db()"

# Expose port
EXPOSE 5002

# Run app
CMD ["python", "app/main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  research-manager:
    build: .
    ports:
      - "5002:5002"
    environment:
      - DB_PATH=/app/data/research_papers.db
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./papers:/app/papers
    restart: unless-stopped
```

### Build & Run

```bash
# Build image
docker build -t research-paper-manager .

# Run container
docker run -p 5002:5002 -v $(pwd)/data:/app/data research-paper-manager

# Or with docker-compose
docker-compose up -d
```

---

## 📦 Database Setup

### SQLite (Default)

Automatically created on first run. Database file: `research_papers.db`

```bash
# Backup database
cp research_papers.db research_papers.backup.db

# Export data
sqlite3 research_papers.db ".dump" > backup.sql

# Restore from backup
sqlite3 research_papers.db < backup.sql
```

### PostgreSQL (Optional)

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DB_PATH=postgresql://user:password@localhost:5432/research_papers
```

---

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test arXiv Integration

```python
from app.services.arxiv_service import ArxivService

arxiv = ArxivService()

# Search for papers
papers = arxiv.search("machine learning", max_results=10)
print(f"Found {len(papers)} papers")

# Fetch specific paper
paper = arxiv.fetch_paper("2505.09388")
print(paper['title'])
```

---

## 🔌 Integration with External Systems

### As OpenWebUI Tool

```python
# In OpenWebUI configuration
EXTERNAL_TOOLS = [
    {
        "name": "Research Paper Manager",
        "endpoint": "http://localhost:5002/api",
        "endpoints": {
            "search": "/search",
            "fetch": "/arxiv/fetch",
            "list": "/papers"
        }
    }
]
```

### With Browser Agent Tool Server

```python
# Port forwarding from tool server
RESEARCH_MANAGER_URL = "http://localhost:5002"

tools = {
    "research_papers": {
        "search": f"{RESEARCH_MANAGER_URL}/api/search",
        "fetch": f"{RESEARCH_MANAGER_URL}/api/arxiv/fetch"
    }
}
```

---

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Find process using port 5002
lsof -i :5002

# Kill process
kill -9 <PID>

# Or run on different port
python app/main.py --port 5003
```

### Database Errors

```bash
# Reset database
rm research_papers.db
python -c "from app.db.database import init_db; init_db()"
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

### arXiv Connection Issues

```bash
# Test arXiv API
curl "https://export.arxiv.org/api/query?search_query=machine+learning&max_results=1"

# Check network
ping arxiv.org
```

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.11+ |
| RAM | 512MB | 2GB+ |
| Disk | 500MB | 5GB+ |
| CPU | 1 core | 2+ cores |
| Internet | Required | Required for arXiv |

---

## 🔐 Security Best Practices

1. **Environment Variables**: Store sensitive data in `.env`, never in code
2. **Database Backups**: Regular backups recommended
3. **API Keys**: Keep AI service keys secure
4. **CORS**: Restrict origins in production
5. **Logging**: Monitor access logs

---

## 📝 Logs

### Access Logs

```bash
# View Flask logs
tail -f flask.log

# Or in production with gunicorn
gunicorn --access-logfile - --error-logfile - app.main:app
```

### Database Logs

```bash
# SQLAlchemy SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] arXiv search works
- [ ] Papers can be imported
- [ ] Dashboard accessible

---

**Last Updated:** 2025-11-25
**Version:** 1.0.0
