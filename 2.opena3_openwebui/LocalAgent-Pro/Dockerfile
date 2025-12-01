FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create directories
RUN mkdir -p /app/sandbox /app/logs

# Expose port
EXPOSE 8001

# Run application
CMD ["python", "src/openwebui_agent_server.py"]
