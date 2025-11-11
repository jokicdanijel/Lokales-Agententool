FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

# Copy service code
COPY . /app/

# Expose port (will be overridden by docker-compose)
EXPOSE 12349

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:${PORT:-12349}/health')"

# Run service
CMD ["python", "-u", "main.py"]
