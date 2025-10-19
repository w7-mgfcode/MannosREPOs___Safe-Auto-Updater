FROM python:3.11-slim

LABEL maintainer="Safe Auto-Updater Team"
LABEL description="Safe Auto-Updater for Docker and Kubernetes assets"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Install helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/

# Set Python path
ENV PYTHONPATH=/app

# Create log directory
RUN mkdir -p /var/log/safe-auto-updater

# Run as non-root user
RUN useradd -m -u 1000 updater && \
    chown -R updater:updater /app /var/log/safe-auto-updater
USER updater

# Entry point
ENTRYPOINT ["python", "-m", "safe_auto_updater.cli"]
CMD ["status"]
