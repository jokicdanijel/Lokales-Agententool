# opena20 Dashboard Agent - Production Docker Image
# PORTIER 3.0 Konform | Python 3.11 Slim Base

FROM python:3.11-slim

LABEL maintainer="xxjokic01@gmail.com"
LABEL version="1.0.0"
LABEL description="ELION/Portier opena20 Dashboard Agent"

# Environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PORT=12349

ENV OPENA2_URL=http://opena2:12345

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    nano \
    htop \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash appuser

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main_dashboard_final.py .
COPY static/ ./static/
COPY templates/ ./templates/
COPY *.html ./

# Create data directories
RUN mkdir -p logs data/dashboard_pages data/opena15_generated

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run application
CMD ["python", "main_dashboard_final.py"]
