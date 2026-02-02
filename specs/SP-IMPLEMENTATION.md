# SP Implementation Guide - Phase III

## Current Status

### ✅ Completed
- Chat endpoint infrastructure (`/api/{user_id}/chat`)
- AI agent integration (OpenAI Agents SDK)
- MCP server framework
- `add_task` MCP tool
- Conversation and message persistence
- Authentication middleware
- Stateless architecture

### 🚧 In Progress
- Remaining MCP tools (list, complete, update, delete)
- Tool registry configuration
- End-to-end testing

### ⏳ Pending
- Frontend ChatKit integration
- Production deployment
- Performance optimization

## Implementation Steps

### Step 1: Implement list_tasks Tool

**File**: `backend/src/mcp/tools/list_tasks.py`

**Purpose**: Retrieve and filter tasks based on user criteria

**Key Features**:
- Filter by status (all, pending, completed)
- Filter by due date (today, overdue, upcoming)
- Search by title/description
- Return structured task list with count

**Dependencies**:
- `TaskService` for database queries
- `MCPTool` base class

### Step 2: Implement complete_task Tool

**File**: `backend/src/mcp/tools/complete_task.py`

**Purpose**: Mark tasks as complete

**Key Features**:
- Match by task ID (exact match)
- Match by task title (fuzzy match)
- Handle task not found gracefully
- Return updated task details

**Dependencies**:
- `TaskService.update_task()`
- Task matching logic

### Step 3: Implement update_task Tool

**File**: `backend/src/mcp/tools/update_task.py`

**Purpose**: Update task details (title, due date, priority, etc.)

**Key Features**:
- Partial updates (only specified fields)
- Match by task ID or title
- Support updating: title, description, due_date, priority
- Handle task not found gracefully

**Dependencies**:
- `TaskService.update_task()`
- Task matching logic

### Step 4: Implement delete_task Tool

**File**: `backend/src/mcp/tools/delete_task.py`

**Purpose**: Remove tasks from the database

**Key Features**:
- Match by task ID or title
- Return deleted task details for confirmation
- Handle task not found gracefully

**Dependencies**:
- `TaskService.delete_task()`
- Task matching logic

### Step 5: Update Tool Registry

**File**: `backend/src/mcp/registry.py`

**Changes**:
1. Import all 5 tools
2. Register each tool in `register_all()` method
3. Verify registration count

**Code Pattern**:
```python
from .tools.add_task import AddTaskTool
from .tools.list_tasks import ListTasksTool
from .tools.complete_task import CompleteTaskTool
from .tools.update_task import UpdateTaskTool
from .tools.delete_task import DeleteTaskTool

def register_all(self):
    self.register(AddTaskTool())
    self.register(ListTasksTool())
    self.register(CompleteTaskTool())
    self.register(UpdateTaskTool())
    self.register(DeleteTaskTool())
```

### Step 6: Initialize Tools at Startup

**File**: `backend/src/main.py`

**Changes**:
Add startup event to initialize tools:
```python
@app.on_event("startup")
async def startup_event():
    from .mcp.registry import initialize_tools
    initialize_tools()
```

### Step 7: Testing

#### Unit Tests
Create test files for each tool in `backend/tests/unit/`:
- `test_list_tasks_tool.py`
- `test_complete_task_tool.py`
- `test_update_task_tool.py`
- `test_delete_task_tool.py`

#### Integration Tests
Update `backend/tests/integration/test_chat_endpoint.py` to test:
- All 5 tool operations via chat
- Multi-turn conversations
- Error scenarios

#### Manual Testing
Use curl or Postman to test chat endpoint with various natural language inputs

## Agent Behavior Mapping

The AI agent should map user intents to MCP tools as follows:

| User Intent | Example Phrases | MCP Tool | Expected Behavior |
|------------|----------------|---------|-------------------|
| Add task | "Add...", "Create...", "Remind me..." | `add_task` | Create new task with extracted details |
| Show tasks | "Show...", "List...", "What's on my list?" | `list_tasks` | Return filtered task list |
| Complete task | "Mark as done", "I finished...", "Complete..." | `complete_task` | Set task.completed = true |
| Update task | "Change...", "Update...", "Move deadline..." | `update_task` | Update specified task fields |
| Delete task | "Delete...", "Remove...", "Get rid of..." | `delete_task` | Remove task from database |

## Error Handling Patterns

### Task Not Found
```python
return self._error_response(
    "task_not_found",
    "I couldn't find that task. Could you describe it differently?"
)
```

### Invalid Command
```python
return self._error_response(
    "invalid_intent",
    "I'm not sure what you'd like me to do. Try 'add task', 'show tasks', or 'mark as done'."
)
```

### Database Error
```python
return self._error_response(
    "db_error",
    "I'm having trouble connecting to the database. Please try again in a moment."
)
```

### Ambiguous Request
```python
return self._error_response(
    "ambiguous",
    f"I found {count} tasks matching that. Which one did you mean? {suggestions}"
)
```

## Chat Endpoint Flow (Verification)

The chat endpoint follows this exact sequence:

1. ✅ **User message receive** - Accept message from authenticated user
2. ✅ **Conversation fetch from DB** - Load or create conversation
3. ✅ **Message array build** - Construct context from last 20 messages
4. ✅ **User message store** - Persist user message immediately
5. ✅ **Agent run with MCP tools** - Process through AI agent
6. ✅ **Tool execution** - Execute MCP tools as needed
7. ✅ **Assistant response store** - Persist AI response
8. ✅ **Response return** - Return to client

All steps are already implemented in `backend/src/api/routes/chat.py`.

## Deployment Checklist

Before deploying to production:

- [ ] All 5 MCP tools implemented
- [ ] Tool registry configured
- [ ] All tests passing
- [ ] Error handling verified
- [ ] Performance tested (< 2s response time)
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Monitoring and logging set up
- [ ] Frontend integrated
- [ ] User acceptance testing complete

## Next Steps

1. Implement remaining MCP tools (list, complete, update, delete)
2. Update tool registry
3. Run automated tests
4. Perform manual testing
5. Integrate with frontend
6. Deploy to production

## References

- [SP-CONSTITUTION.md](file:///E:/Python.py/Hackaton%202(1)/specs/SP-CONSTITUTION.md) - Core principles
- [SP-SPECIFICATION.md](file:///E:/Python.py/Hackaton%202(1)/specs/SP-SPECIFICATION.md) - Feature specification
- [SP-TASKS.md](file:///E:/Python.py/Hackaton%202(1)/specs/SP-TASKS.md) - Task breakdown
- [SP-PLAN.md](file:///E:/Python.py/Hackaton%202(1)/specs/SP-PLAN.md) - Implementation plan
