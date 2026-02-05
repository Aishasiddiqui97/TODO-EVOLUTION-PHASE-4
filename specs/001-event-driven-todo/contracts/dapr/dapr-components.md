# Dapr Component Configurations

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Version**: 1.0.0

## Overview

This document defines Dapr component configurations for local (Minikube) and cloud (AKS/GKE/OKE) deployments. Components provide infrastructure abstraction for PubSub, State Store, Secrets, and Jobs.

---

## PubSub Component (Kafka)

### Local (Minikube) - pubsub-local.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda:9092"
  - name: consumerGroup
    value: "{appId}"
  - name: clientId
    value: "{appId}"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "200ms"
scopes:
- chat-api
- recurring-task
- notification
- audit-log
- websocket-sync
```

### Cloud (Production) - pubsub-cloud.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    secretKeyRef:
      name: kafka-secrets
      key: brokers
  - name: consumerGroup
    value: "{appId}"
  - name: clientId
    value: "{appId}"
  - name: authType
    value: "certificate"
  - name: caCert
    secretKeyRef:
      name: kafka-secrets
      key: caCert
  - name: clientCert
    secretKeyRef:
      name: kafka-secrets
      key: clientCert
  - name: clientKey
    secretKeyRef:
      name: kafka-secrets
      key: clientKey
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "200ms"
scopes:
- chat-api
- recurring-task
- notification
- audit-log
- websocket-sync
```

**Topics Created**:
- `task-events`
- `reminders`
- `task-updates`

---

## State Store Component (PostgreSQL)

### Local (Minikube) - statestore-local.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=postgres port=5432 user=todo password=todo dbname=todo_db sslmode=disable"
  - name: tableName
    value: "dapr_state"
  - name: metadataTableName
    value: "dapr_metadata"
  - name: actorStateStore
    value: "false"
  - name: keyPrefix
    value: "none"
scopes:
- chat-api
- recurring-task
- notification
- audit-log
```

### Cloud (Production) - statestore-cloud.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secrets
      key: connectionString
  - name: tableName
    value: "dapr_state"
  - name: metadataTableName
    value: "dapr_metadata"
  - name: actorStateStore
    value: "false"
  - name: keyPrefix
    value: "none"
  - name: timeout
    value: "30"
  - name: maxConns
    value: "50"
scopes:
- chat-api
- recurring-task
- notification
- audit-log
```

**State Key Patterns**:
- `chat-api.task.{userId}.{taskId}`
- `chat-api.conversation.{userId}`
- `chat-api.preferences.{userId}`
- `notification.reminder.{notificationId}`
- `audit-log.event.{eventId}`
- `processed-events.{eventId}` (for idempotency)

---

## Secrets Component

### Local (Minikube) - secretstore-local.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultName
    value: "default"
scopes:
- chat-api
- notification
```

**Kubernetes Secrets** (local-secrets.yaml):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secrets
  namespace: default
type: Opaque
stringData:
  apiKey: "sk-test-key-local"
  baseUrl: "https://api.openai.com/v1"
---
apiVersion: v1
kind: Secret
metadata:
  name: email-secrets
  namespace: default
type: Opaque
stringData:
  smtpHost: "mailhog"
  smtpPort: "1025"
  smtpUser: ""
  smtpPassword: ""
  fromAddress: "noreply@todo.local"
```

### Cloud (Production) - secretstore-cloud.yaml

**Azure Key Vault Example**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.azure.keyvault
  version: v1
  metadata:
  - name: vaultName
    value: "todo-secrets-prod"
  - name: azureTenantId
    value: "your-tenant-id"
  - name: azureClientId
    value: "your-client-id"
  - name: azureClientSecret
    secretKeyRef:
      name: azure-credentials
      key: clientSecret
scopes:
- chat-api
- notification
```

**AWS Secrets Manager Example**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.aws.secretmanager
  version: v1
  metadata:
  - name: region
    value: "us-east-1"
  - name: accessKey
    secretKeyRef:
      name: aws-credentials
      key: accessKey
  - name: secretKey
    secretKeyRef:
      name: aws-credentials
      key: secretKey
scopes:
- chat-api
- notification
```

---

## Jobs Component (Alpha Scheduler)

### jobs-config.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: scheduler
  namespace: default
spec:
  type: scheduler.alpha
  version: v1
  metadata:
  - name: stateStore
    value: "statestore"
scopes:
- notification
- recurring-task
```

**Job Scheduling Example**:
```python
from dapr.clients import DaprClient

async def schedule_reminder(task_id: str, reminder_time: datetime):
    async with DaprClient() as client:
        await client.schedule_job(
            job_name=f"reminder-{task_id}",
            schedule=reminder_time.isoformat(),
            data=json.dumps({
                "taskId": task_id,
                "type": "reminder"
            })
        )
```

---

## Event Subscriptions

### Chat API Service - subscription-chat-api.yaml

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: chat-api-subscriptions
  namespace: default
spec:
  pubsubname: pubsub
  topic: task-events
  routes:
    default: /events/task
  scopes:
  - chat-api
```

### Recurring Task Service - subscription-recurring-task.yaml

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: recurring-task-subscriptions
  namespace: default
spec:
  pubsubname: pubsub
  topic: task-events
  routes:
    default: /events/task
  scopes:
  - recurring-task
  bulkSubscribe:
    enabled: true
    maxMessagesCount: 100
    maxAwaitDurationMs: 1000
```

### Notification Service - subscription-notification.yaml

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-subscriptions
  namespace: default
spec:
  pubsubname: pubsub
  topic: reminders
  routes:
    default: /events/reminder
  scopes:
  - notification
  deadLetterTopic: reminders-dlq
```

### Audit Log Service - subscription-audit-log.yaml

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: audit-log-subscriptions
  namespace: default
spec:
  pubsubname: pubsub
  topic: task-events
  routes:
    default: /events/task
  scopes:
  - audit-log
  bulkSubscribe:
    enabled: true
    maxMessagesCount: 500
    maxAwaitDurationMs: 2000
```

### WebSocket Sync Service - subscription-websocket-sync.yaml

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: websocket-sync-subscriptions
  namespace: default
spec:
  pubsubname: pubsub
  topic: task-updates
  routes:
    default: /events/sync
  scopes:
  - websocket-sync
```

---

## Resiliency Configuration

### resiliency.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: default-resiliency
  namespace: default
spec:
  policies:
    retries:
      pubsubRetry:
        policy: exponential
        maxInterval: 60s
        maxRetries: 3
      stateRetry:
        policy: constant
        duration: 1s
        maxRetries: 5
    timeouts:
      general:
        timeout: 30s
      pubsub:
        timeout: 10s
    circuitBreakers:
      pubsubCB:
        maxRequests: 3
        timeout: 30s
        trip: consecutiveFailures >= 5
  targets:
    components:
      pubsub:
        outbound:
          retry: pubsubRetry
          timeout: pubsub
          circuitBreaker: pubsubCB
      statestore:
        outbound:
          retry: stateRetry
          timeout: general
```

---

## Observability Configuration

### tracing.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
  metric:
    enabled: true
  logging:
    apiLogging:
      enabled: true
      obfuscateURLs: false
```

### metrics.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: metrics
  namespace: default
spec:
  metric:
    enabled: true
    rules:
    - name: appmetrics
      labels:
      - name: app_id
        value: "{appId}"
      - name: method
        value: "{method}"
      - name: status_code
        value: "{statusCode}"
```

---

## Service-to-Service Invocation (Rare Use)

While event-driven architecture is primary, Dapr Service Invocation can be used for synchronous calls when necessary.

**Example**: Chat API calling Notification Service directly for immediate notification:

```python
from dapr.clients import DaprClient

async def send_immediate_notification(user_id: str, message: str):
    async with DaprClient() as client:
        response = await client.invoke_method(
            app_id="notification",
            method_name="send-notification",
            data=json.dumps({
                "userId": user_id,
                "message": message
            }),
            http_verb="POST"
        )
        return response.data
```

**Service Invocation Configuration** (automatic via Dapr):
- No additional configuration needed
- Services discovered via Kubernetes DNS
- Automatic retries and timeouts via resiliency policy

---

## Environment-Specific Deployment

### Local (Minikube)

**Apply Components**:
```bash
kubectl apply -f contracts/dapr/pubsub-local.yaml
kubectl apply -f contracts/dapr/statestore-local.yaml
kubectl apply -f contracts/dapr/secretstore-local.yaml
kubectl apply -f contracts/dapr/local-secrets.yaml
kubectl apply -f contracts/dapr/jobs-config.yaml
kubectl apply -f contracts/dapr/subscription-*.yaml
kubectl apply -f contracts/dapr/resiliency.yaml
kubectl apply -f contracts/dapr/tracing.yaml
```

### Cloud (Production)

**Apply Components**:
```bash
kubectl apply -f contracts/dapr/pubsub-cloud.yaml
kubectl apply -f contracts/dapr/statestore-cloud.yaml
kubectl apply -f contracts/dapr/secretstore-cloud.yaml
kubectl apply -f contracts/dapr/jobs-config.yaml
kubectl apply -f contracts/dapr/subscription-*.yaml
kubectl apply -f contracts/dapr/resiliency.yaml
kubectl apply -f contracts/dapr/tracing.yaml
```

**Create Cloud Secrets** (example for Kubernetes):
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=brokers="kafka.example.com:9093" \
  --from-file=caCert=ca.pem \
  --from-file=clientCert=client.pem \
  --from-file=clientKey=client-key.pem

kubectl create secret generic postgres-secrets \
  --from-literal=connectionString="host=postgres.example.com port=5432 user=todo password=xxx dbname=todo_db sslmode=require"
```

---

## Summary

Dapr component configurations defined:
- ✅ PubSub (Kafka) - local and cloud variants
- ✅ State Store (PostgreSQL) - local and cloud variants
- ✅ Secrets - Kubernetes Secrets (local), Key Vault/Secrets Manager (cloud)
- ✅ Jobs (Alpha Scheduler) - for reminders and recurring tasks
- ✅ Event Subscriptions - 5 services with topic routing
- ✅ Resiliency - retries, timeouts, circuit breakers
- ✅ Observability - tracing and metrics

All configurations support environment parity with zero code changes.

Ready to proceed to quickstart guide.
