# LocalAgent-Pro Dockerfile (Multi-Stage Build)
FROM python:3.12-slim AS builder

# Build-Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# === RUNTIME STAGE ===
FROM python:3.12-slim

# Metadata
LABEL maintainer="xxjokic01@gmail.com"
LABEL description="LocalAgent-Pro - AI Agent with Tool Execution & Sandbox Isolation"
LABEL version="1.0.0"

# Runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash localagent

# Create app directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/localagent/.local

# Copy application code
COPY --chown=localagent:localagent src/ /app/src/
COPY --chown=localagent:localagent config/ /app/config/

# Create sandbox directory
RUN mkdir -p /app/sandbox && chown localagent:localagent /app/sandbox

# Create logs directory
RUN mkdir -p /app/logs && chown localagent:localagent /app/logs

# Set environment variables
ENV PATH=/home/localagent/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=src/openwebui_agent_server.py \
    FLASK_ENV=production \
    SANDBOX_PATH=/app/sandbox \
    LOG_LEVEL=INFO

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Switch to non-root user
USER localagent

# Start command
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8001"]
