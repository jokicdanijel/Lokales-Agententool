FROM python:3.12-slim

LABEL maintainer="ELION Hyper-Dashboard"
LABEL description="opena7 — Mail Agent"
LABEL version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN useradd -m -u 1000 appuser

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy static HTML files
COPY app/ ./app/
COPY html/ ./html/
COPY .env.example ./.env

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 12352

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12352/health || exit 1

# Start application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12352"]
