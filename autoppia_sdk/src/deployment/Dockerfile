# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 worker && \
    chown -R worker:worker /app

# Copy entrypoint script
COPY --chown=worker:worker scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER worker

# Create cache directory for pip
RUN mkdir -p /app/.cache/pip && \
    chown -R worker:worker /app/.cache/pip

# Set pip cache environment variable
ENV PIP_CACHE_DIR=/app/.cache/pip

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Create volume for pip cache
VOLUME ["/app/.cache/pip"]

# Expose the default worker port
EXPOSE 8080

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 