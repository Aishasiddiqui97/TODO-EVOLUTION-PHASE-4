# Phase V MVP - Quick Start Guide

## Prerequisites

- Docker Desktop (with Kubernetes enabled) OR Minikube
- kubectl CLI
- Dapr CLI
- OpenAI API key

## Option 1: Docker Compose (Fastest)

1. **Set up environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OPENAI_API_KEY
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Test the API:**
   ```bash
   # Health check
   curl http://localhost:8000/health

   # Create a task
   curl -X POST http://localhost:8000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "priority": "high"}'

   # List tasks
   curl http://localhost:8000/api/v1/tasks

   # Chat with AI
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me my tasks"}'
   ```

## Option 2: Kubernetes (Full Deployment)

### Windows

```bash
deploy-local.bat
```

### Linux/Mac

```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

### Manual Steps

1. **Start Minikube:**
   ```bash
   minikube start --cpus=4 --memory=8192
   ```

2. **Initialize Dapr:**
   ```bash
   dapr init -k
   ```

3. **Create secrets:**
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=openai-api-key="your-key-here"
   ```

4. **Deploy infrastructure:**
   ```bash
   kubectl apply -f k8s/local/
   ```

5. **Deploy Dapr components:**
   ```bash
   kubectl apply -f k8s/dapr/
   ```

6. **Build and deploy Chat API:**
   ```bash
   docker build -t chat-api:latest -f backend/Dockerfile .
   minikube image load chat-api:latest
   kubectl apply -f k8s/services/
   ```

7. **Access the API:**
   ```bash
   kubectl port-forward svc/chat-api 8000:8000
   ```

## Testing

Run the test script:

```bash
# Linux/Mac
chmod +x test-api.sh
./test-api.sh

# Windows (use Git Bash or WSL)
bash test-api.sh
```

## API Endpoints

- `GET /health` - Health check
- `GET /` - API info
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `PATCH /api/v1/tasks/{id}/complete` - Complete task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/chat` - Chat with AI

## Troubleshooting

### Chat API not starting
```bash
kubectl logs -f deployment/chat-api -c chat-api
kubectl logs -f deployment/chat-api -c daprd
```

### Check Dapr components
```bash
kubectl get components
kubectl get subscriptions
```

### View events
```bash
kubectl exec -it deployment/redpanda -- rpk topic consume task-events
```

## Next Steps

- Implement recurring tasks (User Story 2)
- Add notifications (User Story 4)
- Add WebSocket sync (User Story 6)
