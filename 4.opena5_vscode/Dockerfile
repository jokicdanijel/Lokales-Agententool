FROM python:3.12-slim

WORKDIR /app

# Installiere System-Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Anforderungen
COPY requirements.txt .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere Anwendung
COPY . .

# Expose Port
EXPOSE 12350

# Health Check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:12350/health || exit 1

# Starte Anwendung
CMD ["python", "main_vscode_agent.py"]
