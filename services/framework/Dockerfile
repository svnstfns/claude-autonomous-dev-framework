# Claude Autonomous Development Framework - Core Service
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    docker.io \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework source
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/.claude

# Set Python path
ENV PYTHONPATH=/app/src

# Environment variables
ENV FRAMEWORK_ENV=production
ENV MEMORY_SERVICE_URL=https://memory-service:8443/mcp
ENV REDIS_URL=redis://redis:6379
ENV DASHBOARD_URL=http://dashboard:8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start the framework
CMD ["python", "src/framework_server.py"]