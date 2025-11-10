FROM python:3.12-slim

LABEL maintainer="ELION Hyper-Dashboard"
LABEL description="opena6 — Browser Automation Agent"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libgconf-2-4 libatk1.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 \
    libxss1 libappindicator1 libindicator7 fonts-liberation \
    libasound2 libnspr4 libxrender1 libxext6 xdg-utils \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN useradd -m -u 1000 appuser

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

# Copy application code
COPY app/ ./app/
COPY .env.example ./.env

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 12349

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12349/health || exit 1

# Start application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "12349"]
