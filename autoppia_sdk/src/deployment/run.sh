#!/usr/bin/env bash
set -e

# Configuration
WORKER_ID=${WORKER_ID}
WORKER_TEMPLATE_REPO_URL=${WORKER_TEMPLATE_REPO_URL}
IMAGE_NAME=${IMAGE_NAME:-worker-template}
IMAGE_TAG=${IMAGE_TAG:-$WORKER_ID}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-""}
ENVIRONMENT=prod

# Validate inputs
if [ -z "$WORKER_TEMPLATE_REPO_URL" ]; then
  echo "Error: WORKER_TEMPLATE_REPO_URL not set."
  exit 1
fi

if [ -z "$WORKER_ID" ]; then
  echo "Error: WORKER_ID not set."
  exit 1
fi

# Clone worker template
echo "Cloning worker template repo: $WORKER_TEMPLATE_REPO_URL"
WORKER_DIR="/tmp/worker_$WORKER_ID"
git clone "$WORKER_TEMPLATE_REPO_URL" "$WORKER_DIR"
cd "$WORKER_DIR"

# Build Docker image
echo "Building Docker image for worker $WORKER_ID..."
docker build -t $IMAGE_NAME:$IMAGE_TAG --build-arg ENVIRONMENT=$ENVIRONMENT .

# Push to registry if specified
if [ -n "$DOCKER_REGISTRY" ]; then
  echo "Tagging and pushing image to registry..."
  docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
  docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
fi

# Deploy worker
echo "Deploying worker $WORKER_ID..."
if [ -f "deploy.sh" ]; then
  chmod +x deploy.sh
  ./deploy.sh "$WORKER_ID"
else
  echo "Warning: No deploy.sh found in worker template. Using default deployment."
  docker run -d \
    --name "worker_$WORKER_ID" \
    -e WORKER_ID=$WORKER_ID \
    -e ENVIRONMENT=$ENVIRONMENT \
    $IMAGE_NAME:$IMAGE_TAG
fi

echo "Worker $WORKER_ID deployed successfully!"
