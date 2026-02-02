# Deployment Runbook: Todo Chatbot

**Feature**: 004-k8s-deployment
**Created**: 2026-02-03
**Purpose**: Operational procedures for deploying and managing the Todo Chatbot application

## Prerequisites

Before starting any deployment operations:

1. **Minikube** installed and running
2. **kubectl** configured to use minikube context
3. **Docker** installed and accessible
4. **Helm** v3.x installed
5. **AI Tools** (optional): kubectl-ai, kagent for AI-assisted operations

## Quick Start

### Initial Deployment

```bash
# Automated deployment (recommended)
./deployment/scripts/deploy.sh

# Manual deployment
minikube start --cpus=4 --memory=8192 --disk-size=20g
eval $(minikube docker-env)
docker build -t todo-backend:v1.0.0 -f deployment/dockerfiles/backend.Dockerfile ./backend
docker build -t todo-frontend:v1.0.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend
helm install todo-chatbot deployment/helm/todo-chatbot/ --namespace default --wait
minikube service todo-chatbot-frontend --url
```

## Common Operations

### 1. Deploy Application

**Automated (Recommended)**:
```bash
./deployment/scripts/deploy.sh
```

**Manual Steps**:
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Configure Docker
eval $(minikube docker-env)

# Build images
docker build -t todo-backend:v1.0.0 -f deployment/dockerfiles/backend.Dockerfile ./backend
docker build -t todo-frontend:v1.0.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend

# Deploy with Helm
helm install todo-chatbot deployment/helm/todo-chatbot/ --namespace default --wait --timeout 5m

# Get frontend URL
minikube service todo-chatbot-frontend --url
```

**AI-Assisted (kubectl-ai)**:
```
Prompt: "Install todo-chatbot Helm chart from deployment/helm/todo-chatbot/ to default namespace, wait for all pods ready"
```

### 2. Scale Application

**Automated**:
```bash
./deployment/scripts/scale.sh backend 5
./deployment/scripts/scale.sh frontend 2
```

**Manual**:
```bash
kubectl scale deployment/todo-chatbot-backend --replicas=5 --namespace=default
kubectl scale deployment/todo-chatbot-frontend --replicas=2 --namespace=default
```

**AI-Assisted (kubectl-ai)**:
```
Prompt: "Scale backend component of todo-chatbot deployment to 5 replicas in default namespace"
```

### 3. Update Application

**Build New Images**:
```bash
eval $(minikube docker-env)
docker build -t todo-backend:v1.1.0 -f deployment/dockerfiles/backend.Dockerfile ./backend
docker build -t todo-frontend:v1.1.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend
```

**Upgrade Helm Release**:
```bash
helm upgrade todo-chatbot deployment/helm/todo-chatbot/ \
  --set backend.image.tag=v1.1.0 \
  --set frontend.image.tag=v1.1.0 \
  --wait
```

**AI-Assisted (kubectl-ai)**:
```
Prompt: "Upgrade todo-chatbot Helm release to use backend image v1.1.0 and frontend image v1.1.0, wait for rolling update"
```

### 4. Rollback Deployment

**Automated**:
```bash
./deployment/scripts/rollback.sh
./deployment/scripts/rollback.sh 2  # Rollback to specific revision
```

**Manual**:
```bash
# View history
helm history todo-chatbot

# Rollback to previous
helm rollback todo-chatbot --namespace=default --wait

# Rollback to specific revision
helm rollback todo-chatbot 2 --namespace=default --wait
```

**AI-Assisted (kubectl-ai)**:
```
Prompt: "Rollback todo-chatbot deployment to previous revision in default namespace, wait for completion"
```

### 5. Check Health

**Manual**:
```bash
# Check pods
kubectl get pods -l app=todo-chatbot

# Check services
kubectl get services -l app=todo-chatbot

# Check pod logs
kubectl logs -l app=todo-chatbot,component=backend --tail=50

# Describe pod for events
kubectl describe pod <pod-name>
```

**AI-Assisted (kagent)**:
```
Prompt: "Check health of todo-chatbot deployment in default namespace, analyze all components and services"
```

### 6. View Logs

```bash
# Backend logs
kubectl logs -l app=todo-chatbot,component=backend --tail=100 -f

# Frontend logs
kubectl logs -l app=todo-chatbot,component=frontend --tail=100 -f

# All logs
kubectl logs -l app=todo-chatbot --tail=100 -f
```

### 7. Access Application

```bash
# Get frontend URL
minikube service todo-chatbot-frontend --url

# Open in browser
minikube service todo-chatbot-frontend
```

## Troubleshooting

### Pods Not Starting

**Symptoms**: Pods stuck in Pending, ImagePullBackOff, or CrashLoopBackOff

**Diagnosis**:
```bash
kubectl get pods -l app=todo-chatbot
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Common Causes & Solutions**:

1. **ImagePullBackOff**: Image not found in Minikube's Docker daemon
   ```bash
   eval $(minikube docker-env)
   docker images | grep todo-
   # Rebuild images if missing
   docker build -t todo-backend:v1.0.0 -f deployment/dockerfiles/backend.Dockerfile ./backend
   ```

2. **CrashLoopBackOff**: Application failing to start
   ```bash
   kubectl logs <pod-name>
   # Check application logs for errors
   # Common issues: missing environment variables, database connection failures
   ```

3. **Pending**: Insufficient resources
   ```bash
   kubectl describe pod <pod-name>
   # Look for "Insufficient cpu" or "Insufficient memory"
   # Solution: Increase Minikube resources or scale down replicas
   minikube stop
   minikube start --cpus=4 --memory=8192
   ```

**AI-Assisted Diagnosis (kagent)**:
```
Prompt: "Diagnose why todo-chatbot-backend deployment failed in default namespace, analyze pod events and logs"
```

### Service Not Accessible

**Symptoms**: Cannot access frontend URL, connection refused

**Diagnosis**:
```bash
kubectl get services -l app=todo-chatbot
kubectl get endpoints todo-chatbot-frontend
minikube service todo-chatbot-frontend --url
```

**Common Causes & Solutions**:

1. **No endpoints**: Pods not ready
   ```bash
   kubectl get pods -l app=todo-chatbot,component=frontend
   # Wait for pods to become ready or check pod issues
   ```

2. **Wrong URL**: Using incorrect service URL
   ```bash
   # Get correct URL
   minikube service todo-chatbot-frontend --url
   ```

3. **Minikube tunnel needed** (on some systems):
   ```bash
   minikube tunnel
   ```

### Helm Chart Issues

**Symptoms**: Helm install/upgrade fails

**Diagnosis**:
```bash
helm lint deployment/helm/todo-chatbot/
helm install todo-chatbot deployment/helm/todo-chatbot/ --dry-run --debug
```

**Common Causes & Solutions**:

1. **Template errors**: Invalid YAML or template syntax
   ```bash
   helm template todo-chatbot deployment/helm/todo-chatbot/
   # Review output for errors
   ```

2. **Release already exists**:
   ```bash
   helm list
   helm uninstall todo-chatbot
   # Then retry install
   ```

## Cleanup

### Uninstall Application

```bash
helm uninstall todo-chatbot --namespace=default
```

### Stop Minikube

```bash
minikube stop
```

### Delete Minikube Cluster

```bash
minikube delete
```

### Remove Docker Images

```bash
docker rmi todo-backend:v1.0.0
docker rmi todo-frontend:v1.0.0
```

## Monitoring

### Resource Usage

```bash
# Pod resource usage
kubectl top pods -l app=todo-chatbot

# Node resource usage
kubectl top nodes
```

### Deployment Status

```bash
# Rollout status
kubectl rollout status deployment/todo-chatbot-backend
kubectl rollout status deployment/todo-chatbot-frontend

# Rollout history
kubectl rollout history deployment/todo-chatbot-backend
```

## Best Practices

1. **Always use Minikube's Docker daemon**: `eval $(minikube docker-env)` before building images
2. **Validate Helm charts before deploying**: `helm lint` and `helm template`
3. **Use --wait flag**: Ensures deployment completes before returning
4. **Check logs after deployment**: Verify no errors in application logs
5. **Monitor resource usage**: Ensure pods have sufficient resources
6. **Keep deployment log updated**: Record all deployment events for audit trail
7. **Test rollback procedures**: Verify rollback works before production issues
8. **Use AI tools for diagnosis**: kagent provides faster root cause analysis

## Reference

- **Specification**: specs/004-k8s-deployment/spec.md
- **Implementation Plan**: specs/004-k8s-deployment/plan.md
- **Tasks**: specs/004-k8s-deployment/tasks.md
- **Quickstart**: specs/004-k8s-deployment/quickstart.md
- **Deployment Log**: deployment/docs/deployment-log.md
- **AI Prompts**: deployment/docs/ai-prompts/
