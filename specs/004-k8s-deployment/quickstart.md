# Quickstart: Kubernetes Deployment

**Feature**: 004-k8s-deployment
**Date**: 2026-02-03
**Purpose**: Quick guide to deploy the Todo Chatbot application to local Kubernetes

## Prerequisites

Before starting, ensure you have:

1. **Minikube** installed and running
   ```bash
   minikube version
   minikube status
   ```

2. **kubectl** configured to use minikube context
   ```bash
   kubectl config current-context  # Should show "minikube"
   ```

3. **Docker** installed and accessible
   ```bash
   docker --version
   ```

4. **Helm** installed (v3.x)
   ```bash
   helm version
   ```

5. **AI Tools** installed and configured:
   - Docker AI (Gordon) or Claude Code
   - kubectl-ai
   - kagent

6. **Application Source Code** from Phase III:
   - `backend/` directory with FastAPI application
   - `frontend/` directory with ChatKit UI

## Quick Start (5 Steps)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# Verify cluster is running
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

### Step 2: Generate Dockerfiles (AI-Driven)

**Using Docker AI or Claude Code:**

```bash
# Prompt for backend Dockerfile
"Generate a production-ready Dockerfile for a Python 3.11 FastAPI backend application.
Base image: python:3.11-alpine
Dependencies: backend/requirements.txt
Entry point: uvicorn main:app --host 0.0.0.0 --port 8000
Health check: GET /health endpoint
Use multi-stage build, run as non-root user."

# Save output to: deployment/dockerfiles/backend.Dockerfile

# Prompt for frontend Dockerfile
"Generate a production-ready Dockerfile for a React frontend application.
Base image: node:18-alpine for build, nginx:alpine for runtime
Dependencies: frontend/package.json
Build command: npm run build
Serve static files with nginx on port 80
Use multi-stage build, run as non-root user."

# Save output to: deployment/dockerfiles/frontend.Dockerfile
```

**Review and Commit:**
```bash
# Review generated Dockerfiles
cat deployment/dockerfiles/backend.Dockerfile
cat deployment/dockerfiles/frontend.Dockerfile

# Commit to Git
git add deployment/dockerfiles/
git commit -m "feat(deploy): add AI-generated Dockerfiles for backend and frontend"
```

### Step 3: Build Container Images

```bash
# Build backend image
docker build -t todo-backend:v1.0.0 \
  -f deployment/dockerfiles/backend.Dockerfile \
  ./backend

# Build frontend image
docker build -t todo-frontend:v1.0.0 \
  -f deployment/dockerfiles/frontend.Dockerfile \
  ./frontend

# Verify images exist
docker images | grep todo-
```

**Expected Output**:
```
todo-backend    v1.0.0    abc123def456    2 minutes ago    180MB
todo-frontend   v1.0.0    def456abc123    1 minute ago     45MB
```

### Step 4: Generate and Deploy Helm Chart (AI-Driven)

**Using kubectl-ai:**

```bash
# Prompt for Helm chart generation
"Generate a Helm chart named 'todo-chatbot' with the following components:

Backend:
- Image: todo-backend:v1.0.0
- Replicas: 3
- Port: 8000
- Service type: ClusterIP
- Health check: /health
- Resources: 256Mi/250m CPU requests, 512Mi/500m CPU limits

Frontend:
- Image: todo-frontend:v1.0.0
- Replicas: 1
- Port: 80
- Service type: NodePort (port 30080)
- Health check: /
- Resources: 128Mi/100m CPU requests, 256Mi/200m CPU limits

Include rolling update strategy with maxUnavailable: 0 and maxSurge: 1."

# Save output to: deployment/helm/todo-chatbot/
```

**Review and Deploy:**
```bash
# Review generated Helm chart
helm lint deployment/helm/todo-chatbot/

# Commit to Git
git add deployment/helm/
git commit -m "feat(deploy): add AI-generated Helm chart for todo-chatbot"

# Deploy using kubectl-ai
"Deploy the todo-chatbot Helm chart to the default namespace.
Chart path: deployment/helm/todo-chatbot/
Release name: todo-chatbot
Wait for all pods to be ready (timeout: 5 minutes)."
```

**Alternative (Manual Helm Command):**
```bash
helm install todo-chatbot deployment/helm/todo-chatbot/ \
  --namespace default \
  --wait \
  --timeout 5m
```

### Step 5: Verify Deployment (AI-Driven)

**Using kagent:**

```bash
# Prompt for health check
"Check the health of the todo-chatbot deployment in the default namespace.
Analyze all components (backend, frontend) and their services.
Provide recommendations if any issues are detected."
```

**Alternative (Manual Verification):**
```bash
# Check pods
kubectl get pods -l app=todo-chatbot

# Check services
kubectl get services -l app=todo-chatbot

# Get frontend URL
minikube service todo-chatbot-frontend --url
```

**Expected Output**:
```
NAME                                    READY   STATUS    RESTARTS   AGE
todo-chatbot-backend-7d9f8c6b5d-abc12   1/1     Running   0          2m
todo-chatbot-backend-7d9f8c6b5d-def34   1/1     Running   0          2m
todo-chatbot-backend-7d9f8c6b5d-ghi56   1/1     Running   0          2m
todo-chatbot-frontend-5c8d7b4a3e-jkl78  1/1     Running   0          2m

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
todo-chatbot-backend        ClusterIP   10.96.123.45    <none>        8000/TCP       2m
todo-chatbot-frontend       NodePort    10.96.234.56    <none>        80:30080/TCP   2m

http://192.168.49.2:30080
```

**Access the Application:**
```bash
# Open frontend in browser
open http://192.168.49.2:30080

# Or use the Minikube service command
minikube service todo-chatbot-frontend
```

## Common Operations

### Scale Backend

**Using kubectl-ai:**
```bash
"Scale the backend component of the todo-chatbot deployment to 5 replicas in the default namespace."
```

**Alternative (Manual):**
```bash
kubectl scale deployment/todo-chatbot-backend --replicas=5
kubectl get pods -l app=todo-chatbot,component=backend
```

### Update Application

**Using kubectl-ai:**
```bash
# Build new images with new version tag
docker build -t todo-backend:v1.1.0 -f deployment/dockerfiles/backend.Dockerfile ./backend
docker build -t todo-frontend:v1.1.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend

# Upgrade Helm release
"Upgrade the todo-chatbot Helm release to use new image versions:
- Backend image: todo-backend:v1.1.0
- Frontend image: todo-frontend:v1.1.0
Wait for rolling update to complete."
```

**Alternative (Manual):**
```bash
helm upgrade todo-chatbot deployment/helm/todo-chatbot/ \
  --set backend.image.tag=v1.1.0 \
  --set frontend.image.tag=v1.1.0 \
  --wait
```

### Rollback Deployment

**Using kubectl-ai:**
```bash
"Rollback the todo-chatbot deployment to the previous revision in the default namespace. Wait for all pods to be ready."
```

**Alternative (Manual):**
```bash
# View revision history
helm history todo-chatbot

# Rollback to previous revision
helm rollback todo-chatbot --wait
```

### View Logs

```bash
# Backend logs
kubectl logs -l app=todo-chatbot,component=backend --tail=50

# Frontend logs
kubectl logs -l app=todo-chatbot,component=frontend --tail=50

# Follow logs in real-time
kubectl logs -l app=todo-chatbot,component=backend -f
```

### Check Resource Usage

```bash
# Pod resource usage
kubectl top pods -l app=todo-chatbot

# Node resource usage
kubectl top nodes
```

## Troubleshooting

### Pods Not Starting

**Using kagent:**
```bash
"Diagnose why the todo-chatbot-backend deployment failed in the default namespace. Analyze pod events, container logs, and resource constraints."
```

**Manual Diagnosis:**
```bash
# Check pod status
kubectl get pods -l app=todo-chatbot

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common issues:
# - ImagePullBackOff: Image not found in Minikube's Docker daemon
#   Solution: Rebuild image with eval $(minikube docker-env)
# - CrashLoopBackOff: Application failing to start
#   Solution: Check logs for application errors
# - Pending: Insufficient resources
#   Solution: Increase Minikube resources or scale down replicas
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints todo-chatbot-frontend

# If no endpoints, check pod readiness
kubectl get pods -l app=todo-chatbot,component=frontend

# Check service configuration
kubectl describe service todo-chatbot-frontend

# Get correct URL
minikube service todo-chatbot-frontend --url
```

### Image Build Failures

```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is accessible
docker ps

# Check Dockerfile syntax
docker build --no-cache -t test-image -f deployment/dockerfiles/backend.Dockerfile ./backend

# Common issues:
# - Missing dependencies: Update requirements.txt or package.json
# - Build context errors: Ensure Dockerfile paths are relative to context
# - Permission errors: Check file permissions in source directories
```

### Helm Chart Issues

```bash
# Validate Helm chart
helm lint deployment/helm/todo-chatbot/

# Dry-run deployment
helm install todo-chatbot deployment/helm/todo-chatbot/ --dry-run --debug

# Check Helm release status
helm status todo-chatbot

# View Helm release history
helm history todo-chatbot
```

## Cleanup

### Uninstall Application

```bash
# Using kubectl-ai
"Uninstall the todo-chatbot Helm release from the default namespace."

# Manual
helm uninstall todo-chatbot
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```

### Remove Docker Images

```bash
# List images
docker images | grep todo-

# Remove images
docker rmi todo-backend:v1.0.0
docker rmi todo-frontend:v1.0.0
```

## Next Steps

After successful deployment:

1. **Test Application**: Verify all features work correctly in Kubernetes environment
2. **Monitor Performance**: Use `kubectl top` to monitor resource usage
3. **Test Scaling**: Scale backend to different replica counts and verify load distribution
4. **Test Updates**: Deploy new versions and verify zero-downtime updates
5. **Test Rollback**: Intentionally deploy a broken version and verify automatic rollback
6. **Document Learnings**: Update deployment log with any issues encountered and resolutions

## Reference

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **AI Tool Interfaces**: [contracts/ai-tool-interfaces.md](./contracts/ai-tool-interfaces.md)
- **Deployment Workflows**: [contracts/deployment-workflows.md](./contracts/deployment-workflows.md)

## Support

For issues or questions:
1. Check deployment log: `deployment/docs/deployment-log.md`
2. Review AI prompts: `deployment/docs/ai-prompts/`
3. Consult troubleshooting section above
4. Use kagent for automated diagnosis
5. Escalate to human review if automated recovery fails
