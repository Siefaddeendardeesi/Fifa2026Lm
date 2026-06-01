#!/usr/bin/env bash
# Deploy to Azure Container Instances
set -euo pipefail

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-fifa2026lm-rg}"
LOCATION="${AZURE_LOCATION:-eastus}"
ACR_NAME="${AZURE_ACR_NAME:-fifa2026lm}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic
az acr build --registry "$ACR_NAME" --image "fifa2026lm:${IMAGE_TAG}" -f docker/Dockerfile .

ACR_LOGIN=$(az acr login-server --name "$ACR_NAME" --output tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name fifa2026lm-api \
  --image "${ACR_LOGIN}/fifa2026lm:${IMAGE_TAG}" \
  --registry-login-server "$ACR_LOGIN" \
  --registry-username "$ACR_NAME" \
  --registry-password "$ACR_PASSWORD" \
  --dns-name-label fifa2026lm-api \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production \
  --cpu 2 --memory 4

echo "Deployed to: http://fifa2026lm-api.${LOCATION}.azurecontainer.io:8000"
