# Event Schemas

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Version**: 1.0.0

## Overview

This document defines all event schemas for the event-driven Todo Chatbot system. Events are published via Dapr PubSub to Kafka topics and consumed by microservices.

---

## Event Structure

All events follow a consistent envelope structure:

```json
{
  "eventId": "UUID",
  "eventType": "string",
  "timestamp": "ISO8601 DateTime",
  "correlationId": "UUID",
  "sourceService": "string",
  "userId": "UUID",
  "payload": {}
}
```

**Envelope Fields**:
- `eventId`: Unique identifier for this event (for idempotency)
- `eventType`: Dot-notation event type (e.g., "task.created")
- `timestamp`: When event was generated (UTC)
- `correlationId`: Request correlation ID for distributed tracing
- `sourceService`: Service that published the event
- `userId`: User who triggered the event
- `payload`: Event-specific data

---

## Topic: task-events

**Description**: All task lifecycle events (created, updated, completed, deleted)

**Consumers**:
- Recurring Task Service (listens for task.completed)
- Notification Service (listens for task.created, task.updated)
- Audit Log Service (listens for all events)
- WebSocket Sync Service (listens for all events)

### Event: task.created

**Published by**: Chat API Service

**When**: New task is created through chat interface

**Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "eventType": "task.created",
  "timestamp": "2026-02-05T10:30:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440003",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "description": "Review the Q1 proposal and provide feedback",
      "priority": "high",
      "dueDate": "2026-02-10T00:00:00Z",
      "dueTime": "15:00",
      "tags": ["work", "urgent", "review"],
      "status": "pending",
      "recurrencePattern": null,
      "parentTaskId": null,
      "createdAt": "2026-02-05T10:30:00Z",
      "updatedAt": "2026-02-05T10:30:00Z"
    }
  }
}
```

**Idempotency**: Consumers should check if task with same `eventId` already processed.

---

### Event: task.updated

**Published by**: Chat API Service

**When**: Task attributes are modified (title, priority, due date, tags, etc.)

**Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440001",
  "eventType": "task.updated",
  "timestamp": "2026-02-06T14:20:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440004",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "description": "Review the Q1 proposal and provide feedback",
      "priority": "medium",
      "dueDate": "2026-02-12T00:00:00Z",
      "dueTime": "15:00",
      "tags": ["work", "review"],
      "status": "pending",
      "recurrencePattern": null,
      "parentTaskId": null,
      "createdAt": "2026-02-05T10:30:00Z",
      "updatedAt": "2026-02-06T14:20:00Z"
    },
    "changes": {
      "priority": {"from": "high", "to": "medium"},
      "dueDate": {"from": "2026-02-10T00:00:00Z", "to": "2026-02-12T00:00:00Z"},
      "tags": {"from": ["work", "urgent", "review"], "to": ["work", "review"]}
    }
  }
}
```

**Changes Field**: Documents what changed for audit and notification purposes.

---

### Event: task.completed

**Published by**: Chat API Service

**When**: User marks task as complete

**Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440002",
  "eventType": "task.completed",
  "timestamp": "2026-02-10T15:30:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440005",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "description": "Review the Q1 proposal and provide feedback",
      "priority": "high",
      "dueDate": "2026-02-10T00:00:00Z",
      "dueTime": "15:00",
      "tags": ["work", "urgent", "review"],
      "status": "completed",
      "recurrencePattern": {
        "type": "weekly",
        "interval": 1,
        "daysOfWeek": ["MON"],
        "timezone": "America/New_York",
        "endCondition": {"type": "never"}
      },
      "parentTaskId": null,
      "createdAt": "2026-02-05T10:30:00Z",
      "updatedAt": "2026-02-10T15:30:00Z",
      "completedAt": "2026-02-10T15:30:00Z"
    }
  }
}
```

**Special Handling**: If task has `recurrencePattern`, Recurring Task Service creates next instance.

---

### Event: task.deleted

**Published by**: Chat API Service

**When**: User deletes a task

**Schema**:
```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440003",
  "eventType": "task.deleted",
  "timestamp": "2026-02-11T09:00:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440006",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "taskSnapshot": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "status": "completed",
      "completedAt": "2026-02-10T15:30:00Z"
    }
  }
}
```

**Task Snapshot**: Includes final state before deletion for audit purposes.

---

## Topic: reminders

**Description**: Scheduled reminder notifications

**Consumers**:
- Notification Service (sends notifications)

### Event: reminder.due

**Published by**: Dapr Jobs API (scheduled by Notification Service)

**When**: Task reminder time arrives

**Schema**:
```json
{
  "eventId": "660e8400-e29b-41d4-a716-446655440001",
  "eventType": "reminder.due",
  "timestamp": "2026-02-09T15:00:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440007",
  "sourceService": "dapr-jobs",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "notificationId": "660e8400-e29b-41d4-a716-446655440001",
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "reminderType": "advance",
    "scheduledTime": "2026-02-09T15:00:00Z"
  }
}
```

**Reminder Types**:
- `advance`: Advance reminder (default 24 hours before due)
- `due`: Task is now due

---

## Topic: task-updates

**Description**: Real-time sync updates for connected clients

**Consumers**:
- WebSocket Sync Service (pushes to connected clients)

### Event: sync.task.created

**Published by**: Chat API Service (after task.created event)

**When**: Task created, needs to be synced to clients

**Schema**:
```json
{
  "eventId": "770e8400-e29b-41d4-a716-446655440001",
  "eventType": "sync.task.created",
  "timestamp": "2026-02-05T10:30:01Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440003",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "priority": "high",
      "dueDate": "2026-02-10T00:00:00Z",
      "status": "pending"
    },
    "sequenceNumber": 12345
  }
}
```

**Sequence Number**: Monotonically increasing number for ordering and gap detection.

---

### Event: sync.task.updated

**Published by**: Chat API Service (after task.updated event)

**Schema**:
```json
{
  "eventId": "770e8400-e29b-41d4-a716-446655440002",
  "eventType": "sync.task.updated",
  "timestamp": "2026-02-06T14:20:01Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440004",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "task": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "priority": "medium",
      "dueDate": "2026-02-12T00:00:00Z",
      "status": "pending"
    },
    "sequenceNumber": 12346
  }
}
```

---

### Event: sync.task.completed

**Published by**: Chat API Service (after task.completed event)

**Schema**:
```json
{
  "eventId": "770e8400-e29b-41d4-a716-446655440003",
  "eventType": "sync.task.completed",
  "timestamp": "2026-02-10T15:30:01Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440005",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "completedAt": "2026-02-10T15:30:00Z",
    "sequenceNumber": 12347
  }
}
```

---

### Event: sync.task.deleted

**Published by**: Chat API Service (after task.deleted event)

**Schema**:
```json
{
  "eventId": "770e8400-e29b-41d4-a716-446655440004",
  "eventType": "sync.task.deleted",
  "timestamp": "2026-02-11T09:00:01Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440006",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "sequenceNumber": 12348
  }
}
```

---

### Event: notification.sent

**Published by**: Notification Service

**When**: Notification successfully delivered

**Schema**:
```json
{
  "eventId": "880e8400-e29b-41d4-a716-446655440010",
  "eventType": "notification.sent",
  "timestamp": "2026-02-09T15:00:05Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440007",
  "sourceService": "notification",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "payload": {
    "notificationId": "660e8400-e29b-41d4-a716-446655440001",
    "taskId": "550e8400-e29b-41d4-a716-446655440000",
    "channels": ["in-app", "email"],
    "sentAt": "2026-02-09T15:00:05Z"
  }
}
```

---

## Event Publishing Patterns

### Transactional Outbox Pattern

To ensure events are published reliably after state changes:

1. Save state to Dapr State API
2. Publish event to Dapr PubSub
3. If publish fails, retry with exponential backoff
4. Event includes `eventId` for idempotency

**Example**:
```python
async def create_task(task_data: dict):
    # 1. Save to state store
    await dapr_client.save_state(
        store_name="statestore",
        key=f"chat-api.task.{user_id}.{task_id}",
        value=json.dumps(task_data)
    )

    # 2. Publish event
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": "task.created",
        "timestamp": datetime.utcnow().isoformat(),
        "correlationId": correlation_id,
        "sourceService": "chat-api",
        "userId": user_id,
        "payload": {"task": task_data}
    }

    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic_name="task-events",
        data=json.dumps(event)
    )
```

### Idempotent Event Processing

Consumers must handle duplicate events:

```python
async def handle_task_created(event: dict):
    event_id = event["eventId"]

    # Check if already processed
    processed = await dapr_client.get_state(
        store_name="statestore",
        key=f"processed-events.{event_id}"
    )

    if processed.data:
        return  # Already processed, skip

    # Process event
    await process_task_created(event["payload"]["task"])

    # Mark as processed
    await dapr_client.save_state(
        store_name="statestore",
        key=f"processed-events.{event_id}",
        value="true"
    )
```

---

## Event Versioning

Events follow semantic versioning. Version included in `eventType`:

- `task.created.v1` - Version 1 of task.created event
- `task.created.v2` - Version 2 with breaking changes

**Backward Compatibility**: Consumers should handle multiple versions gracefully.

---

## Dead Letter Queue

Failed events (after 3 retries) moved to dead letter queue for manual inspection:

**Topic**: `task-events-dlq`, `reminders-dlq`, `task-updates-dlq`

**DLQ Event Structure**:
```json
{
  "originalEvent": {},
  "failureReason": "string",
  "failureCount": 3,
  "lastAttempt": "ISO8601 DateTime",
  "movedToDLQAt": "ISO8601 DateTime"
}
```

---

## Summary

Event schemas defined for 3 topics:
- ✅ `task-events`: 4 event types (created, updated, completed, deleted)
- ✅ `reminders`: 1 event type (reminder.due)
- ✅ `task-updates`: 5 event types (sync events + notification.sent)

All events follow consistent envelope structure with idempotency support. Publishing patterns and error handling documented.

Ready to proceed to REST API contracts.
