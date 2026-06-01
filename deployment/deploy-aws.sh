#!/usr/bin/env bash
# Deploy to AWS ECS Fargate
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO="${ECR_REPO:-fifa2026lm}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
CLUSTER="${ECS_CLUSTER:-fifa2026lm-cluster}"

aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com"

aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$AWS_REGION" 2>/dev/null || \
  aws ecr create-repository --repository-name "$ECR_REPO" --region "$AWS_REGION"

ECR_URI="$(aws ecr describe-repositories --repository-names "$ECR_REPO" --query 'repositories[0].repositoryUri' --output text --region "$AWS_REGION")"

docker build -t "$ECR_REPO:$IMAGE_TAG" -f docker/Dockerfile .
docker tag "$ECR_REPO:$IMAGE_TAG" "$ECR_URI:$IMAGE_TAG"
docker push "$ECR_URI:$IMAGE_TAG"

aws ecs describe-clusters --clusters "$CLUSTER" --region "$AWS_REGION" 2>/dev/null || \
  aws ecs create-cluster --cluster-name "$CLUSTER" --region "$AWS_REGION"

echo "Image pushed to $ECR_URI:$IMAGE_TAG"
echo "Register task definition and create ECS service with this image URI."
