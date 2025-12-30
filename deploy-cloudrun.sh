#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🚀 Narratives Media - Cloud Run Deployment Script
# ═══════════════════════════════════════════════════════════════

# Set your project details
PROJECT_ID="your-gcp-project-id"        # <-- তোমার GCP Project ID দাও
REGION="asia-south1"                     # Mumbai region (closest to BD)
SERVICE_NAME="narratives-icebreaker"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🎬 Narratives Media - Cloud Run Deployment"
echo "==========================================="

# Step 1: Set project
echo "📌 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Step 2: Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Step 3: Build and push Docker image
echo "🐳 Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Step 4: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 10

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your app URL will be shown above"
