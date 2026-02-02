# SP (Smart Planner) Constitution

## Core Principles

### 1. Stateless Server Architecture
**Principle**: The server MUST NOT store session or conversation state in memory.

**Rationale**: Enables horizontal scaling, fault tolerance, and simplified deployment across multiple instances.

**Implementation Requirements**:
- Each request fetches conversation history from database
- No in-memory session storage
- Conversation service loads history per request
- Server can be restarted without losing state

### 2. AI Logic Separation
**Principle**: AI agent MUST NOT directly access the database.

**Rationale**: Clear separation of concerns, better testability, and standardized tool protocol.

**Implementation Requirements**:
- OpenAI Agents SDK handles all natural language understanding
- AI agent only calls MCP tools
- Tools handle all database operations
- No direct database imports in AI layer

### 3. MCP Tool-Based Operations
**Principle**: All CRUD operations MUST go through MCP tools.

**Rationale**: Standardized interface, better logging, and easier testing/monitoring.

**Implementation Requirements**:
- 5 core tools: `add_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task`
- Tools are stateless functions
- Each tool persists changes immediately to database
- Tools return structured results for AI agent

### 4. Conversation State Persistence
**Principle**: Conversation history MUST be maintained across sessions.

**Rationale**: Users expect context to be preserved between chat sessions.

**Implementation Requirements**:
- Conversation and Message models in database
- History maintained with timestamps
- ConversationService and MessageService handle persistence
- Context window limited to last 20 messages for performance

### 5. User Confirmations
**Principle**: Every operation MUST return a friendly confirmation.

**Rationale**: Users need clear feedback that their request was understood and executed.

**Implementation Requirements**:
- AI response formatter creates conversational confirmations
- Confirmations include specific details (task title, due date, etc.)
- Errors are explained in user-friendly language
- No technical jargon in user-facing messages

### 6. Error Handling
**Principle**: Errors MUST be handled gracefully without exposing technical details.

**Rationale**: Users should receive actionable error messages, not stack traces.

**Implementation Requirements**:
- Error handler middleware catches all exceptions
- AI-friendly error messages for common scenarios
- Retry suggestions for transient failures
- Logging for debugging without exposing to users

## Agent Behavior Contract

### Intent Classification
The AI agent MUST correctly map user intents to MCP tools:

| User Intent | MCP Tool | Example Phrases |
|------------|---------|----------------|
| Add task | `add_task` | "Add...", "Create...", "Remind me to..." |
| Show tasks | `list_tasks` | "Show...", "What's on my list?", "List..." |
| Complete task | `complete_task` | "Mark as done", "I finished...", "Complete..." |
| Delete task | `delete_task` | "Delete...", "Remove...", "Get rid of..." |
| Update task | `update_task` | "Change...", "Update...", "Move deadline..." |

### Error Response Contract
The system MUST handle these error scenarios gracefully:

1. **Task Not Found**: Polite message suggesting alternatives
2. **Invalid Command**: Clarification request with examples
3. **DB Error**: Generic retry message without technical details
4. **AI Service Down**: Graceful degradation with retry option

## Chat Endpoint Flow

The chat endpoint MUST follow this exact sequence:

1. **User message receive** - Accept message from authenticated user
2. **Conversation fetch from DB** - Load or create conversation
3. **Message array build** - Construct context from last 20 messages
4. **User message store** - Persist user message immediately
5. **Agent run with MCP tools** - Process through AI agent
6. **Tool execution** - Execute MCP tools as needed
7. **Assistant response store** - Persist AI response
8. **Response return** - Return to client

## Non-Negotiable Requirements

### Security
- All endpoints MUST require authentication
- Users can ONLY access their own tasks and conversations
- No SQL injection vulnerabilities (use parameterized queries)
- API keys MUST NOT be exposed in logs or responses

### Performance
- Chat response time: < 2 seconds for 95% of requests
- Database queries: < 500ms completion time
- Support 100+ concurrent conversations
- Conversation history limited to prevent memory issues

### Data Integrity
- All database operations MUST be atomic
- Failed operations MUST NOT leave partial state
- Conversation history MUST be accurate and complete
- Timestamps MUST be UTC

## Folder Structure Contract

```
/specs
  ├── SP-CONSTITUTION.md      # This file
  ├── SP-SPECIFICATION.md     # Feature specification
  ├── SP-TASKS.md             # Implementation tasks
  ├── SP-PLAN.md              # Technical plan
  └── SP-IMPLEMENTATION.md    # Implementation guide

/backend
  ├── main.py                 # FastAPI entry point
  ├── api/chat.py             # Chat endpoint
  ├── agents/todo_agent.py    # AI agent (or ai/agent.py)
  ├── mcp/server.py           # MCP server
  ├── mcp/tools.py            # Tool implementations
  ├── models/                 # Database models
  ├── db/                     # Database connection
  └── auth/                   # Authentication

/frontend
  └── chatkit-ui              # Chat interface
```

## Validation Checklist

Before considering Phase III complete, verify:

- [ ] Server is stateless (can restart without losing state)
- [ ] AI agent never directly accesses database
- [ ] All 5 MCP tools are implemented and registered
- [ ] Conversation history persists across sessions
- [ ] All operations return user-friendly confirmations
- [ ] Error handling is graceful and actionable
- [ ] Chat endpoint follows the 8-step flow
- [ ] Intent mapping is accurate (90%+ success rate)
- [ ] Response time is < 2 seconds
- [ ] Authentication is enforced on all endpoints
