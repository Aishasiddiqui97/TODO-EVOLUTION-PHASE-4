#!/bin/bash

# Deploy Event-Driven Todo Chatbot to Minikube
# This script sets up the entire application stack locally

set -e

echo "🚀 Deploying Event-Driven Todo Chatbot to Minikube"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube not found. Please install: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Please install: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

echo "✅ All prerequisites found"

# Start Minikube if not running
echo ""
echo "🔧 Starting Minikube..."
if ! minikube status &> /dev/null; then
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo "✅ Minikube already running"
fi

# Enable required addons
echo ""
echo "🔧 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Initialize Dapr on Kubernetes
echo ""
echo "🔧 Initializing Dapr..."
if ! kubectl get namespace dapr-system &> /dev/null; then
    dapr init -k
else
    echo "✅ Dapr already initialized"
fi

# Wait for Dapr to be ready
echo "⏳ Waiting for Dapr to be ready..."
kubectl wait --for=condition=ready pod -l app=dapr-operator -n dapr-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=dapr-sidecar-injector -n dapr-system --timeout=300s

# Create namespace
echo ""
echo "🔧 Creating namespace..."
kubectl create namespace todo-chatbot-local --dry-run=client -o yaml | kubectl apply -f -

# Build Docker images
echo ""
echo "🏗️  Building Docker images..."
eval $(minikube docker-env)

cd "$(dirname "$0")/.."

docker build -f backend/src/services/chat-api/Dockerfile -t todo-chatbot/chat-api:latest .
docker build -f backend/src/services/recurring-task/Dockerfile -t todo-chatbot/recurring-task:latest .
docker build -f backend/src/services/notification/Dockerfile -t todo-chatbot/notification:latest .
docker build -f backend/src/services/websocket-sync/Dockerfile -t todo-chatbot/websocket-sync:latest .
docker build -f backend/src/services/audit-log/Dockerfile -t todo-chatbot/audit-log:latest .

echo "✅ Docker images built successfully"

# Deploy Dapr components
echo ""
echo "🔧 Deploying Dapr components..."
kubectl apply -f k8s/dapr/ -n todo-chatbot-local

# Deploy observability stack
echo ""
echo "🔧 Deploying observability stack..."
kubectl apply -f k8s/observability/ -n todo-chatbot-local

# Deploy services using Kustomize
echo ""
echo "🔧 Deploying services..."
kubectl apply -k k8s/overlays/local

# Wait for deployments to be ready
echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/chat-api -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/recurring-task -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/notification -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/websocket-sync -n todo-chatbot-local --timeout=300s
kubectl wait --for=condition=available deployment/audit-log -n todo-chatbot-local --timeout=300s

# Get service URLs
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
kubectl get pods -n todo-chatbot-local

echo ""
echo "🌐 Access URLs:"
echo "  Chat API: http://$(minikube ip):$(kubectl get svc chat-api -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')"
echo "  WebSocket: ws://$(minikube ip):$(kubectl get svc websocket-sync -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')"
echo "  Prometheus: http://$(minikube ip):$(kubectl get svc prometheus -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')"
echo "  Zipkin: http://$(minikube ip):$(kubectl get svc zipkin -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')"

echo ""
echo "📝 Useful commands:"
echo "  View logs: kubectl logs -f deployment/chat-api -n todo-chatbot-local"
echo "  Port forward: kubectl port-forward svc/chat-api 8001:80 -n todo-chatbot-local"
echo "  Dashboard: minikube dashboard"
echo "  Stop: minikube stop"
echo "  Delete: minikube delete"

echo ""
echo "🎉 Deployment successful!"
