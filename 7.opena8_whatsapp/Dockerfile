FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r opena8 && useradd -r -g opena8 opena8

# Install dependencies
COPY 8.opena8_whatsapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY 8.opena8_whatsapp/app ./app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:12351/health').read()" || exit 1

# Switch to non-root user
USER opena8

EXPOSE 12351

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12351"]
