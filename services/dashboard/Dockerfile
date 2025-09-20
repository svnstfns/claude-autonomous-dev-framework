# Claude Autonomous Development Framework - Dashboard Service
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dashboard source
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set Python path
ENV PYTHONPATH=/app/src

# Environment variables
ENV DASHBOARD_ENV=production
ENV FRAMEWORK_API_URL=http://framework:8080
ENV MEMORY_API_URL=https://memory-service:8443/mcp
ENV REDIS_URL=redis://redis:6379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Expose port
EXPOSE 8081

# Start the dashboard
CMD ["python", "src/dashboard_server.py"]