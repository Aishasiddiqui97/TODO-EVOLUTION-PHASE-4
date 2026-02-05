# Quickstart Guide

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Version**: 1.0.0

## Overview

This guide helps developers set up and run the event-driven Todo Chatbot system locally using Minikube and Dapr. The system consists of 5 microservices communicating via events.

---

## Prerequisites

### Required Software

- **Docker Desktop**: 4.25+ with Kubernetes enabled
- **Minikube**: 1.32+ (alternative to Docker Desktop Kubernetes)
- **kubectl**: 1.28+
- **Dapr CLI**: 1.12+
- **Python**: 3.12+
- **Node.js**: 18+
- **Git**: Latest version

### Installation Commands

**macOS** (using Homebrew):
```bash
brew install minikube kubectl dapr/tap/dapr-cli python@3.12 node
```

**Windows** (using Chocolatey):
```bash
choco install minikube kubernetes-cli dapr-cli python nodejs git
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

# Python 3.12
sudo apt update && sudo apt install python3.12 python3-pip

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

---

## Local Development Setup

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
```

### Step 2: Install Dapr on Kubernetes

```bash
# Initialize Dapr on Kubernetes cluster
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
```

**Expected Output**:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   30s  2026-02-05 10:00:00
dapr-sentry            dapr-system  True     Running  1         1.12.0   30s  2026-02-05 10:00:00
dapr-operator          dapr-system  True     Running  1         1.12.0   30s  2026-02-05 10:00:00
dapr-placement         dapr-system  True     Running  1         1.12.0   30s  2026-02-05 10:00:00
```

### Step 3: Deploy Infrastructure

**PostgreSQL**:
```bash
# Deploy PostgreSQL
kubectl apply -f k8s/local/postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

**Redpanda (Kafka-compatible)**:
```bash
# Deploy Redpanda
kubectl apply -f k8s/local/redpanda.yaml

# Wait for Redpanda to be ready
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
```

**MailHog (Email testing)**:
```bash
# Deploy MailHog
kubectl apply -f k8s/local/mailhog.yaml

# Wait for MailHog to be ready
kubectl wait --for=condition=ready pod -l app=mailhog --timeout=60s
```

### Step 4: Deploy Dapr Components

```bash
# Apply Dapr component configurations
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/pubsub-local.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/statestore-local.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/secretstore-local.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/local-secrets.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/jobs-config.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/resiliency.yaml
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/tracing.yaml

# Apply event subscriptions
kubectl apply -f specs/001-event-driven-todo/contracts/dapr/subscription-*.yaml

# Verify components
dapr components -k
```

### Step 5: Build and Deploy Services

**Build Docker Images**:
```bash
# Set Minikube Docker environment
eval $(minikube docker-env)

# Build all service images
docker build -t chat-api:latest backend/src/services/chat-api/
docker build -t recurring-task:latest backend/src/services/recurring-task/
docker build -t notification:latest backend/src/services/notification/
docker build -t audit-log:latest backend/src/services/audit-log/
docker build -t websocket-sync:latest backend/src/services/websocket-sync/
```

**Deploy Services**:
```bash
# Deploy all microservices
kubectl apply -f k8s/base/chat-api/
kubectl apply -f k8s/base/recurring-task/
kubectl apply -f k8s/base/notification/
kubectl apply -f k8s/base/audit-log/
kubectl apply -f k8s/base/websocket-sync/

# Wait for all services to be ready
kubectl wait --for=condition=ready pod -l app=chat-api --timeout=120s
kubectl wait --for=condition=ready pod -l app=recurring-task --timeout=120s
kubectl wait --for=condition=ready pod -l app=notification --timeout=120s
kubectl wait --for=condition=ready pod -l app=audit-log --timeout=120s
kubectl wait --for=condition=ready pod -l app=websocket-sync --timeout=120s
```

### Step 6: Deploy Frontend

```bash
# Install frontend dependencies
cd frontend
npm install

# Build frontend
npm run build

# Deploy frontend to Kubernetes
kubectl apply -f k8s/base/frontend/

# Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=frontend --timeout=60s
```

### Step 7: Access the Application

**Port Forward Services**:
```bash
# Chat API
kubectl port-forward svc/chat-api 8000:8000 &

# WebSocket Sync
kubectl port-forward svc/websocket-sync 8001:8001 &

# Frontend
kubectl port-forward svc/frontend 3000:3000 &

# MailHog UI (email testing)
kubectl port-forward svc/mailhog 8025:8025 &
```

**Access URLs**:
- Frontend: http://localhost:3000
- Chat API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8001/ws
- MailHog UI: http://localhost:8025

---

## Development Workflow

### Running Services Locally (Without Kubernetes)

For faster development iteration, run services locally with Dapr sidecar:

**Terminal 1 - Chat API**:
```bash
cd backend/src/services/chat-api
pip install -r requirements.txt

dapr run \
  --app-id chat-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../../../../specs/001-event-driven-todo/contracts/dapr/ \
  -- python main.py
```

**Terminal 2 - Recurring Task Service**:
```bash
cd backend/src/services/recurring-task
pip install -r requirements.txt

dapr run \
  --app-id recurring-task \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --components-path ../../../../specs/001-event-driven-todo/contracts/dapr/ \
  -- python main.py
```

**Terminal 3 - Notification Service**:
```bash
cd backend/src/services/notification
pip install -r requirements.txt

dapr run \
  --app-id notification \
  --app-port 8003 \
  --dapr-http-port 3503 \
  --components-path ../../../../specs/001-event-driven-todo/contracts/dapr/ \
  -- python main.py
```

**Terminal 4 - Frontend**:
```bash
cd frontend
npm run dev
```

**Note**: You'll still need PostgreSQL, Redpanda, and MailHog running (can use Docker Compose for these).

### Docker Compose for Infrastructure Only

```yaml
# docker-compose.infrastructure.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: todo
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"

  redpanda:
    image: vectorized/redpanda:latest
    command:
      - redpanda start
      - --smp 1
      - --overprovisioned
      - --kafka-addr PLAINTEXT://0.0.0.0:9092
    ports:
      - "9092:9092"

  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"
      - "8025:8025"
```

**Start Infrastructure**:
```bash
docker-compose -f docker-compose.infrastructure.yml up -d
```

---

## Testing

### Unit Tests

```bash
# Run all unit tests
cd backend
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

### Integration Tests

```bash
# Run integration tests (requires Dapr and infrastructure)
pytest tests/integration/ -v
```

### Contract Tests

```bash
# Test event schemas
pytest tests/contract/test_event_schemas.py -v

# Test API contracts
pytest tests/contract/test_api_contracts.py -v
```

### End-to-End Tests

```bash
# Run E2E tests against running system
cd frontend
npm run test:e2e
```

---

## Monitoring and Debugging

### View Logs

**All Services**:
```bash
kubectl logs -l app=chat-api -f
kubectl logs -l app=recurring-task -f
kubectl logs -l app=notification -f
kubectl logs -l app=audit-log -f
kubectl logs -l app=websocket-sync -f
```

**Dapr Sidecars**:
```bash
kubectl logs -l app=chat-api -c daprd -f
```

### View Dapr Dashboard

```bash
# Start Dapr dashboard
dapr dashboard -k

# Access at http://localhost:8080
```

**Dashboard Features**:
- View all Dapr applications
- Monitor component health
- View event subscriptions
- Inspect state store
- View distributed traces

### View Metrics

**Prometheus** (if installed):
```bash
kubectl port-forward svc/prometheus 9090:9090
# Access at http://localhost:9090
```

**Grafana** (if installed):
```bash
kubectl port-forward svc/grafana 3001:3000
# Access at http://localhost:3001
```

### View Distributed Traces

**Zipkin**:
```bash
kubectl port-forward svc/zipkin 9411:9411
# Access at http://localhost:9411
```

### Debug Event Flow

**Publish Test Event**:
```bash
dapr publish \
  --publish-app-id chat-api \
  --pubsub pubsub \
  --topic task-events \
  --data '{"eventType":"task.created","userId":"test-user","payload":{"task":{"id":"test-123","title":"Test Task"}}}'
```

**Check Event Subscriptions**:
```bash
kubectl get subscriptions
```

---

## Common Issues and Solutions

### Issue: Pods Not Starting

**Check Pod Status**:
```bash
kubectl get pods
kubectl describe pod <pod-name>
```

**Common Causes**:
- Insufficient resources: Increase Minikube memory/CPU
- Image pull errors: Verify images built with Minikube Docker env
- Dapr sidecar injection failed: Check Dapr installation

### Issue: Events Not Being Delivered

**Check Dapr Components**:
```bash
dapr components -k
```

**Check Subscriptions**:
```bash
kubectl get subscriptions
kubectl describe subscription <subscription-name>
```

**Check Redpanda**:
```bash
kubectl exec -it <redpanda-pod> -- rpk topic list
kubectl exec -it <redpanda-pod> -- rpk topic consume task-events
```

### Issue: State Not Persisting

**Check PostgreSQL**:
```bash
kubectl exec -it <postgres-pod> -- psql -U todo -d todo_db -c "SELECT * FROM dapr_state LIMIT 10;"
```

**Check State Store Component**:
```bash
kubectl describe component statestore
```

### Issue: WebSocket Connection Failing

**Check WebSocket Service**:
```bash
kubectl logs -l app=websocket-sync -f
```

**Test WebSocket Connection**:
```bash
wscat -c ws://localhost:8001/ws?token=<jwt-token>
```

---

## Cleanup

### Stop Services

```bash
# Delete all deployments
kubectl delete -f k8s/base/

# Delete Dapr components
kubectl delete -f specs/001-event-driven-todo/contracts/dapr/

# Delete infrastructure
kubectl delete -f k8s/local/
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

## Next Steps

1. **Implement Services**: Follow tasks.md for implementation order
2. **Add Tests**: Write unit, integration, and E2E tests
3. **Configure CI/CD**: Set up GitHub Actions pipeline
4. **Deploy to Cloud**: Follow cloud deployment guide
5. **Monitor Production**: Set up alerts and dashboards

---

## Useful Commands Reference

```bash
# Minikube
minikube status
minikube dashboard
minikube service list
minikube logs

# kubectl
kubectl get all
kubectl get pods -w
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f
kubectl exec -it <pod-name> -- /bin/bash

# Dapr
dapr status -k
dapr dashboard -k
dapr components -k
dapr list -k

# Docker (with Minikube)
eval $(minikube docker-env)
docker images
docker ps
```

---

## Support

- **Documentation**: See specs/001-event-driven-todo/
- **Issues**: Report at GitHub repository
- **Dapr Docs**: https://docs.dapr.io
- **Kubernetes Docs**: https://kubernetes.io/docs

---

## Summary

This quickstart guide covers:
- ✅ Prerequisites and installation
- ✅ Local development setup with Minikube and Dapr
- ✅ Infrastructure deployment (PostgreSQL, Redpanda, MailHog)
- ✅ Service deployment and access
- ✅ Development workflow options
- ✅ Testing strategies
- ✅ Monitoring and debugging
- ✅ Common issues and solutions
- ✅ Cleanup procedures

Follow this guide to get the event-driven Todo Chatbot running locally in under 30 minutes.
