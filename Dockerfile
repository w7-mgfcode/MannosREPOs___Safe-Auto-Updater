# Safe Auto-Updater Dockerfile
FROM python:3.11-slim

LABEL maintainer="MannosREPOs"
LABEL description="Safe Auto-Updater for Docker and Kubernetes"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY setup.py .
COPY README.md .

# Install the application
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 updater && \
    chown -R updater:updater /app

USER updater

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--help"]
