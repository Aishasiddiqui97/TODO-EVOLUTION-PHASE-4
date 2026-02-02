# SP (Smart Planner) - Phase III Specification

## Overview

SP (Smart Planner) Phase III introduces an AI-powered chatbot interface that enables users to manage their todo tasks through natural language conversation. Users can create, view, update, complete, and delete tasks by simply chatting with the bot, eliminating the need for traditional form-based interfaces.

## User Stories

### US-1: Create Tasks via Natural Language
**As a** user  
**I want to** add tasks by describing them in natural language  
**So that** I can quickly capture todos without filling out forms

**Acceptance Criteria**:
- User can type "Remind me to buy groceries tomorrow"
- System creates task with title "Buy groceries" and due date set to tomorrow
- System confirms task creation with friendly message
- Task appears in user's task list

**Examples**:
- "Add buy milk to my list" → Creates task "Buy milk"
- "I need to finish the report by Friday" → Creates task "Finish the report" with due date Friday
- "Remind me to call mom at 3pm" → Creates task "Call mom" with due time 3pm

### US-2: View Tasks Conversationally
**As a** user  
**I want to** ask about my tasks in natural language  
**So that** I can quickly see what I need to do

**Acceptance Criteria**:
- User can ask "What's on my todo list?"
- System displays all tasks in readable format
- User can filter by asking "What do I need to do today?"
- System shows only tasks due today

**Examples**:
- "Show me my tasks" → Lists all tasks
- "What's due today?" → Lists tasks due today
- "Show pending tasks" → Lists incomplete tasks

### US-3: Complete Tasks via Chat
**As a** user  
**I want to** mark tasks as complete through conversation  
**So that** I can update my progress naturally

**Acceptance Criteria**:
- User can say "I finished buying groceries"
- System marks the task as completed
- System confirms completion with friendly message
- Completed task no longer appears in pending list

**Examples**:
- "Mark 'buy milk' as done" → Completes task
- "I finished the report" → Completes matching task
- "Done with groceries" → Completes task

### US-4: Update Tasks via Chat
**As a** user  
**I want to** modify task details through conversation  
**So that** I can adjust plans without navigating forms

**Acceptance Criteria**:
- User can say "Move the report deadline to Monday"
- System updates the due date
- System confirms the change
- Updated task reflects new details

**Examples**:
- "Change 'call mom' to 'call mom and dad'" → Updates title
- "Move meeting to 4pm" → Updates due time
- "Make the report high priority" → Updates priority

### US-5: Delete Tasks via Chat
**As a** user  
**I want to** remove tasks through conversation  
**So that** I can clean up my list naturally

**Acceptance Criteria**:
- User can say "Delete the buy milk task"
- System removes the task
- System confirms deletion
- Task no longer appears in any list

**Examples**:
- "Remove the groceries task" → Deletes task
- "Delete all completed tasks" → Deletes all completed
- "Get rid of the meeting task" → Deletes task

## Technical Architecture

### System Components

```
┌─────────────┐
│   Frontend  │ (ChatKit UI)
│   Next.js   │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│  Chat API   │ (FastAPI)
│  Endpoint   │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│  AI Agent   │  │  Database   │
│  (OpenAI)   │  │  (Neon PG)  │
└──────┬──────┘  └─────────────┘
       │
       ▼
┌─────────────┐
│  MCP Tools  │
│  (5 tools)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │
│  (Neon PG)  │
└─────────────┘
```

### Data Flow

1. **User Input** → Frontend sends message to `/api/{user_id}/chat`
2. **Authentication** → Verify user identity via JWT
3. **Conversation Load** → Fetch conversation history from database
4. **AI Processing** → OpenAI agent interprets intent and extracts details
5. **Tool Execution** → MCP tools perform database operations
6. **Response Generation** → AI formats friendly response
7. **Persistence** → Save messages to database
8. **Response** → Return to frontend

### Database Schema

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

## MCP Tools Specification

### 1. add_task
**Purpose**: Create a new task

**Parameters**:
- `title` (required): Task title
- `description` (optional): Task description
- `due_date` (optional): ISO 8601 date string
- `priority` (optional): "low", "medium", or "high"
- `user_id` (required): User ID

**Returns**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "due_date": "2026-01-24T00:00:00Z",
    "priority": "medium"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

### 2. list_tasks
**Purpose**: Retrieve and filter tasks

**Parameters**:
- `user_id` (required): User ID
- `filter` (optional): "all", "today", "pending", "completed"
- `search` (optional): Search term

**Returns**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "uuid",
        "title": "Buy groceries",
        "completed": false,
        "due_date": "2026-01-24T00:00:00Z"
      }
    ],
    "count": 1
  },
  "message": "Found 1 task"
}
```

### 3. complete_task
**Purpose**: Mark a task as complete

**Parameters**:
- `user_id` (required): User ID
- `task_id` (optional): Specific task ID
- `task_title` (optional): Task title to match

**Returns**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries",
    "completed": true
  },
  "message": "Task 'Buy groceries' marked as complete"
}
```

### 4. update_task
**Purpose**: Modify task details

**Parameters**:
- `user_id` (required): User ID
- `task_id` (optional): Specific task ID
- `task_title` (optional): Current task title to match
- `new_title` (optional): New title
- `new_due_date` (optional): New due date
- `new_priority` (optional): New priority

**Returns**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries and supplies",
    "due_date": "2026-01-25T00:00:00Z"
  },
  "message": "Task updated successfully"
}
```

### 5. delete_task
**Purpose**: Remove a task

**Parameters**:
- `user_id` (required): User ID
- `task_id` (optional): Specific task ID
- `task_title` (optional): Task title to match

**Returns**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "title": "Buy groceries"
  },
  "message": "Task 'Buy groceries' deleted"
}
```

## Error Handling

### Error Scenarios

| Scenario | Error Code | User Message |
|----------|-----------|--------------|
| Task not found | `task_not_found` | "I couldn't find that task. Could you describe it differently?" |
| Invalid command | `invalid_intent` | "I'm not sure what you'd like me to do. Try 'add task', 'show tasks', or 'mark as done'." |
| DB connection error | `db_error` | "I'm having trouble connecting to the database. Please try again in a moment." |
| AI service down | `ai_error` | "I'm having trouble processing your request. Please try again." |
| Ambiguous request | `ambiguous` | "I found multiple tasks matching that. Which one did you mean?" |

## Success Metrics

- **Intent Accuracy**: 90%+ correct tool selection
- **Response Time**: < 2 seconds for 95% of requests
- **User Satisfaction**: Tasks created 50% faster than forms
- **Error Recovery**: 90% of users can self-recover from errors

## Out of Scope

- Voice input/output
- Task sharing/collaboration
- Recurring tasks
- File attachments
- Calendar integration
- Multi-language support
- Advanced AI features (prioritization suggestions, smart scheduling)
