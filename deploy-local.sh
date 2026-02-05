#!/bin/bash
# Deployment script for Event-Driven Todo Chatbot - Phase V MVP
# Deploys to local Kubernetes (Minikube)

set -e

echo "🚀 Event-Driven Todo Chatbot - Phase V Deployment"
echo "=================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v minikube &> /dev/null; then
    echo "❌ minikube not found. Please install minikube."
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo "❌ dapr CLI not found. Please install Dapr CLI."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ docker not found. Please install Docker."
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Start Minikube if not running
echo "🔧 Starting Minikube..."
if ! minikube status &> /dev/null; then
    minikube start --cpus=4 --memory=8192
else
    echo "✅ Minikube already running"
fi
echo ""

# Initialize Dapr
echo "🔧 Initializing Dapr on Kubernetes..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    dapr init -k
else
    echo "✅ Dapr already initialized"
fi
echo ""

# Create secrets
echo "🔐 Creating secrets..."
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
kubectl create secret generic app-secrets \
    --from-literal=openai-api-key="$OPENAI_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Secrets created"
echo ""

# Deploy infrastructure
echo "📦 Deploying infrastructure..."
kubectl apply -f k8s/local/postgres.yaml
kubectl apply -f k8s/local/redpanda.yaml
echo "✅ Infrastructure deployed"
echo ""

# Wait for infrastructure
echo "⏳ Waiting for infrastructure to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
echo "✅ Infrastructure ready"
echo ""

# Deploy Dapr components
echo "🔧 Deploying Dapr components..."
kubectl apply -f k8s/dapr/
echo "✅ Dapr components deployed"
echo ""

# Build and load Chat API image
echo "🏗️  Building Chat API image..."
docker build -t chat-api:latest -f backend/Dockerfile .
echo "✅ Image built"
echo ""

echo "📤 Loading image into Minikube..."
minikube image load chat-api:latest
echo "✅ Image loaded"
echo ""

# Deploy Chat API
echo "🚀 Deploying Chat API..."
kubectl apply -f k8s/services/chat-api-deployment.yaml
kubectl apply -f k8s/services/chat-api-service.yaml
echo "✅ Chat API deployed"
echo ""

# Wait for Chat API
echo "⏳ Waiting for Chat API to be ready..."
kubectl wait --for=condition=ready pod -l app=chat-api --timeout=180s
echo "✅ Chat API ready"
echo ""

# Display status
echo "📊 Deployment Status"
echo "===================="
kubectl get pods
echo ""

# Port forwarding instructions
echo "🌐 Access Instructions"
echo "======================"
echo ""
echo "To access the Chat API, run:"
echo "  kubectl port-forward svc/chat-api 8000:8000"
echo ""
echo "Then visit:"
echo "  http://localhost:8000"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs"
echo ""
echo "Health Check:"
echo "  curl http://localhost:8000/health"
echo ""
echo "✅ Deployment complete!"
