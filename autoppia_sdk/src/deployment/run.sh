#!/usr/bin/env bash
set -e

# In the Dockerfile, we set ENV for these, or user passes them via docker run -e ...
WORKER_ID=${WORKER_ID}
WORKER_TEMPLATE_REPO_URL=${WORKER_TEMPLATE_REPO_URL}

if [ -z "$WORKER_TEMPLATE_REPO_URL" ]; then
  echo "Error: WORKER_TEMPLATE_REPO_URL not set."
  exit 1
fi

if [ -z "$WORKER_ID" ]; then
  echo "Error: WORKER_ID not set."
  exit 1
fi

echo "Cloning the worker template repo: $WORKER_TEMPLATE_REPO_URL"
git clone "$WORKER_TEMPLATE_REPO_URL" /tmp/worker_repo

cd /tmp/worker_repo

echo "Installing the worker template code..."
pip install -e .

echo "Running worker repo's deploy.sh with worker_id=$WORKER_ID"
chmod +x deploy.sh
./deploy.sh "$WORKER_ID"

# The assumption here is that deploy.sh never returns if uvicorn is running in the foreground
# or if it does, the container stops.
