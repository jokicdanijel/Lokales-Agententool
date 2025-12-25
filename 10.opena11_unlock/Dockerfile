# 🔐 OPENA11 Unlock Master Agent
# PORTIER PAS-6.0 Docker Image

FROM python:3.12-slim

LABEL maintainer="ELION Team"
LABEL version="6.0.0"
LABEL description="OPENA11 Unlock Master Agent - PORTIER PAS-6.0"

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OPENA11_PORT=12357
ENV OPENA11_HOST=0.0.0.0

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 12357

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12357/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12357"]
