# Troubleshooting Guide - Phase V MVP

## Common Issues and Solutions

### 1. Chat API Not Starting

**Symptoms:**
- Pod stuck in CrashLoopBackOff
- Container exits immediately
- Health check failures

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -l app=chat-api

# View logs
kubectl logs -f deployment/chat-api -c chat-api
kubectl logs -f deployment/chat-api -c daprd

# Describe pod for events
kubectl describe pod -l app=chat-api
```

**Common Causes:**

**A. Missing OpenAI API Key**
```bash
# Check if secret exists
kubectl get secret app-secrets

# Verify secret content
kubectl get secret app-secrets -o jsonpath='{.data.openai-api-key}' | base64 -d

# Recreate secret
kubectl delete secret app-secrets
kubectl create secret generic app-secrets --from-literal=openai-api-key="your-key"
```

**B. Dapr Sidecar Not Ready**
```bash
# Check Dapr installation
dapr status -k

# Reinstall Dapr if needed
dapr uninstall -k
dapr init -k
```

**C. Import Errors**
```bash
# Check if all dependencies are installed
kubectl exec -it deployment/chat-api -c chat-api -- pip list

# Rebuild image with dependencies
docker build -t chat-api:latest -f backend/Dockerfile .
minikube image load chat-api:latest
kubectl rollout restart deployment/chat-api
```

### 2. Tasks Not Persisting

**Symptoms:**
- Tasks created but not returned by list endpoint
- Tasks disappear after pod restart

**Diagnosis:**
```bash
# Check PostgreSQL
kubectl get pods -l app=postgres
kubectl logs -f deployment/postgres

# Check Dapr state store component
kubectl get component statestore

# Test state store directly
kubectl exec -it deployment/chat-api -c daprd -- \
  curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'
```

**Common Causes:**

**A. PostgreSQL Not Running**
```bash
# Check PostgreSQL status
kubectl get pods -l app=postgres

# Check PostgreSQL logs
kubectl logs -f deployment/postgres

# Restart PostgreSQL
kubectl rollout restart deployment/postgres
```

**B. State Store Component Misconfigured**
```bash
# Check component
kubectl get component statestore -o yaml

# Verify connection string
kubectl get secret postgres-secret -o yaml

# Reapply component
kubectl apply -f k8s/dapr/statestore-local.yaml
```

**C. Task Index Not Updated**
- This is a known limitation in MVP
- Task index is maintained separately
- Check create_task.py for index management logic

### 3. Events Not Publishing

**Symptoms:**
- Tasks created but no events in Kafka
- Subscriptions not receiving events

**Diagnosis:**
```bash
# Check Redpanda
kubectl get pods -l app=redpanda
kubectl logs -f deployment/redpanda

# Check Dapr pubsub component
kubectl get component pubsub

# List topics
kubectl exec -it deployment/redpanda -- rpk topic list

# Consume events
kubectl exec -it deployment/redpanda -- rpk topic consume task-events
```

**Common Causes:**

**A. Redpanda Not Running**
```bash
# Check Redpanda status
kubectl get pods -l app=redpanda

# Restart Redpanda
kubectl rollout restart deployment/redpanda
```

**B. PubSub Component Misconfigured**
```bash
# Check component
kubectl get component pubsub -o yaml

# Reapply component
kubectl apply -f k8s/dapr/pubsub-local.yaml
```

**C. Subscription Not Created**
```bash
# List subscriptions
kubectl get subscriptions

# Check specific subscription
kubectl get subscription chat-api-subscription -o yaml

# Reapply subscriptions
kubectl apply -f k8s/dapr/subscription-chat-api.yaml
```

### 4. Chat Endpoint Not Responding

**Symptoms:**
- 500 errors from /api/v1/chat
- Timeout errors
- No response from AI

**Diagnosis:**
```bash
# Check logs
kubectl logs -f deployment/chat-api -c chat-api | grep chat

# Test endpoint directly
kubectl port-forward svc/chat-api 8000:8000
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

**Common Causes:**

**A. OpenAI API Key Invalid**
```bash
# Check environment variable
kubectl exec -it deployment/chat-api -c chat-api -- env | grep OPENAI

# Test OpenAI API directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer your-key"
```

**B. MCP Tools Not Loading**
```bash
# Check if tools are registered
kubectl logs deployment/chat-api -c chat-api | grep "Registered.*tools"

# Should see: "Registered 5 MCP tools"
```

**C. Import Errors**
```bash
# Check Python path
kubectl exec -it deployment/chat-api -c chat-api -- python -c "import sys; print(sys.path)"

# Test imports
kubectl exec -it deployment/chat-api -c chat-api -- \
  python -c "from src.mcp.server import mcp_server; print(mcp_server.tools)"
```

### 5. Docker Compose Issues

**Symptoms:**
- Services not starting
- Network errors
- Connection refused

**Diagnosis:**
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f chat-api
docker-compose logs -f postgres
docker-compose logs -f redpanda

# Check networks
docker network ls
docker network inspect todo-network
```

**Common Causes:**

**A. Port Conflicts**
```bash
# Check if ports are in use
netstat -an | grep 8000
netstat -an | grep 5432
netstat -an | grep 9092

# Stop conflicting services
docker-compose down
```

**B. Environment Variables Not Set**
```bash
# Check .env file
cat backend/.env

# Verify variables are loaded
docker-compose config
```

**C. Volume Permissions**
```bash
# Remove volumes and recreate
docker-compose down -v
docker-compose up -d
```

### 6. Minikube Issues

**Symptoms:**
- Minikube not starting
- Image not found
- DNS resolution failures

**Diagnosis:**
```bash
# Check Minikube status
minikube status

# Check Minikube logs
minikube logs

# Check available resources
minikube ssh -- free -h
minikube ssh -- df -h
```

**Common Causes:**

**A. Insufficient Resources**
```bash
# Stop Minikube
minikube stop

# Start with more resources
minikube start --cpus=4 --memory=8192
```

**B. Image Not Loaded**
```bash
# List images in Minikube
minikube image ls | grep chat-api

# Load image
docker build -t chat-api:latest -f backend/Dockerfile .
minikube image load chat-api:latest

# Verify
minikube image ls | grep chat-api
```

**C. DNS Issues**
```bash
# Check CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system
```

## Debugging Commands

### View All Resources
```bash
kubectl get all
kubectl get components
kubectl get subscriptions
kubectl get secrets
```

### Check Dapr Status
```bash
dapr status -k
kubectl get pods -n dapr-system
```

### View Events
```bash
kubectl get events --sort-by='.lastTimestamp'
```

### Port Forward for Testing
```bash
# Chat API
kubectl port-forward svc/chat-api 8000:8000

# PostgreSQL
kubectl port-forward svc/postgres 5432:5432

# Redpanda
kubectl port-forward svc/redpanda 9092:9092
```

### Execute Commands in Pods
```bash
# Chat API container
kubectl exec -it deployment/chat-api -c chat-api -- bash

# Dapr sidecar
kubectl exec -it deployment/chat-api -c daprd -- sh

# PostgreSQL
kubectl exec -it deployment/postgres -- psql -U todouser -d todoapp
```

### Clean Restart
```bash
# Delete everything
kubectl delete -f k8s/services/
kubectl delete -f k8s/dapr/
kubectl delete -f k8s/local/

# Redeploy
kubectl apply -f k8s/local/
kubectl apply -f k8s/dapr/
kubectl apply -f k8s/services/
```

## Getting Help

If you're still experiencing issues:

1. **Check logs thoroughly:**
   ```bash
   kubectl logs -f deployment/chat-api -c chat-api --tail=100
   kubectl logs -f deployment/chat-api -c daprd --tail=100
   ```

2. **Verify all components:**
   ```bash
   kubectl get components
   kubectl get subscriptions
   kubectl describe component statestore
   kubectl describe component pubsub
   ```

3. **Test individual components:**
   - Test PostgreSQL connection
   - Test Redpanda topics
   - Test Dapr components
   - Test API endpoints

4. **Review configuration:**
   - Check all YAML files
   - Verify environment variables
   - Confirm secrets are set

5. **Start fresh:**
   ```bash
   minikube delete
   minikube start --cpus=4 --memory=8192
   dapr init -k
   # Redeploy everything
   ```
