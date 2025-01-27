#!/bin/bash
set -e

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check required environment variables
check_env_vars() {
    if [ -z "$WORKER_ID" ] || [ -z "$WORKER_REPO_URL" ] || [ -z "$SSH_PRIVATE_KEY" ]; then
        log "Error: WORKER_ID, WORKER_REPO_URL, and SSH_PRIVATE_KEY must be set"
        exit 1
    fi
}

# Function to handle cleanup on script exit
cleanup() {
    log "Cleaning up..."
    if [ -d "/app/$WORKER_ID" ]; then
        rm -rf /app/"$WORKER_ID"
    fi
}

# Register cleanup function
trap cleanup EXIT

# Function to setup SSH
setup_ssh() {
    log "Setting up SSH..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
}

# Main execution
main() {
    # Check environment variables
    check_env_vars

    # Setup SSH
    setup_ssh

    # Log startup
    log "Starting worker deployment"
    log "Worker ID: $WORKER_ID"
    log "Repository URL: $WORKER_REPO_URL"

    # Clone the repository
    log "Cloning repository..."
    git clone "$WORKER_REPO_URL" /app/"$WORKER_ID"

    # Change to worker directory
    cd /app/"$WORKER_ID"

    # Create .env file with credentials
    log "Creating .env file..."
    cat > .env << EOL
# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}

# Other Configurations
WORKER_ID=${WORKER_ID}
EOL

    # Add local bin to PATH
    export PATH="$HOME/.local/bin:$PATH"

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