#!/usr/bin/env bash
set -e

if [ -z "$WORKER_ID" ]; then
  echo "WORKER_ID not set. Exiting."
  exit 1
fi

# 1. Retrieve worker info from your backend
echo "Retrieving worker info for WORKER_ID=$WORKER_ID"
python scripts/fetch_worker_info.py "$WORKER_ID"

# scripts/fetch_worker_info.py could output JSON to a file, e.g. /tmp/worker_info.json
# {
#   "repo_url": "...",
#   "worker_class": "...",
#   ...
# }

repo_url=$(jq -r '.repo_url' /tmp/worker_info.json)
worker_class=$(jq -r '.worker_class' /tmp/worker_info.json)

# 2. Clone the worker-specific repo
git clone "$repo_url" /tmp/worker_repo

# 3. Pip install the worker
pip install -e /tmp/worker_repo

# 4. Launch uvicorn with our WorkerAPI, passing needed env vars
echo "Starting WorkerAPI with worker_class=$worker_class"
exec uvicorn serve:app --host 0.0.0.0 --port 8000
