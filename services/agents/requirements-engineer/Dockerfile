# Requirements Engineer Agent Service
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

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy agent source
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src

# Environment variables
ENV AGENT_ENV=production
ENV MEMORY_SERVICE_URL=https://memory-service:8443/mcp
ENV AGENT_PORT=8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

# Expose port
EXPOSE 8082

# Start the agent service
CMD ["python", "src/requirements_engineer_agent.py"]