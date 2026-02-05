#!/bin/bash

# Deploy Event-Driven Todo Chatbot to Cloud Kubernetes
# Supports Azure AKS, AWS EKS, and Google GKE

set -e

echo "☁️  Deploying Event-Driven Todo Chatbot to Cloud"
echo "================================================"

# Parse arguments
ENVIRONMENT=${1:-staging}
CLOUD_PROVIDER=${2:-azure}

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

if [[ "$CLOUD_PROVIDER" != "azure" && "$CLOUD_PROVIDER" != "aws" && "$CLOUD_PROVIDER" != "gcp" ]]; then
    echo "❌ Invalid cloud provider. Use 'azure', 'aws', or 'gcp'"
    exit 1
fi

echo "📋 Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Cloud Provider: $CLOUD_PROVIDER"

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Please install: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Check cloud-specific CLI
case $CLOUD_PROVIDER in
    azure)
        if ! command -v az &> /dev/null; then
            echo "❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
            exit 1
        fi
        ;;
    aws)
        if ! command -v aws &> /dev/null; then
            echo "❌ AWS CLI not found. Please install: https://aws.amazon.com/cli/"
            exit 1
        fi
        ;;
    gcp)
        if ! command -v gcloud &> /dev/null; then
            echo "❌ Google Cloud SDK not found. Please install: https://cloud.google.com/sdk/docs/install"
            exit 1
        fi
        ;;
esac

echo "✅ All prerequisites found"

# Set kubectl context
echo ""
echo "🔧 Configuring kubectl context..."

case $CLOUD_PROVIDER in
    azure)
        RESOURCE_GROUP="todo-chatbot-rg"
        CLUSTER_NAME="todo-chatbot-aks"
        az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --overwrite-existing
        ;;
    aws)
        CLUSTER_NAME="todo-chatbot-eks"
        REGION="us-east-1"
        aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION
        ;;
    gcp)
        PROJECT_ID="todo-chatbot"
        CLUSTER_NAME="todo-chatbot-gke"
        ZONE="us-central1-a"
        gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID
        ;;
esac

echo "✅ kubectl context configured"

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
NAMESPACE="todo-chatbot-prod"
echo ""
echo "🔧 Creating namespace: $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create secrets (if not exists)
echo ""
echo "🔐 Checking secrets..."

case $CLOUD_PROVIDER in
    azure)
        # Azure Service Bus connection string
        if ! kubectl get secret azure-servicebus -n $NAMESPACE &> /dev/null; then
            echo "⚠️  Azure Service Bus secret not found. Please create it manually:"
            echo "  kubectl create secret generic azure-servicebus --from-literal=connectionString='<connection-string>' -n $NAMESPACE"
        fi

        # Azure Cosmos DB credentials
        if ! kubectl get secret azure-cosmosdb -n $NAMESPACE &> /dev/null; then
            echo "⚠️  Azure Cosmos DB secret not found. Please create it manually:"
            echo "  kubectl create secret generic azure-cosmosdb --from-literal=url='<url>' --from-literal=masterKey='<key>' -n $NAMESPACE"
        fi

        # Azure Key Vault credentials
        if ! kubectl get secret azure-credentials -n $NAMESPACE &> /dev/null; then
            echo "⚠️  Azure credentials secret not found. Please create it manually:"
            echo "  kubectl create secret generic azure-credentials --from-literal=clientSecret='<secret>' -n $NAMESPACE"
        fi
        ;;
    aws)
        # AWS credentials
        if ! kubectl get secret aws-credentials -n $NAMESPACE &> /dev/null; then
            echo "⚠️  AWS credentials secret not found. Please create it manually:"
            echo "  kubectl create secret generic aws-credentials --from-literal=accessKey='<key>' --from-literal=secretKey='<secret>' -n $NAMESPACE"
        fi
        ;;
esac

# Deploy Dapr components
echo ""
echo "🔧 Deploying Dapr components..."
case $CLOUD_PROVIDER in
    azure)
        kubectl apply -f k8s/dapr/pubsub-cloud-azure.yaml -n $NAMESPACE
        kubectl apply -f k8s/dapr/statestore-cloud-azure.yaml -n $NAMESPACE
        kubectl apply -f k8s/dapr/secretstore-cloud-azure.yaml -n $NAMESPACE
        ;;
    aws)
        kubectl apply -f k8s/dapr/secretstore-cloud-aws.yaml -n $NAMESPACE
        # Note: Add AWS-specific PubSub and State Store components
        ;;
esac

kubectl apply -f k8s/dapr/config.yaml -n $NAMESPACE

# Deploy observability stack
echo ""
echo "🔧 Deploying observability stack..."
kubectl apply -f k8s/observability/ -n $NAMESPACE

# Deploy services using Kustomize
echo ""
echo "🔧 Deploying services..."
cd "$(dirname "$0")/.."
kubectl apply -k k8s/overlays/cloud

# Wait for deployments to be ready
echo ""
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/chat-api -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/recurring-task -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/notification -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/websocket-sync -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/audit-log -n $NAMESPACE --timeout=600s

# Get ingress URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
kubectl get pods -n $NAMESPACE

echo ""
echo "🌐 Ingress:"
kubectl get ingress -n $NAMESPACE

INGRESS_HOST=$(kubectl get ingress todo-chatbot-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "Not configured")
echo ""
echo "🌐 Access URLs:"
echo "  API: https://$INGRESS_HOST"
echo "  WebSocket: wss://ws.$INGRESS_HOST"

echo ""
echo "📝 Useful commands:"
echo "  View logs: kubectl logs -f deployment/chat-api -n $NAMESPACE"
echo "  Scale: kubectl scale deployment/chat-api --replicas=5 -n $NAMESPACE"
echo "  Rollback: kubectl rollout undo deployment/chat-api -n $NAMESPACE"
echo "  Dashboard: kubectl proxy (then visit http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/)"

echo ""
echo "🎉 Deployment successful!"
