# API Examples - Event-Driven Todo Chatbot

This document provides comprehensive examples of using the Chat API.

## Base URL

```
http://localhost:8000
```

## Authentication

MVP uses a hardcoded user ID. Production will require JWT authentication.

## Task Management

### Create a Task

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread, and vegetables",
    "priority": "high",
    "dueDate": "2026-02-10",
    "dueTime": "18:00",
    "tags": ["shopping", "urgent"]
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "userId": "user-001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "priority": "high",
  "dueDate": "2026-02-10",
  "dueTime": "18:00",
  "tags": ["shopping", "urgent"],
  "status": "pending",
  "createdAt": "2026-02-06T10:30:00Z",
  "updatedAt": "2026-02-06T10:30:00Z",
  "completedAt": null
}
```

### List All Tasks

**Request:**
```bash
curl http://localhost:8000/api/v1/tasks
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "userId": "user-001",
    "title": "Buy groceries",
    "priority": "high",
    "status": "pending",
    ...
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "userId": "user-001",
    "title": "Finish report",
    "priority": "medium",
    "status": "pending",
    ...
  }
]
```

### List Tasks with Filters

**Filter by status:**
```bash
curl "http://localhost:8000/api/v1/tasks?status=pending"
```

**Filter by priority:**
```bash
curl "http://localhost:8000/api/v1/tasks?priority=high"
```

**Filter by tags:**
```bash
curl "http://localhost:8000/api/v1/tasks?tags=shopping,urgent"
```

**Combine filters:**
```bash
curl "http://localhost:8000/api/v1/tasks?status=pending&priority=high&limit=10"
```

### Get Task by ID

**Request:**
```bash
curl http://localhost:8000/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "userId": "user-001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "priority": "high",
  "dueDate": "2026-02-10",
  "dueTime": "18:00",
  "tags": ["shopping", "urgent"],
  "status": "pending",
  "createdAt": "2026-02-06T10:30:00Z",
  "updatedAt": "2026-02-06T10:30:00Z",
  "completedAt": null
}
```

### Update a Task

**Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "priority": "medium",
    "tags": ["shopping", "cooking"]
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "userId": "user-001",
  "title": "Buy groceries and cook dinner",
  "priority": "medium",
  "tags": ["shopping", "cooking"],
  "status": "pending",
  "updatedAt": "2026-02-06T11:00:00Z",
  ...
}
```

### Complete a Task

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000/complete
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "userId": "user-001",
  "title": "Buy groceries and cook dinner",
  "status": "completed",
  "completedAt": "2026-02-06T19:30:00Z",
  "updatedAt": "2026-02-06T19:30:00Z",
  ...
}
```

### Delete a Task

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response:**
```
HTTP 204 No Content
```

## Chat Interface

### Send a Message

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my tasks"
  }'
```

**Response:**
```json
{
  "message": "Here are your tasks:\n- Buy groceries (Priority: high, Status: pending)\n- Finish report (Priority: medium, Status: pending)",
  "conversationId": "conv-user-001-a1b2c3d4",
  "toolCalls": [
    {
      "tool": "list_tasks",
      "result": "success"
    }
  ]
}
```

### Continue Conversation

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark the first one as complete",
    "conversationId": "conv-user-001-a1b2c3d4"
  }'
```

**Response:**
```json
{
  "message": "I can help you mark a task as complete. Which task would you like to complete? Please provide the task title or ID.",
  "conversationId": "conv-user-001-a1b2c3d4",
  "toolCalls": null
}
```

### Natural Language Task Creation

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to call mom tomorrow at 3pm"
  }'
```

**Response:**
```json
{
  "message": "I can help you create a task. Please provide the task title and any additional details like priority, due date, or tags.",
  "conversationId": "conv-user-001-e5f6g7h8",
  "toolCalls": null
}
```

## Health Check

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "chat-api",
  "version": "1.0.0"
}
```

## API Information

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "chat-api",
  "version": "1.0.0",
  "description": "Event-Driven Todo Chatbot API",
  "endpoints": {
    "health": "/health",
    "chat": "/api/v1/chat",
    "tasks": "/api/v1/tasks"
  }
}
```

## Error Responses

### 400 Bad Request

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "priority": "invalid"
  }'
```

**Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    },
    {
      "loc": ["body", "priority"],
      "msg": "string does not match regex pattern",
      "type": "value_error.str.regex"
    }
  ]
}
```

### 404 Not Found

**Request:**
```bash
curl http://localhost:8000/api/v1/tasks/nonexistent-id
```

**Response:**
```json
{
  "detail": "Task with ID 'nonexistent-id' not found"
}
```

### 500 Internal Server Error

**Response:**
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred"
}
```

## Python Examples

### Using requests library

```python
import requests

BASE_URL = "http://localhost:8000"

# Create a task
response = requests.post(
    f"{BASE_URL}/api/v1/tasks",
    json={
        "title": "Learn Python",
        "priority": "high",
        "tags": ["learning", "programming"]
    }
)
task = response.json()
print(f"Created task: {task['id']}")

# List tasks
response = requests.get(f"{BASE_URL}/api/v1/tasks")
tasks = response.json()
print(f"Total tasks: {len(tasks)}")

# Complete a task
task_id = task['id']
response = requests.patch(f"{BASE_URL}/api/v1/tasks/{task_id}/complete")
print(f"Task completed: {response.status_code == 200}")

# Chat with AI
response = requests.post(
    f"{BASE_URL}/api/v1/chat",
    json={"message": "Show me my tasks"}
)
chat_response = response.json()
print(f"AI: {chat_response['message']}")
```

### Using httpx (async)

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # Create a task
        response = await client.post(
            f"{BASE_URL}/api/v1/tasks",
            json={
                "title": "Async task",
                "priority": "medium"
            }
        )
        task = response.json()
        print(f"Created task: {task['id']}")

        # List tasks
        response = await client.get(f"{BASE_URL}/api/v1/tasks")
        tasks = response.json()
        print(f"Total tasks: {len(tasks)}")

asyncio.run(main())
```

## JavaScript Examples

### Using fetch

```javascript
const BASE_URL = 'http://localhost:8000';

// Create a task
async function createTask() {
  const response = await fetch(`${BASE_URL}/api/v1/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: 'Learn JavaScript',
      priority: 'high',
      tags: ['learning', 'programming']
    })
  });

  const task = await response.json();
  console.log('Created task:', task.id);
  return task;
}

// List tasks
async function listTasks() {
  const response = await fetch(`${BASE_URL}/api/v1/tasks`);
  const tasks = await response.json();
  console.log('Total tasks:', tasks.length);
  return tasks;
}

// Complete a task
async function completeTask(taskId) {
  const response = await fetch(
    `${BASE_URL}/api/v1/tasks/${taskId}/complete`,
    { method: 'PATCH' }
  );

  const task = await response.json();
  console.log('Task completed:', task.status === 'completed');
  return task;
}

// Chat with AI
async function chat(message) {
  const response = await fetch(`${BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message })
  });

  const chatResponse = await response.json();
  console.log('AI:', chatResponse.message);
  return chatResponse;
}

// Run examples
(async () => {
  const task = await createTask();
  await listTasks();
  await completeTask(task.id);
  await chat('Show me my tasks');
})();
```

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- View all endpoints
- Try API calls directly from the browser
- See request/response schemas
- Test authentication (when implemented)
