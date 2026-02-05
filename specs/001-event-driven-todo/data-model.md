# Data Model

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Phase**: 1 - Data Model Design

## Overview

This document defines the data entities, their attributes, relationships, and state transitions for the event-driven Todo Chatbot system. All entities are stored using Dapr State API with PostgreSQL backend.

---

## Entity Definitions

### 1. Task

**Description**: Represents a todo item with priority, due date, tags, and optional recurrence pattern.

**State Key Pattern**: `chat-api.task.{userId}.{taskId}`

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique task identifier | Auto-generated |
| userId | UUID | Yes | Owner of the task | Must be valid user ID |
| title | String | Yes | Task title | 1-500 characters |
| description | String | No | Detailed task description | Max 5000 characters |
| priority | Enum | Yes | Task priority | "high", "medium", "low" |
| dueDate | DateTime | No | When task is due | ISO 8601 format, must be future date |
| dueTime | Time | No | Specific time task is due | HH:MM format, requires dueDate |
| tags | Array[String] | No | Categorization tags | Max 100 tags, each 1-50 chars |
| status | Enum | Yes | Task completion status | "pending", "completed" |
| recurrencePattern | RecurrencePattern | No | Recurring task pattern | See RecurrencePattern entity |
| parentTaskId | UUID | No | Parent task if this is recurring instance | Must be valid task ID |
| createdAt | DateTime | Yes | Creation timestamp | ISO 8601 format, auto-set |
| updatedAt | DateTime | Yes | Last update timestamp | ISO 8601 format, auto-updated |
| completedAt | DateTime | No | Completion timestamp | ISO 8601 format, set when status=completed |

**Relationships**:
- Task → User (many-to-one): Each task belongs to one user
- Task → Task (one-to-many): Parent task can have multiple recurring instances
- Task → Notification (one-to-many): Each task can have multiple scheduled notifications

**State Transitions**:
```
pending → completed (user marks task complete)
completed → pending (user reopens task)
```

**Indexes** (via Dapr State API queries):
- userId + status (for listing user's pending/completed tasks)
- userId + dueDate (for finding tasks due soon)
- userId + tags (for filtering by tags)

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
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
  "updatedAt": "2026-02-05T10:30:00Z",
  "completedAt": null
}
```

---

### 2. RecurrencePattern

**Description**: Defines how a task repeats (daily, weekly, custom intervals).

**Embedded in Task entity** (not stored separately)

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| type | Enum | Yes | Pattern type | "daily", "weekly", "custom" |
| interval | Integer | Yes | Repeat every N days/weeks | 1-365 for daily, 1-52 for weekly |
| daysOfWeek | Array[String] | Conditional | Days for weekly pattern | Required if type=weekly, ["MON","TUE","WED","THU","FRI","SAT","SUN"] |
| timezone | String | Yes | Timezone for scheduling | IANA timezone (e.g., "America/New_York") |
| endCondition | Object | No | When recurrence stops | See EndCondition below |

**EndCondition** (nested object):

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| type | Enum | Yes | End condition type | "never", "afterOccurrences", "byDate" |
| occurrences | Integer | Conditional | Number of occurrences | Required if type=afterOccurrences, 1-1000 |
| endDate | DateTime | Conditional | End date | Required if type=byDate, ISO 8601 format |

**Example**:
```json
{
  "type": "weekly",
  "interval": 1,
  "daysOfWeek": ["MON", "WED", "FRI"],
  "timezone": "America/New_York",
  "endCondition": {
    "type": "afterOccurrences",
    "occurrences": 10
  }
}
```

---

### 3. Notification

**Description**: Represents a scheduled notification/reminder for a task.

**State Key Pattern**: `notification.reminder.{notificationId}`

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | UUID | Yes | Unique notification identifier | Auto-generated |
| taskId | UUID | Yes | Associated task | Must be valid task ID |
| userId | UUID | Yes | Recipient user | Must be valid user ID |
| scheduledTime | DateTime | Yes | When to send notification | ISO 8601 format, must be future |
| channels | Array[String] | Yes | Delivery channels | ["in-app", "email"] |
| status | Enum | Yes | Notification status | "scheduled", "sent", "failed" |
| sentAt | DateTime | No | When notification was sent | ISO 8601 format |
| retryCount | Integer | Yes | Number of retry attempts | 0-3, default 0 |
| lastError | String | No | Last error message if failed | Max 1000 characters |
| createdAt | DateTime | Yes | Creation timestamp | ISO 8601 format, auto-set |

**State Transitions**:
```
scheduled → sent (notification delivered successfully)
scheduled → failed (delivery failed after 3 retries)
failed → scheduled (manual retry)
```

**Example**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "scheduledTime": "2026-02-09T15:00:00Z",
  "channels": ["in-app", "email"],
  "status": "scheduled",
  "sentAt": null,
  "retryCount": 0,
  "lastError": null,
  "createdAt": "2026-02-05T10:30:00Z"
}
```

---

### 4. TaskEvent

**Description**: Audit log entry for task lifecycle events.

**State Key Pattern**: `audit-log.event.{eventId}`

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| eventId | UUID | Yes | Unique event identifier | Auto-generated |
| eventType | Enum | Yes | Type of event | "task.created", "task.updated", "task.completed", "task.deleted" |
| timestamp | DateTime | Yes | When event occurred | ISO 8601 format, auto-set |
| correlationId | UUID | Yes | Request correlation ID | For tracing related events |
| sourceService | String | Yes | Service that generated event | "chat-api", "recurring-task", etc. |
| userId | UUID | Yes | User who triggered event | Must be valid user ID |
| taskSnapshot | Object | Yes | Task state at event time | Full Task object |
| changes | Object | No | What changed (for updates) | Key-value pairs of changed fields |

**Retention**: Events retained for 90 days (configurable)

**Example**:
```json
{
  "eventId": "770e8400-e29b-41d4-a716-446655440002",
  "eventType": "task.completed",
  "timestamp": "2026-02-10T15:30:00Z",
  "correlationId": "880e8400-e29b-41d4-a716-446655440003",
  "sourceService": "chat-api",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "taskSnapshot": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review proposal document",
    "status": "completed",
    "completedAt": "2026-02-10T15:30:00Z"
  },
  "changes": {
    "status": {"from": "pending", "to": "completed"},
    "completedAt": {"from": null, "to": "2026-02-10T15:30:00Z"}
  }
}
```

---

### 5. UserPreferences

**Description**: User settings for notifications, reminders, and defaults.

**State Key Pattern**: `chat-api.preferences.{userId}`

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| userId | UUID | Yes | User identifier | Must be valid user ID |
| notificationChannels | Array[String] | Yes | Enabled channels | ["in-app", "email"], default both |
| reminderAdvanceTime | Integer | Yes | Hours before due time | 1-168 (1 week), default 24 |
| defaultPriority | Enum | Yes | Default task priority | "high", "medium", "low", default "medium" |
| timezone | String | Yes | User timezone | IANA timezone, default "UTC" |
| emailAddress | String | Yes | Email for notifications | Valid email format |
| updatedAt | DateTime | Yes | Last update timestamp | ISO 8601 format, auto-updated |

**Example**:
```json
{
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "notificationChannels": ["in-app", "email"],
  "reminderAdvanceTime": 24,
  "defaultPriority": "medium",
  "timezone": "America/New_York",
  "emailAddress": "user@example.com",
  "updatedAt": "2026-02-05T10:00:00Z"
}
```

---

### 6. WebSocketConnection

**Description**: Active real-time connection metadata (stored in-memory, not persisted).

**Storage**: In-memory only (not in Dapr State API)

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| connectionId | UUID | Yes | Unique connection identifier | Auto-generated |
| userId | UUID | Yes | Connected user | Must be valid user ID |
| connectedAt | DateTime | Yes | Connection timestamp | ISO 8601 format, auto-set |
| lastActivity | DateTime | Yes | Last message timestamp | ISO 8601 format, auto-updated |
| clientInfo | Object | No | Client metadata | Browser, device, IP address |

**Lifecycle**: Connection removed from memory on disconnect or 30-minute timeout.

**Example**:
```json
{
  "connectionId": "990e8400-e29b-41d4-a716-446655440004",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "connectedAt": "2026-02-05T10:00:00Z",
  "lastActivity": "2026-02-05T10:15:00Z",
  "clientInfo": {
    "browser": "Chrome 120",
    "device": "Desktop",
    "ipAddress": "192.168.1.100"
  }
}
```

---

### 7. Conversation

**Description**: Chat conversation history for AI context (from Phase III).

**State Key Pattern**: `chat-api.conversation.{userId}`

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| userId | UUID | Yes | User identifier | Must be valid user ID |
| messages | Array[Message] | Yes | Conversation messages | Max 100 messages, oldest pruned |
| updatedAt | DateTime | Yes | Last update timestamp | ISO 8601 format, auto-updated |

**Message** (nested object):

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| role | Enum | Yes | Message role | "user", "assistant" |
| content | String | Yes | Message text | Max 10000 characters |
| timestamp | DateTime | Yes | Message timestamp | ISO 8601 format |

**Example**:
```json
{
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "role": "user",
      "content": "Create a high-priority task to review proposal by Friday",
      "timestamp": "2026-02-05T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I've created a high-priority task 'Review proposal' with due date Friday, February 7th.",
      "timestamp": "2026-02-05T10:30:05Z"
    }
  ],
  "updatedAt": "2026-02-05T10:30:05Z"
}
```

---

## Entity Relationships

```
User (1) ──────< (N) Task
                      │
                      ├──< (N) Notification
                      │
                      └──< (N) TaskEvent

Task (1) ──────< (N) Task (recurring instances)

User (1) ────── (1) UserPreferences

User (1) ──────< (N) WebSocketConnection

User (1) ────── (1) Conversation
```

---

## State Key Naming Conventions

All state keys follow pattern: `{service}.{entity}.{scope}.{id}`

**Examples**:
- `chat-api.task.user123.task456` - Task owned by user123
- `chat-api.conversation.user123` - Conversation for user123
- `chat-api.preferences.user123` - Preferences for user123
- `notification.reminder.reminder789` - Notification reminder
- `audit-log.event.event999` - Audit log event

**Rationale**: Service prefix prevents cross-service state access, enforcing bounded contexts.

---

## Data Validation Rules

### Task Validation

1. **Title**: Required, 1-500 characters, no leading/trailing whitespace
2. **Priority**: Must be one of: "high", "medium", "low"
3. **Due Date**: If provided, must be future date (or today)
4. **Due Time**: Requires dueDate to be set
5. **Tags**: Max 100 tags, each 1-50 characters, lowercase, alphanumeric + hyphens
6. **Recurrence Pattern**: If provided, must have valid type and interval
7. **Status**: Must be "pending" or "completed"

### RecurrencePattern Validation

1. **Type**: Must be "daily", "weekly", or "custom"
2. **Interval**: 1-365 for daily, 1-52 for weekly
3. **Days of Week**: Required for weekly, must be valid day codes
4. **Timezone**: Must be valid IANA timezone
5. **End Condition**: If provided, must have valid type and required fields

### Notification Validation

1. **Scheduled Time**: Must be future timestamp
2. **Channels**: Must include at least one of: "in-app", "email"
3. **Retry Count**: 0-3, incremented on failure
4. **Status**: Must be "scheduled", "sent", or "failed"

---

## Data Migration Strategy

### Phase III → Phase V Migration

**Existing Data**:
- Tasks (from Phase III)
- Conversations (from Phase III)
- Users (from Phase III)

**New Data**:
- RecurrencePattern (new field in Task)
- Notification (new entity)
- TaskEvent (new entity)
- UserPreferences (new entity)
- WebSocketConnection (in-memory only)

**Migration Steps**:
1. Add new fields to Task entity (recurrencePattern, tags, priority defaults)
2. Create UserPreferences for existing users with defaults
3. No data loss - all Phase III data remains compatible
4. New features (recurring, notifications) opt-in for existing tasks

**Backward Compatibility**: Phase III tasks work without modification. New fields optional.

---

## Summary

Data model defined with 7 entities:
- ✅ Task (core entity with priorities, due dates, tags, recurrence)
- ✅ RecurrencePattern (embedded in Task)
- ✅ Notification (scheduled reminders)
- ✅ TaskEvent (audit trail)
- ✅ UserPreferences (user settings)
- ✅ WebSocketConnection (real-time sync)
- ✅ Conversation (AI chat history from Phase III)

All entities use Dapr State API with clear key naming conventions. Validation rules ensure data integrity. Migration strategy preserves Phase III compatibility.

Ready to proceed to API and Event Contracts.
