# syntax=docker/dockerfile:1
FROM python:3.11.4

WORKDIR /app

# Install any system dependencies needed for building wheels, Git, etc.
RUN apt-get update && apt-get install -y git

# Copy only the requirements for the generic worker runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your generic worker code (autoppia_sdk)
COPY . /app

# Optionally define build args if you want them at build time
ARG WORKER_TEMPLATE_REPO_URL
ARG WORKER_ID

# Expose the FastAPI port
EXPOSE 8000

# We assume these become environment variables inside the container as well
ENV WORKER_TEMPLATE_REPO_URL=${WORKER_TEMPLATE_REPO_URL}
ENV WORKER_ID=${WORKER_ID}

# Copy or set your run.sh as entrypoint
RUN chmod +x /app/run.sh
ENTRYPOINT ["/app/run.sh"]
