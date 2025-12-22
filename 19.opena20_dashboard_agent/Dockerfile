# opena20 Dashboard Agent - Production Docker Image \n# PORTIER 3.0 Konform | Ubuntu 25.04 Base

FROM ubuntu:25.04

LABEL maintainer="xxjokic01@gmail.com"
LABEL version="1.0.0"
LABEL description="ELION/Portier opena20 Dashboard Agent"

# Environment
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PORT=12349
ENV BEARER_TOKEN=c899b90d-faf8-485b-afa4-078357cf5313
ENV OPENA2_URL=http://opena2:12345

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    python3-pip \
    curl \
    jq \
    nano \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash appuser

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python3.13 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

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
CMD ["python3.13", "main_dashboard_final.py"]
