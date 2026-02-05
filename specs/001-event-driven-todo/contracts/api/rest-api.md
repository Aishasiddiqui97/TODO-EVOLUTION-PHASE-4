# REST API Contracts

**Feature**: Event-Driven Todo Chatbot with Advanced Features
**Date**: 2026-02-05
**Version**: 1.0.0

## Overview

This document defines the REST API contracts for the Chat API Service. The Chat API is the primary user-facing service that handles natural language interactions via MCP tools.

**Base URL**: `http://localhost:8000/api/v1` (local) or `https://api.todo.example.com/api/v1` (production)

**Authentication**: JWT Bearer token in Authorization header

---

## Chat API Service

### POST /chat/message

**Description**: Send a message to the AI chatbot

**Authentication**: Required

**Request**:
```json
{
  "message": "Create a high-priority task to review proposal by Friday",
  "conversationId": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (200 OK):
```json
{
  "response": "I've created a high-priority task 'Review proposal' with due date Friday, February 7th.",
  "conversationId": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2026-02-05T10:30:05Z",
  "actions": [
    {
      "type": "task_created",
      "taskId": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

**Error Responses**:
- 401 Unauthorized: Invalid or missing auth token
- 400 Bad Request: Invalid message format
- 500 Internal Server Error: Processing failed

---

### GET /tasks

**Description**: List user's tasks with optional filtering

**Authentication**: Required

**Query Parameters**:
- `status` (optional): Filter by status ("pending", "completed")
- `priority` (optional): Filter by priority ("high", "medium", "low")
- `tags` (optional): Comma-separated tags to filter by
- `dueBefore` (optional): ISO 8601 date to filter tasks due before
- `dueAfter` (optional): ISO 8601 date to filter tasks due after
- `limit` (optional): Max results (default 50, max 100)
- `offset` (optional): Pagination offset (default 0)

**Request**:
```
GET /tasks?status=pending&priority=high&limit=20
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Review proposal document",
      "description": "Review the Q1 proposal and provide feedback",
      "priority": "high",
      "dueDate": "2026-02-10T00:00:00Z",
      "dueTime": "15:00",
      "tags": ["work", "urgent", "review"],
      "status": "pending",
      "recurrencePattern": null,
      "createdAt": "2026-02-05T10:30:00Z",
      "updatedAt": "2026-02-05T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### GET /tasks/{taskId}

**Description**: Get a specific task by ID

**Authentication**: Required

**Path Parameters**:
- `taskId`: UUID of the task

**Response** (200 OK):
```json
{
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
  "updatedAt": "2026-02-05T10:30:00Z",
  "completedAt": null
}
```

**Error Responses**:
- 404 Not Found: Task not found or not owned by user

---

### GET /preferences

**Description**: Get user preferences

**Authentication**: Required

**Response** (200 OK):
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

### PUT /preferences

**Description**: Update user preferences

**Authentication**: Required

**Request**:
```json
{
  "notificationChannels": ["in-app", "email"],
  "reminderAdvanceTime": 48,
  "defaultPriority": "high",
  "timezone": "America/Los_Angeles"
}
```

**Response** (200 OK):
```json
{
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "notificationChannels": ["in-app", "email"],
  "reminderAdvanceTime": 48,
  "defaultPriority": "high",
  "timezone": "America/Los_Angeles",
  "emailAddress": "user@example.com",
  "updatedAt": "2026-02-05T11:00:00Z"
}
```

---

### GET /health

**Description**: Health check endpoint

**Authentication**: Not required

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "chat-api",
  "version": "1.0.0",
  "timestamp": "2026-02-05T10:00:00Z",
  "dependencies": {
    "dapr": "healthy",
    "statestore": "healthy",
    "pubsub": "healthy"
  }
}
```

---

## WebSocket Sync Service

### WebSocket /ws

**Description**: WebSocket endpoint for real-time task updates

**Authentication**: Required (token in query param or initial message)

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8001/ws?token=<jwt_token>');
```

**Client → Server Messages**:

**Ping** (keep-alive):
```json
{
  "type": "ping",
  "timestamp": "2026-02-05T10:00:00Z"
}
```

**Server → Client Messages**:

**Pong** (keep-alive response):
```json
{
  "type": "pong",
  "timestamp": "2026-02-05T10:00:01Z"
}
```

**Task Update**:
```json
{
  "type": "task_update",
  "action": "created",
  "task": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Review proposal document",
    "priority": "high",
    "status": "pending"
  },
  "sequenceNumber": 12345,
  "timestamp": "2026-02-05T10:30:01Z"
}
```

**Notification**:
```json
{
  "type": "notification",
  "notificationId": "660e8400-e29b-41d4-a716-446655440001",
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Reminder: Review proposal document is due in 24 hours",
  "timestamp": "2026-02-09T15:00:05Z"
}
```

**Connection Closed**:
```json
{
  "type": "close",
  "reason": "timeout",
  "timestamp": "2026-02-05T10:30:00Z"
}
```

---

## MCP Tools (Internal)

These are MCP tools used by the AI agent, not exposed as REST endpoints.

### create_task

**Description**: Create a new task

**Parameters**:
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "priority": "high|medium|low (optional, default: medium)",
  "dueDate": "ISO 8601 date (optional)",
  "dueTime": "HH:MM (optional)",
  "tags": ["string"] (optional),
  "recurrencePattern": {
    "type": "daily|weekly|custom",
    "interval": "integer",
    "daysOfWeek": ["MON", "TUE", ...] (for weekly),
    "timezone": "IANA timezone",
    "endCondition": {
      "type": "never|afterOccurrences|byDate",
      "occurrences": "integer (optional)",
      "endDate": "ISO 8601 date (optional)"
    }
  } (optional)
}
```

**Returns**:
```json
{
  "success": true,
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Task created successfully"
}
```

---

### update_task

**Description**: Update an existing task

**Parameters**:
```json
{
  "taskId": "UUID (required)",
  "title": "string (optional)",
  "description": "string (optional)",
  "priority": "high|medium|low (optional)",
  "dueDate": "ISO 8601 date (optional)",
  "dueTime": "HH:MM (optional)",
  "tags": ["string"] (optional)
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Task updated successfully"
}
```

---

### complete_task

**Description**: Mark a task as complete

**Parameters**:
```json
{
  "taskId": "UUID (required)"
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Task marked as complete"
}
```

---

### delete_task

**Description**: Delete a task

**Parameters**:
```json
{
  "taskId": "UUID (required)"
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

---

### list_tasks

**Description**: List user's tasks with filtering

**Parameters**:
```json
{
  "status": "pending|completed (optional)",
  "priority": "high|medium|low (optional)",
  "tags": ["string"] (optional),
  "dueBefore": "ISO 8601 date (optional)",
  "dueAfter": "ISO 8601 date (optional)",
  "limit": "integer (optional, default 50)"
}
```

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "UUID",
      "title": "string",
      "priority": "high|medium|low",
      "dueDate": "ISO 8601 date",
      "status": "pending|completed",
      "tags": ["string"]
    }
  ],
  "total": 10
}
```

---

### search_tasks

**Description**: Search tasks by text query

**Parameters**:
```json
{
  "query": "string (required)",
  "limit": "integer (optional, default 20)"
}
```

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": "UUID",
      "title": "string",
      "description": "string",
      "relevanceScore": 0.95
    }
  ],
  "total": 5
}
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "timestamp": "2026-02-05T10:00:00Z",
    "correlationId": "880e8400-e29b-41d4-a716-446655440003"
  }
}
```

**Common Error Codes**:
- `UNAUTHORIZED`: Authentication failed
- `FORBIDDEN`: User doesn't have permission
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid request data
- `INTERNAL_ERROR`: Server error
- `SERVICE_UNAVAILABLE`: Dependency unavailable

---

## Rate Limiting

**Limits**:
- Chat API: 60 requests/minute per user
- Task API: 120 requests/minute per user
- WebSocket: 1 connection per user per device

**Rate Limit Headers**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1675598400
```

**Rate Limit Exceeded** (429 Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "retryAfter": 30
  }
}
```

---

## CORS Configuration

**Allowed Origins**:
- Local: `http://localhost:3000`, `http://localhost:3001`
- Production: `https://app.todo.example.com`

**Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers**: Authorization, Content-Type, X-Correlation-Id

---

## Summary

REST API contracts defined:
- ✅ Chat API endpoints (message, tasks, preferences, health)
- ✅ WebSocket protocol for real-time sync
- ✅ MCP tools for AI agent (6 tools)
- ✅ Error response format
- ✅ Rate limiting and CORS

Ready to proceed to Dapr component configurations.
