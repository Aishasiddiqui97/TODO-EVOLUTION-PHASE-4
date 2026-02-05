# Research & Architecture Decisions

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Phase**: 0 - Research & Technical Decisions

## Overview

This document captures the research findings, technology choices, and architectural decisions for implementing Phase V event-driven Todo Chatbot. All decisions align with Phase V constitution requirements for event-driven architecture, infrastructure abstraction via Dapr, and environment parity.

---

## 1. Microservices Architecture

### Decision

Implement 5 independent microservices communicating via asynchronous events:
1. **Chat API Service** - User-facing API with MCP tools
2. **Recurring Task Service** - Handles recurring task logic
3. **Notification Service** - Sends reminders and notifications
4. **Audit Log Service** - Maintains event audit trail
5. **WebSocket Sync Service** - Real-time client synchronization

### Rationale

- **Separation of Concerns**: Each service has single responsibility
- **Independent Scaling**: Services scale based on their specific load patterns
- **Fault Isolation**: Failure in one service doesn't cascade to others
- **Independent Deployment**: Services can be deployed and updated independently
- **Team Autonomy**: Different teams can own different services

### Alternatives Considered

**Monolithic Architecture**:
- Rejected: Doesn't support independent scaling of notification/sync services
- Rejected: Violates Phase V event-driven architecture principle
- Rejected: Makes it harder to isolate failures

**Serverless Functions**:
- Rejected: Dapr sidecar pattern works better with long-running services
- Rejected: WebSocket connections require persistent connections
- Rejected: More complex state management across function invocations

### Best Practices Applied

- Each service has its own database schema (via Dapr State API with key prefixes)
- Services communicate only via events (no direct HTTP calls between services)
- Shared code (models, events) in common library
- Each service independently deployable with its own Dockerfile

---

## 2. Event-Driven Communication

### Decision

Use Dapr PubSub component with Kafka-compatible broker for all inter-service communication. Three primary topics:
- `task-events`: Task lifecycle events (created, updated, completed, deleted)
- `reminders`: Scheduled reminder triggers
- `task-updates`: Real-time sync updates for connected clients

### Rationale

- **Loose Coupling**: Services don't need to know about each other
- **Temporal Decoupling**: Producers and consumers operate independently
- **Scalability**: Multiple consumers can process events in parallel
- **Reliability**: Events persisted in Kafka provide durability
- **Replay Capability**: Can replay events for debugging or recovery
- **Constitution Compliance**: Satisfies Phase V event-driven architecture requirement

### Alternatives Considered

**Direct HTTP/gRPC Calls**:
- Rejected: Creates tight coupling between services
- Rejected: Violates Phase V event-driven architecture principle
- Rejected: Synchronous calls create cascading failures

**Message Queue (RabbitMQ)**:
- Rejected: Kafka provides better event replay and retention
- Rejected: Less suitable for high-throughput event streaming
- Considered: Could be used via Dapr PubSub, but Kafka is industry standard for event streaming

**Database Polling**:
- Rejected: Inefficient and creates database load
- Rejected: Doesn't provide real-time event delivery
- Rejected: Violates event-driven architecture principle

### Event Schema Design

All events follow consistent structure:
```json
{
  "eventId": "uuid",
  "eventType": "task.created | task.updated | task.completed | task.deleted",
  "timestamp": "ISO8601",
  "correlationId": "uuid",
  "sourceService": "chat-api",
  "userId": "uuid",
  "payload": {
    // Event-specific data
  }
}
```

**Idempotency**: All events include `eventId` to enable idempotent processing. Consumers track processed event IDs to avoid duplicate processing.

---

## 3. Dapr Building Blocks

### Decision

Use Dapr for all infrastructure concerns:
- **PubSub**: Event publishing and subscription (Kafka)
- **State Store**: Task and conversation state (PostgreSQL)
- **Secrets**: API keys and credentials (Kubernetes Secrets)
- **Jobs**: Scheduled reminders and recurring task checks
- **Service Invocation**: Synchronous calls when necessary (rare)

### Rationale

- **Infrastructure Abstraction**: Application code doesn't depend on specific infrastructure
- **Portability**: Same code runs on different infrastructure (local vs cloud)
- **Observability**: Dapr provides built-in metrics, logs, and tracing
- **Resilience**: Dapr handles retries, timeouts, circuit breakers
- **Constitution Compliance**: Satisfies Phase V infrastructure abstraction requirement

### Dapr PubSub Component

**Local (Minikube)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"
  - name: consumerGroup
    value: "{serviceId}"
```

**Cloud (AKS/GKE/OKE)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    secretKeyRef:
      name: kafka-secrets
      key: brokers
  - name: authType
    value: "certificate"
```

### Dapr State Store Component

**Local (Minikube)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=postgres port=5432 user=todo password=todo dbname=todo_db"
```

**Cloud**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secrets
      key: connectionString
```

### Alternatives Considered

**Direct SDK Usage**:
- Rejected: Violates Phase V infrastructure abstraction principle
- Rejected: Creates vendor lock-in
- Rejected: Requires code changes for different environments

**Service Mesh (Istio/Linkerd)**:
- Considered: Provides similar observability and resilience
- Rejected: Dapr provides higher-level abstractions (state, pubsub, secrets)
- Rejected: Service mesh focuses on networking, not application-level concerns
- Note: Could be used alongside Dapr for advanced networking features

---

## 4. State Management Strategy

### Decision

Use Dapr State API with PostgreSQL backend. State keys follow pattern: `{service}.{entity}.{id}`

Examples:
- `chat-api.task.user123.task456`
- `chat-api.conversation.user123`
- `notification.reminder.reminder789`

### Rationale

- **Service Isolation**: Key prefixes prevent cross-service state access
- **Consistency**: Dapr State API provides strong consistency guarantees
- **Caching**: Dapr can cache frequently accessed state
- **Portability**: Can switch state store backend without code changes
- **Constitution Compliance**: Satisfies Phase V infrastructure abstraction requirement

### State Operations

**Create/Update**:
```python
from dapr.clients import DaprClient

async def save_task(task_id: str, task_data: dict):
    async with DaprClient() as client:
        await client.save_state(
            store_name="statestore",
            key=f"chat-api.task.{user_id}.{task_id}",
            value=json.dumps(task_data),
            state_metadata={"contentType": "application/json"}
        )
```

**Read**:
```python
async def get_task(task_id: str) -> dict:
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="statestore",
            key=f"chat-api.task.{user_id}.{task_id}"
        )
        return json.loads(state.data) if state.data else None
```

**Optimistic Concurrency**:
```python
async def update_task_with_etag(task_id: str, task_data: dict, etag: str):
    async with DaprClient() as client:
        await client.save_state(
            store_name="statestore",
            key=f"chat-api.task.{user_id}.{task_id}",
            value=json.dumps(task_data),
            etag=etag  # Fails if state changed since read
        )
```

### Alternatives Considered

**Direct PostgreSQL Access**:
- Rejected: Violates Phase V infrastructure abstraction principle
- Rejected: Requires different code for different databases
- Rejected: No built-in caching or consistency guarantees

**Redis for State**:
- Considered: Could be used as Dapr State Store backend
- Decision: PostgreSQL chosen for durability and relational queries
- Note: Redis could be added as cache layer via Dapr configuration

---

## 5. Notification Delivery

### Decision

Implement dual-channel notifications:
1. **In-App Notifications**: Via WebSocket real-time sync
2. **Email Notifications**: Via SMTP/SendGrid

Notification Service subscribes to `reminders` topic and sends notifications through both channels.

### Rationale

- **Reliability**: Email ensures delivery even when app is closed
- **User Experience**: In-app notifications provide immediate feedback
- **Flexibility**: Users can configure preferred channels (future enhancement)
- **Spec Compliance**: Satisfies FR-020 requirement for in-app + email

### Email Service Integration

**Local (Minikube)**:
- Use MailHog for email testing (SMTP server with web UI)
- No actual emails sent, captured in MailHog UI

**Cloud**:
- Use SendGrid, AWS SES, or similar email service
- Credentials stored in Dapr Secrets

### Implementation Pattern

```python
async def send_notification(user_id: str, task: dict):
    # Send in-app notification via event
    await publish_event(
        topic="task-updates",
        event={
            "eventType": "notification.sent",
            "userId": user_id,
            "payload": {"task": task}
        }
    )

    # Send email notification
    email_config = await get_secret("email-config")
    await send_email(
        to=user.email,
        subject=f"Reminder: {task['title']}",
        body=render_template("reminder", task=task)
    )
```

### Alternatives Considered

**Push Notifications (FCM/APNS)**:
- Considered: Better mobile experience
- Deferred: Adds complexity, can be added in future iteration
- Note: Spec allows for this as future enhancement

**SMS Notifications**:
- Considered: High reliability
- Rejected: Cost prohibitive, not in spec requirements
- Note: Could be added as premium feature

---

## 6. Real-Time Sync Architecture

### Decision

WebSocket Sync Service maintains persistent WebSocket connections with clients. Subscribes to `task-updates` topic and pushes updates to connected clients in real-time.

### Rationale

- **Low Latency**: WebSocket provides sub-second update propagation
- **Efficient**: Single connection per client, no polling overhead
- **Scalable**: Service can be horizontally scaled with sticky sessions
- **Spec Compliance**: Satisfies FR-028 requirement for real-time sync

### WebSocket Connection Management

**Connection Lifecycle**:
1. Client connects to `/ws` endpoint with auth token
2. Service validates token and stores connection in memory
3. Service subscribes to `task-updates` for user's tasks
4. On event received, service pushes to all user's connections
5. On disconnect, service cleans up connection

**Reconnection Handling**:
- Client automatically reconnects on connection loss
- Service sends missed events since last connection (via sequence numbers)
- Exponential backoff for reconnection attempts

### Implementation Pattern

```python
from fastapi import WebSocket
from dapr.clients import DaprClient

class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(websocket)

    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.connections:
            for ws in self.connections[user_id]:
                await ws.send_json(message)

# Event subscriber
async def handle_task_update(event: dict):
    user_id = event["userId"]
    await ws_manager.broadcast_to_user(user_id, event)
```

### Alternatives Considered

**Server-Sent Events (SSE)**:
- Considered: Simpler than WebSocket
- Rejected: One-way communication, can't send client updates
- Rejected: Less efficient for bidirectional sync

**Polling**:
- Rejected: Inefficient, high latency
- Rejected: Doesn't meet <1s update requirement

**GraphQL Subscriptions**:
- Considered: Modern approach with good tooling
- Rejected: Adds complexity, WebSocket is sufficient
- Note: Could be added as alternative API in future

---

## 7. Recurring Task Scheduling

### Decision

Use Dapr Jobs API for scheduling recurring task checks. Recurring Task Service:
1. Subscribes to `task-events` topic for `task.completed` events
2. When recurring task completed, calculates next occurrence
3. Schedules Dapr job for next occurrence time
4. Job triggers creation of next task instance

### Rationale

- **Reliability**: Dapr Jobs persisted and survive service restarts
- **Scalability**: Dapr handles job distribution across service instances
- **Simplicity**: No need for separate scheduler service (Cron, Celery)
- **Constitution Compliance**: Uses Dapr building block for infrastructure

### Recurrence Pattern Calculation

```python
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY

def calculate_next_occurrence(pattern: dict, completed_at: datetime) -> datetime:
    if pattern["type"] == "daily":
        return completed_at + timedelta(days=pattern["interval"])

    elif pattern["type"] == "weekly":
        # Use dateutil.rrule for complex weekly patterns
        rule = rrule(
            WEEKLY,
            interval=pattern["interval"],
            byweekday=pattern["days"],  # [MO, WE, FR]
            dtstart=completed_at
        )
        return rule.after(completed_at)

    elif pattern["type"] == "custom":
        return completed_at + timedelta(days=pattern["interval"])
```

### Dapr Jobs API Usage

```python
async def schedule_next_task(task_id: str, next_occurrence: datetime):
    async with DaprClient() as client:
        await client.schedule_job(
            job_name=f"recurring-task-{task_id}",
            schedule=next_occurrence.isoformat(),
            data={"taskId": task_id}
        )

# Job handler
@app.post("/jobs/create-recurring-task")
async def create_recurring_task_job(data: dict):
    task_id = data["taskId"]
    # Create next task instance
    await create_task_instance(task_id)
```

### Alternatives Considered

**Cron Jobs (Kubernetes CronJob)**:
- Rejected: Less flexible for dynamic scheduling
- Rejected: Requires separate job per recurring task
- Rejected: Doesn't integrate with Dapr ecosystem

**Celery Beat**:
- Rejected: Requires Redis/RabbitMQ broker
- Rejected: Adds infrastructure complexity
- Rejected: Doesn't use Dapr building blocks

**Database Polling**:
- Rejected: Inefficient for large numbers of recurring tasks
- Rejected: Adds database load
- Rejected: Less accurate timing

---

## 8. Deployment Strategy

### Decision

Support two deployment targets with identical application code:
1. **Local (Minikube)**: For development and testing
2. **Cloud (AKS/GKE/OKE)**: For production

Environment differences handled entirely through Dapr component configuration and Kubernetes manifests (Kustomize overlays).

### Local Deployment (Minikube)

**Infrastructure**:
- Minikube cluster (single-node)
- Redpanda (Kafka-compatible) in Docker
- PostgreSQL in Kubernetes
- Dapr installed on cluster
- MailHog for email testing

**Setup Commands**:
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Install Dapr
dapr init --kubernetes

# Deploy infrastructure
kubectl apply -k k8s/local/

# Deploy services
kubectl apply -k k8s/base/
```

### Cloud Deployment (AKS/GKE/OKE)

**Infrastructure**:
- Managed Kubernetes (AKS/GKE/OKE)
- Managed Kafka (Redpanda Cloud, Confluent Cloud, or MSK)
- Managed PostgreSQL (Azure Database, Cloud SQL, or RDS)
- Dapr installed on cluster
- SendGrid/AWS SES for email

**CI/CD Pipeline** (GitHub Actions):
```yaml
name: Deploy to Cloud
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push images
        run: |
          docker build -t registry/chat-api:${{ github.sha }} services/chat-api
          docker push registry/chat-api:${{ github.sha }}
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -k k8s/cloud/
          kubectl set image deployment/chat-api chat-api=registry/chat-api:${{ github.sha }}
```

### Environment Parity

**Application Code**: Identical across environments
**Configuration**: Different Dapr component YAML files
**Secrets**: Kubernetes Secrets (local) vs Cloud Secret Manager (cloud)
**Scaling**: Single replica (local) vs Auto-scaling (cloud)

### Alternatives Considered

**Docker Compose**:
- Rejected: Doesn't support Kubernetes/Dapr features
- Rejected: Not production-ready
- Note: Could be used for quick local testing without K8s

**Separate Codebases**:
- Rejected: Violates Phase V environment parity principle
- Rejected: Maintenance burden of keeping codebases in sync

---

## 9. Observability Strategy

### Decision

Use Dapr built-in observability features:
- **Logging**: Structured JSON logs to stdout (captured by Kubernetes)
- **Metrics**: Prometheus metrics exposed by Dapr sidecar
- **Tracing**: Distributed tracing via Dapr (exportable to Jaeger/Zipkin)

### Rationale

- **Zero Code Changes**: Observability enabled by Dapr configuration
- **Standardization**: All services use same observability patterns
- **Integration**: Works with standard tools (Prometheus, Grafana, Jaeger)
- **Constitution Compliance**: Satisfies Phase V observability-first requirement

### Logging Configuration

```python
import logging
import json

# Structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def log_event(event_type: str, **kwargs):
    logger.info(json.dumps({
        "eventType": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }))

# Usage
log_event("task.created", taskId=task_id, userId=user_id)
```

### Metrics Collection

Dapr automatically exposes metrics:
- HTTP request latency
- Event publishing latency
- State operation latency
- Service invocation metrics

Custom metrics via Prometheus client:
```python
from prometheus_client import Counter, Histogram

task_created_counter = Counter('tasks_created_total', 'Total tasks created')
event_processing_duration = Histogram('event_processing_seconds', 'Event processing duration')

# Usage
task_created_counter.inc()
with event_processing_duration.time():
    await process_event(event)
```

### Distributed Tracing

Dapr automatically propagates trace context across services. Enable tracing in Dapr configuration:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
```

### Alternatives Considered

**Custom Logging Framework**:
- Rejected: Dapr provides standardized logging
- Rejected: Adds complexity without benefit

**APM Tools (New Relic, Datadog)**:
- Considered: Richer features and UI
- Deferred: Can be added later, Dapr tracing is sufficient for MVP
- Note: Dapr tracing can export to these tools

---

## 10. Security & Secrets Management

### Decision

Use Dapr Secrets API with Kubernetes Secrets (local) and cloud secret managers (cloud). No secrets in code or environment variables.

### Rationale

- **Security**: Secrets never in code or version control
- **Rotation**: Secrets can be rotated without code changes
- **Portability**: Same code works with different secret stores
- **Constitution Compliance**: Satisfies Phase V secrets management requirement

### Secrets Configuration

**Local (Kubernetes Secrets)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.kubernetes
  version: v1
```

**Cloud (Azure Key Vault example)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.azure.keyvault
  version: v1
  metadata:
  - name: vaultName
    value: "todo-secrets"
```

### Accessing Secrets

```python
async def get_email_config():
    async with DaprClient() as client:
        secret = await client.get_secret(
            store_name="secretstore",
            key="email-config"
        )
        return secret.secrets
```

### Alternatives Considered

**Environment Variables**:
- Rejected: Secrets visible in process list
- Rejected: Difficult to rotate
- Rejected: Not secure for production

**HashiCorp Vault**:
- Considered: Industry-standard secret management
- Deferred: Dapr Secrets API can integrate with Vault if needed
- Note: Can be added as Dapr secret store backend

---

## Summary

All technical decisions documented and justified. No unresolved "NEEDS CLARIFICATION" items remain. Architecture satisfies all Phase V constitution requirements:

✅ Event-driven architecture with Dapr PubSub
✅ Infrastructure abstraction via Dapr building blocks
✅ Environment parity (same code, different config)
✅ Observability first (logs, metrics, traces)
✅ Spec-driven development workflow
✅ Microservices with clear boundaries

Ready to proceed to Phase 1: Data Models and Contracts.
