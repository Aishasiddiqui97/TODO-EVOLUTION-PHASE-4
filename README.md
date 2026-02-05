# Event-Driven Todo Chatbot

A production-ready, event-driven task management system with AI-powered natural language interface built on Dapr and Kubernetes.

[![CI](https://github.com/your-org/todo-chatbot/workflows/CI/badge.svg)](https://github.com/your-org/todo-chatbot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **Natural Language Interface**: Interact with tasks using conversational AI powered by OpenAI Agents SDK
- **Event-Driven Architecture**: Built on Dapr with PubSub, State Store, and Service Invocation
- **Real-Time Sync**: WebSocket-based synchronization across multiple devices
- **Recurring Tasks**: Flexible recurrence patterns with natural language support
- **Smart Search**: Advanced filtering and full-text search with relevance scoring
- **Notifications**: In-app and email notifications with retry logic and consolidation
- **Audit Trail**: Immutable audit log for compliance and debugging
- **Cloud-Native**: Kubernetes-ready with auto-scaling and observability

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│                    WebSocket Client + Chat UI                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ├─── HTTP ───┐
                 │            │
                 └─ WebSocket ┘
                      │
┌─────────────────────┴────────────────────────────────────────────┐
│                      Kubernetes Cluster                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Dapr Service Mesh                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │   │
│  │  │  PubSub    │  │ State Store│  │  Secrets   │         │   │
│  │  │  (Redis)   │  │  (Redis)   │  │ (K8s/KV)   │         │   │
│  │  └────────────┘  └────────────┘  └────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Microservices                           │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │   Chat API   │  │  Recurring   │  │ Notification │   │  │
│  │  │   (8001)     │  │  Task (8002) │  │   (8003)     │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │                                                            │  │
│  │  ┌──────────────┐  ┌──────────────┐                      │  │
│  │  │  WebSocket   │  │  Audit Log   │                      │  │
│  │  │  Sync (8004) │  │   (8005)     │                      │  │
│  │  └──────────────┘  └──────────────┘                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Observability                            │  │
│  │  ┌──────────────┐  ┌──────────────┐                      │  │
│  │  │  Prometheus  │  │    Zipkin    │                      │  │
│  │  │  (Metrics)   │  │   (Tracing)  │                      │  │
│  │  └──────────────┘  └──────────────┘                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### Microservices

1. **Chat API** (Port 8001)
   - Natural language interface using OpenAI Agents SDK
   - MCP tools for task operations
   - User preferences management
   - REST API endpoints

2. **Recurring Task Service** (Port 8002)
   - Processes task.completed events
   - Creates next instance for recurring tasks
   - Natural language recurrence pattern parsing

3. **Notification Service** (Port 8003)
   - In-app and email notifications
   - Notification consolidation
   - Retry logic with exponential backoff
   - SMTP integration

4. **WebSocket Sync Service** (Port 8004)
   - Real-time task synchronization
   - Connection management
   - Sequence tracking for missed events
   - Reconnection handling

5. **Audit Log Service** (Port 8005)
   - Immutable audit trail
   - Query API for audit logs
   - User statistics

### Event Flow

```
User Action (Chat) → Chat API → MCP Tool → State Store
                                    ↓
                            Publish Event (PubSub)
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            Recurring Task Service          Notification Service
            WebSocket Sync Service          Audit Log Service
                    ↓                               ↓
            Process Event                   Process Event
                    ↓                               ↓
            Update State                    Send Notification
            Create Next Instance            Log to Audit Trail
            Broadcast to Clients
```

## 🚀 Quick Start

### Prerequisites

- **Docker** (20.10+)
- **Kubernetes** (1.21+) - Minikube, AKS, EKS, or GKE
- **Dapr CLI** (1.11+)
- **kubectl** (1.21+)
- **Node.js** (18+) for frontend
- **Python** (3.11+) for backend

### Local Development with Minikube

```bash
# Clone repository
git clone https://github.com/your-org/todo-chatbot.git
cd todo-chatbot

# Deploy to Minikube
chmod +x scripts/deploy-local.sh
./scripts/deploy-local.sh

# Access the application
# Chat API: http://<minikube-ip>:<nodeport>
# Frontend: cd frontend && npm install && npm run dev
```

### Local Development with Dapr CLI

```bash
# Terminal 1: Chat API
cd backend
dapr run --app-id chat-api --app-port 8001 --dapr-http-port 3500 \
  --components-path ../k8s/dapr \
  -- python -m uvicorn src.main:app --host 0.0.0.0 --port 8001

# Terminal 2: WebSocket Sync
dapr run --app-id websocket-sync --app-port 8004 --dapr-http-port 3502 \
  --components-path ../k8s/dapr \
  -- python -m uvicorn src.services.websocket-sync.main:app --host 0.0.0.0 --port 8004

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

### Cloud Deployment

```bash
# Deploy to Azure AKS
chmod +x scripts/deploy-cloud.sh
./scripts/deploy-cloud.sh production azure

# Deploy to AWS EKS
./scripts/deploy-cloud.sh production aws

# Deploy to Google GKE
./scripts/deploy-cloud.sh production gcp
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_TESTING_GUIDE.md)
- [Implementation Progress](IMPLEMENTATION_PROGRESS.md) - 127/139 tasks (91%)
- [User Story 2: Recurring Tasks](USER_STORY_2_COMPLETE.md)
- [User Story 3: Task Tags](USER_STORY_3_COMPLETE.md)
- [User Story 4: Notifications](USER_STORY_4_COMPLETE.md)
- [User Story 5: Search & Filtering](USER_STORY_5_COMPLETE.md)
- [User Story 6: Real-Time Sync](USER_STORY_6_COMPLETE.md)
- [Audit Log Service](AUDIT_LOG_SERVICE_COMPLETE.md)
- [Cloud Deployment](CLOUD_DEPLOYMENT_COMPLETE.md)

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/ --cov=src

# Frontend tests
cd frontend
npm test

# Integration tests
./scripts/run-integration-tests.sh
```

### Manual Testing

```bash
# Create a task
curl -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "userId": "user-001"}'

# List tasks
curl http://localhost:8001/api/v1/tasks?userId=user-001

# Chat interface
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy milk to my list"}'
```

## 📊 Monitoring

### Prometheus Metrics

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n todo-chatbot-local

# Access: http://localhost:9090
```

### Zipkin Tracing

```bash
# Port forward Zipkin
kubectl port-forward svc/zipkin 9411:9411 -n todo-chatbot-local

# Access: http://localhost:9411
```

### Logs

```bash
# View service logs
kubectl logs -f deployment/chat-api -n todo-chatbot-local

# View Dapr sidecar logs
kubectl logs -f deployment/chat-api -c daprd -n todo-chatbot-local
```

## 🔧 Configuration

### Environment Variables

```bash
# Backend
ENVIRONMENT=production          # local, staging, production
LOG_LEVEL=info                 # debug, info, warning, error
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8004
```

### Dapr Components

- **PubSub**: Redis (local), Azure Service Bus (cloud)
- **State Store**: Redis (local), Azure Cosmos DB (cloud)
- **Secrets**: Kubernetes (local), Azure Key Vault (cloud)

## 🛠️ Development

### Project Structure

```
.
├── backend/
│   └── src/
│       ├── mcp/tools/          # MCP tools for AI agent
│       ├── services/           # Microservices
│       │   ├── chat-api/
│       │   ├── recurring-task/
│       │   ├── notification/
│       │   ├── websocket-sync/
│       │   └── audit-log/
│       └── shared/             # Shared utilities
├── frontend/
│   └── src/
│       ├── components/         # React components
│       └── services/           # WebSocket client
├── k8s/
│   ├── dapr/                   # Dapr components
│   ├── services/               # Service manifests
│   ├── observability/          # Prometheus, Zipkin
│   └── overlays/               # Kustomize overlays
│       ├── local/
│       └── cloud/
├── scripts/                    # Deployment scripts
└── specs/                      # Specifications
```

## 🔐 Security

- **Authentication**: Implement OAuth 2.0 / JWT (currently using temp user IDs)
- **Rate Limiting**: 100 requests per 60 seconds per client
- **CORS**: Configured per environment
- **Input Validation**: Pydantic models + custom validators
- **Secrets Management**: Kubernetes Secrets / Azure Key Vault
- **Network Policies**: Restrict inter-service communication
- **Security Context**: Non-root containers, dropped capabilities

## 📈 Performance

- **Horizontal Scaling**: Auto-scaling based on CPU/memory
- **Caching**: Redis for state and PubSub
- **Connection Pooling**: HTTP and database connections
- **Async I/O**: FastAPI with async/await
- **WebSocket**: Persistent connections for real-time sync

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Dapr](https://dapr.io/) - Distributed Application Runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [OpenAI](https://openai.com/) - AI models and Agents SDK
- [Kubernetes](https://kubernetes.io/) - Container orchestration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/todo-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/todo-chatbot/discussions)
- **Email**: support@todo-chatbot.example.com

## 🗺️ Roadmap

- [ ] OAuth 2.0 authentication
- [ ] Mobile app (React Native)
- [ ] Voice interface
- [ ] Task attachments
- [ ] Collaboration features
- [ ] Analytics dashboard
- [ ] AI-powered task suggestions

---

**Built with ❤️ using Dapr, Kubernetes, and AI**
