#!/usr/bin/env bash
# Deploy to Google Cloud Run
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-fifa2026lm-api}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

gcloud builds submit --tag "$IMAGE" --file docker/Dockerfile .

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "ENVIRONMENT=production" \
  --memory 2Gi \
  --cpu 2

gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)'
