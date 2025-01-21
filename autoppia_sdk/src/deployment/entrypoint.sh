#!/bin/bash
set -e

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check required environment variables
check_env_vars() {
    if [ -z "$WORKER_ID" ] || [ -z "$WORKER_REPO_URL" ]; then
        log "Error: WORKER_ID and WORKER_REPO_URL must be set"
        exit 1
    fi
}

# Function to handle cleanup on script exit
cleanup() {
    log "Cleaning up..."
    if [ -d "/app/worker" ]; then
        rm -rf /app/worker
    fi
}

# Register cleanup function
trap cleanup EXIT

# Main execution
main() {
    # Check environment variables
    check_env_vars

    # Log startup
    log "Starting worker deployment"
    log "Worker ID: $WORKER_ID"
    log "Repository URL: $WORKER_REPO_URL"

    # Clone the repository
    log "Cloning repository..."
    git clone "$WORKER_REPO_URL" /app/"$WORKER_ID"

    # Change to worker directory
    cd /app/"$WORKER_ID"

    # Check if deploy.sh exists and is executable
    if [ ! -f "deploy.sh" ]; then
        log "Error: deploy.sh not found in repository"
        exit 1
    fi

    # Make deploy.sh executable
    chmod +x deploy.sh

    # Run deploy.sh with worker ID
    log "Running deploy.sh..."
    ./deploy.sh "$WORKER_ID"
}

# Run main function
main 