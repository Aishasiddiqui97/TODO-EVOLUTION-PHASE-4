# Quick Start Guide

Get the Event-Driven Todo Chatbot running locally in under 10 minutes using automated deployment scripts.

---

## Prerequisites

Install the following software:

- **Docker Desktop** (with Kubernetes enabled) OR **Minikube** (1.32+)
- **kubectl** (1.28+)
- **Dapr CLI** (1.12+)
- **Git**

### Quick Install

**macOS** (Homebrew):
```bash
brew install minikube kubectl dapr/tap/dapr-cli
```

**Windows** (Chocolatey):
```bash
choco install minikube kubernetes-cli dapr-cli
```

**Linux** (Ubuntu/Debian):
```bash
# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl

# Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

---

## Automated Deployment (Recommended)

### Local Development with Minikube

**Linux/Mac**:
```bash
chmod +x scripts/deploy-local.sh
./scripts/deploy-local.sh
```

**Windows** (Git Bash or WSL):
```bash
bash scripts/deploy-local.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Start Minikube with appropriate resources
3. ✅ Initialize Dapr on Kubernetes
4. ✅ Build Docker images for all services
5. ✅ Deploy Dapr components (PubSub, State Store, Secrets)
6. ✅ Deploy observability stack (Prometheus, Zipkin)
7. ✅ Deploy all 5 microservices
8. ✅ Display access URLs and useful commands

**Deployment time**: ~5-10 minutes

---

## Cloud Deployment

Deploy to Azure AKS, AWS EKS, or Google GKE:

```bash
# Azure
chmod +x scripts/deploy-cloud.sh
./scripts/deploy-cloud.sh production azure

# AWS
./scripts/deploy-cloud.sh production aws

# GCP
./scripts/deploy-cloud.sh production gcp
```

See [Cloud Deployment Guide](CLOUD_DEPLOYMENT_COMPLETE.md) for prerequisites and configuration.

---

## Access the Application

After deployment completes, access the services:

### Get Service URLs

```bash
# Minikube IP
MINIKUBE_IP=$(minikube ip)

# Service NodePorts
CHAT_API_PORT=$(kubectl get svc chat-api -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')
WEBSOCKET_PORT=$(kubectl get svc websocket-sync -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')
PROMETHEUS_PORT=$(kubectl get svc prometheus -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')
ZIPKIN_PORT=$(kubectl get svc zipkin -n todo-chatbot-local -o jsonpath='{.spec.ports[0].nodePort}')

echo "Chat API: http://$MINIKUBE_IP:$CHAT_API_PORT"
echo "WebSocket: ws://$MINIKUBE_IP:$WEBSOCKET_PORT"
echo "Prometheus: http://$MINIKUBE_IP:$PROMETHEUS_PORT"
echo "Zipkin: http://$MINIKUBE_IP:$ZIPKIN_PORT"
```

### Or Use Port Forwarding

```bash
# Chat API
kubectl port-forward svc/chat-api 8001:80 -n todo-chatbot-local &

# WebSocket Sync
kubectl port-forward svc/websocket-sync 8004:80 -n todo-chatbot-local &

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n todo-chatbot-local &

# Zipkin
kubectl port-forward svc/zipkin 9411:9411 -n todo-chatbot-local &
```

**Access URLs**:
- Chat API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- WebSocket: ws://localhost:8004/ws
- Prometheus: http://localhost:9090
- Zipkin: http://localhost:9411

---

## Test the API

### Health Check

```bash
curl http://localhost:8001/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "chat-api",
  "version": "1.0.0"
}
```

### Create a Task

```bash
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Get milk, eggs, and bread",
    "priority": "high",
    "userId": "user-001"
  }'
```

### List Tasks

```bash
curl http://localhost:8001/api/v1/tasks?userId=user-001
```

### Chat with AI

```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my high-priority tasks",
    "userId": "user-001"
  }'
```

### Search Tasks

```bash
curl -X POST http://localhost:8001/api/v1/tasks/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me high-priority tasks due this week",
    "userId": "user-001"
  }'
```

---

## Frontend Setup

The frontend is a Next.js application with real-time WebSocket synchronization.

### Install and Run

```bash
cd frontend
npm install

# Development mode
npm run dev

# Production build
npm run build
npm start
```

**Access**: http://localhost:3000

### Configure API Endpoints

Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8004
```

---

## Monitoring and Debugging

### View Service Logs

```bash
# All services
kubectl logs -l app=chat-api -n todo-chatbot-local -f
kubectl logs -l app=recurring-task -n todo-chatbot-local -f
kubectl logs -l app=notification -n todo-chatbot-local -f
kubectl logs -l app=websocket-sync -n todo-chatbot-local -f
kubectl logs -l app=audit-log -n todo-chatbot-local -f

# Dapr sidecars
kubectl logs -l app=chat-api -c daprd -n todo-chatbot-local -f
```

### Dapr Dashboard

```bash
dapr dashboard -k
```

Access at http://localhost:8080 to view:
- All Dapr applications
- Component health
- Event subscriptions
- State store contents
- Distributed traces

### View Metrics

**Prometheus**: http://localhost:9090
- Query metrics: `dapr_http_server_request_count`
- View service health and performance

**Zipkin**: http://localhost:9411
- View distributed traces
- Analyze request flows across services

### Check Service Status

```bash
# All pods
kubectl get pods -n todo-chatbot-local

# Service endpoints
kubectl get svc -n todo-chatbot-local

# Dapr components
dapr components -k

# Event subscriptions
kubectl get subscriptions -n todo-chatbot-local
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-chatbot-local
kubectl describe pod <pod-name> -n todo-chatbot-local

# Check logs
kubectl logs <pod-name> -n todo-chatbot-local
kubectl logs <pod-name> -c daprd -n todo-chatbot-local
```

**Common Issues**:
- Insufficient resources: Increase Minikube memory/CPU
  ```bash
  minikube delete
  minikube start --cpus=4 --memory=8192
  ```
- Image pull errors: Verify images built with Minikube Docker env
  ```bash
  eval $(minikube docker-env)
  docker images | grep todo-chatbot
  ```

### Events Not Being Delivered

```bash
# Check Dapr components
dapr components -k

# Check subscriptions
kubectl get subscriptions -n todo-chatbot-local

# Check Redis (PubSub/State Store)
kubectl exec -it deployment/redis -n todo-chatbot-local -- redis-cli
> KEYS *
> GET <key>
```

### WebSocket Connection Failing

```bash
# Check WebSocket service
kubectl logs -l app=websocket-sync -n todo-chatbot-local -f

# Test connection
wscat -c ws://localhost:8004/ws?userId=user-001
```

---

## Cleanup

### Stop Services

```bash
# Delete all deployments
kubectl delete namespace todo-chatbot-local

# Or use Kustomize
kubectl delete -k k8s/overlays/local
```

### Uninstall Dapr

```bash
dapr uninstall --kubernetes
```

### Stop Minikube

```bash
minikube stop
# or
minikube delete  # Complete cleanup
```

---

## Development Workflow

For faster development iteration, run services locally with Dapr CLI instead of Kubernetes.

See [Development Guide](specs/001-event-driven-todo/quickstart.md) for:
- Running services locally with Dapr CLI
- Docker Compose for infrastructure only
- Unit, integration, and E2E testing
- Debugging event flows
- Common development issues

---

## Architecture Overview

The system consists of 5 microservices:

1. **Chat API** (Port 8001) - Natural language interface with OpenAI Agents SDK
2. **Recurring Task Service** (Port 8002) - Processes recurring task patterns
3. **Notification Service** (Port 8003) - In-app and email notifications
4. **WebSocket Sync Service** (Port 8004) - Real-time synchronization
5. **Audit Log Service** (Port 8005) - Immutable audit trail

**Event-Driven Communication**:
- Dapr PubSub (Redis) for event messaging
- Dapr State Store (Redis) for persistence
- Dapr Secrets API for configuration

See [README.md](README.md) for detailed architecture diagrams and documentation.

---

## Documentation

- **[README.md](README.md)** - Comprehensive system documentation
- **[Detailed Quickstart](specs/001-event-driven-todo/quickstart.md)** - Step-by-step manual setup
- **[Deployment Guide](DEPLOYMENT_TESTING_GUIDE.md)** - Testing and validation
- **[Implementation Progress](IMPLEMENTATION_PROGRESS.md)** - 127/139 tasks (91%)
- **[Cloud Deployment](CLOUD_DEPLOYMENT_COMPLETE.md)** - Azure/AWS/GCP setup
- **[User Stories](USER_STORY_*.md)** - Feature completion reports

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/todo-chatbot/issues)
- **Documentation**: See `specs/001-event-driven-todo/`
- **Dapr Docs**: https://docs.dapr.io
- **Kubernetes Docs**: https://kubernetes.io/docs

---

## Summary

✅ **Automated deployment** with `scripts/deploy-local.sh`
✅ **5 microservices** with event-driven architecture
✅ **Real-time sync** via WebSocket
✅ **AI-powered** natural language interface
✅ **Production-ready** with observability and monitoring

**Get started in under 10 minutes!**
