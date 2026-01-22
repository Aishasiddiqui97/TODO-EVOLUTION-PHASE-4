# Research: AI-Powered Todo Chatbot (Phase III)

**Date**: 2026-01-22
**Feature**: 003-ai-chatbot-mcp
**Purpose**: Document technology decisions, best practices, and implementation patterns

## Technology Stack Decisions

All technology choices for Phase III are mandated by the project constitution (v1.1.0). This document captures best practices and implementation patterns for each technology.

---

## 1. FastAPI (Backend Framework)

### Decision
Use FastAPI 0.115+ as the backend framework

### Rationale
- Mandated by Phase III constitution
- High performance (async/await support)
- Automatic OpenAPI documentation
- Type hints and validation with Pydantic
- Excellent for building REST APIs

### Best Practices

**Project Structure**:
```python
# Layered architecture
backend/src/
├── main.py           # Application entry, CORS, middleware
├── api/              # Routes and endpoints
├── services/         # Business logic
├── models/           # Database models
├── mcp/              # MCP tools
└── ai/               # AI agent logic
```

**Async/Await**:
- Use `async def` for all route handlers
- Use `await` for database queries
- Use `asyncio` for concurrent operations

**Dependency Injection**:
```python
from fastapi import Depends

def get_db():
    # Database session
    pass

@app.post("/api/chat")
async def chat(db = Depends(get_db)):
    # Use db here
    pass
```

**Error Handling**:
```python
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )
```

**CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 2. OpenAI Agents SDK (AI Framework)

### Decision
Use OpenAI Agents SDK for natural language understanding and tool calling

### Rationale
- Mandated by Phase III constitution
- Native tool calling support
- High accuracy for intent classification
- Maintained by OpenAI
- Integrates well with MCP

### Best Practices

**Agent Initialization**:
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_agent():
    return client.beta.assistants.create(
        name="Todo Chatbot",
        instructions="You are a helpful assistant...",
        tools=[...],  # MCP tools
        model="gpt-4-turbo-preview"
    )
```

**Tool Calling Pattern**:
```python
# Define tools in OpenAI format
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "due_date": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    }
]
```

**Intent Classification**:
- Use system prompts to guide intent detection
- Provide few-shot examples for common intents
- Handle ambiguous cases with clarification questions

**Context Management**:
- Limit context window to last 20 messages
- Summarize older messages if needed
- Include relevant task context in prompts

---

## 3. MCP (Model Context Protocol)

### Decision
Use official MCP SDK for tool-based operations

### Rationale
- Mandated by Phase III constitution
- Standardized protocol for tool execution
- Better observability and testing
- Clear separation between AI and data layers

### Best Practices

**Tool Structure**:
```python
from mcp import Tool

class AddTaskTool(Tool):
    name = "add_task"
    description = "Create a new task"

    async def execute(self, title: str, due_date: str = None):
        # Stateless function
        # Persist to database immediately
        task = await task_service.create(title, due_date)
        return {"task_id": task.id, "message": "Task created"}
```

**Tool Registry**:
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    async def execute(self, tool_name: str, **kwargs):
        tool = self.tools.get(tool_name)
        return await tool.execute(**kwargs)
```

**Error Handling in Tools**:
- Return structured error responses
- Include error codes for AI agent to interpret
- Log all tool calls for debugging

**Tool Testing**:
- Test each tool independently
- Mock database for unit tests
- Integration tests with real database

---

## 4. Neon Serverless PostgreSQL

### Decision
Use Neon Serverless PostgreSQL for data persistence

### Rationale
- Mandated by Phase III constitution
- Serverless scaling (auto-scales to zero)
- Connection pooling built-in
- Automatic backups
- Cost-effective for variable workloads

### Best Practices

**Connection Management**:
```python
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session
```

**Connection Pooling**:
- Neon handles pooling automatically
- Use `pool_pre_ping=True` for connection health checks
- Set reasonable pool size limits

**Migrations with Alembic**:
```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add conversation tables"

# Apply migration
alembic upgrade head
```

**Indexing Strategy**:
```sql
-- Index for conversation retrieval
CREATE INDEX idx_conversation_user_id ON conversations(user_id);
CREATE INDEX idx_message_conversation_id ON messages(conversation_id);

-- Index for task queries
CREATE INDEX idx_task_user_id ON tasks(user_id);
CREATE INDEX idx_task_due_date ON tasks(due_date);
```

---

## 5. SQLModel (ORM)

### Decision
Use SQLModel 0.0.22+ as the ORM

### Rationale
- Mandated by Phase III constitution
- Combines SQLAlchemy and Pydantic
- Type hints for better IDE support
- Automatic validation
- Works well with FastAPI

### Best Practices

**Model Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    description: str | None = None
    completed: bool = False
    due_date: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Relationships**:
```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="tasks")
```

**Queries**:
```python
from sqlmodel import select

# Simple query
statement = select(Task).where(Task.user_id == user_id)
tasks = session.exec(statement).all()

# With filtering
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
).order_by(Task.due_date)
```

---

## 6. Better Auth (Authentication)

### Decision
Use Better Auth for authentication

### Rationale
- Mandated by Phase III constitution
- Modern auth solution
- Supports both backend and frontend
- Good developer experience
- Session management built-in

### Best Practices

**Backend Integration**:
```python
from better_auth import BetterAuth

auth = BetterAuth(
    secret=os.getenv("AUTH_SECRET"),
    database_url=os.getenv("DATABASE_URL")
)

# Middleware
async def auth_middleware(request: Request):
    token = request.headers.get("Authorization")
    user = await auth.verify_token(token)
    request.state.user = user
```

**Frontend Integration**:
```typescript
import { createAuthClient } from '@better-auth/react'

const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL
})

// In component
const { user, signIn, signOut } = useAuth()
```

**Protected Routes**:
```python
from fastapi import Depends

async def get_current_user(request: Request):
    if not request.state.user:
        raise HTTPException(401, "Unauthorized")
    return request.state.user

@app.post("/api/chat")
async def chat(user = Depends(get_current_user)):
    # User is authenticated
    pass
```

---

## 7. OpenAI ChatKit (Frontend)

### Decision
Use OpenAI ChatKit for conversational UI

### Rationale
- Mandated by Phase III constitution
- Pre-built chat interface
- Optimized for AI interactions
- Maintained by OpenAI
- Customizable message renderers

### Best Practices

**ChatKit Setup**:
```typescript
import { ChatKit } from '@openai/chatkit'

export default function ChatPage() {
  return (
    <ChatKit
      apiUrl="/api/chat"
      onMessage={handleMessage}
      messageRenderer={CustomMessageRenderer}
    />
  )
}
```

**Custom Message Renderer**:
```typescript
function CustomMessageRenderer({ message }) {
  if (message.type === 'task_created') {
    return <TaskCreatedFeedback task={message.data} />
  }
  return <DefaultRenderer message={message} />
}
```

**State Management**:
```typescript
const [conversationId, setConversationId] = useState(null)

const handleMessage = async (message) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      conversation_id: conversationId,
      message: message
    })
  })
  const data = await response.json()
  setConversationId(data.conversation_id)
}
```

---

## 8. Stateless Architecture Pattern

### Decision
Implement stateless server architecture

### Rationale
- Constitutional requirement
- Enables horizontal scaling
- Fault tolerance
- Simplified deployment

### Implementation Pattern

**Request Flow**:
```
1. Client sends message + conversation_id
2. Server fetches conversation history from DB
3. Server loads last N messages into context
4. Server calls AI agent with context
5. AI agent calls MCP tools
6. Tools persist changes to DB
7. Server persists new message to DB
8. Server returns response + conversation_id
```

**Conversation Service**:
```python
class ConversationService:
    async def get_history(self, conversation_id: str, limit: int = 20):
        # Fetch from database
        messages = await db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        return list(reversed(messages))

    async def add_message(self, conversation_id: str, role: str, content: str):
        # Persist to database
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        await db.add(message)
        await db.commit()
```

**No In-Memory State**:
```python
# ❌ WRONG - stores state in memory
conversations = {}  # Global state

# ✅ CORRECT - fetches from database
async def get_conversation(conversation_id: str):
    return await db.query(Conversation).get(conversation_id)
```

---

## 9. Natural Language Date Parsing

### Decision
Implement natural language date parser for task due dates

### Rationale
- Required for user story acceptance criteria
- Improves user experience
- Enables natural conversation

### Implementation Options

**Option 1: dateparser library**:
```python
import dateparser

def parse_date(text: str) -> datetime:
    return dateparser.parse(text, settings={
        'PREFER_DATES_FROM': 'future'
    })

# Examples:
# "tomorrow" -> 2026-01-23
# "next Friday" -> 2026-01-24
# "in 2 hours" -> 2026-01-22 15:00
```

**Option 2: OpenAI function calling**:
```python
# Let AI agent extract date
tools = [{
    "name": "add_task",
    "parameters": {
        "due_date": {
            "type": "string",
            "description": "ISO 8601 date (YYYY-MM-DD)"
        }
    }
}]

# AI converts "tomorrow" to "2026-01-23"
```

**Recommendation**: Use Option 2 (AI extraction) for consistency with overall architecture

---

## 10. Error Handling Strategy

### Decision
Implement multi-layer error handling

### Rationale
- Constitutional requirement for graceful errors
- Better user experience
- Easier debugging

### Implementation Layers

**Layer 1: Tool Level**:
```python
class AddTaskTool:
    async def execute(self, title: str):
        try:
            task = await task_service.create(title)
            return {"success": True, "task": task}
        except ValidationError as e:
            return {"success": False, "error": "invalid_input"}
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return {"success": False, "error": "tool_failure"}
```

**Layer 2: AI Agent Level**:
```python
def handle_tool_error(error_code: str) -> str:
    messages = {
        "invalid_input": "I couldn't understand that. Could you rephrase?",
        "tool_failure": "Something went wrong. Please try again.",
        "task_not_found": "I couldn't find that task. Could you be more specific?"
    }
    return messages.get(error_code, "An error occurred.")
```

**Layer 3: API Level**:
```python
@app.exception_handler(Exception)
async def global_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Something went wrong. Please try again."}
    )
```

---

## 11. Performance Optimization

### Decision
Implement caching and optimization strategies

### Rationale
- Meet <2s response time requirement
- Support 100+ concurrent conversations
- Efficient database queries

### Strategies

**Database Query Optimization**:
- Use indexes on frequently queried columns
- Limit conversation history to last 20 messages
- Use `select_related` for relationships
- Implement pagination for large result sets

**Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_preferences(user_id: int):
    # Cache user preferences
    pass
```

**Async Operations**:
```python
import asyncio

# Parallel operations
results = await asyncio.gather(
    fetch_conversation_history(conv_id),
    fetch_user_tasks(user_id),
    fetch_user_preferences(user_id)
)
```

**Connection Pooling**:
- Neon handles this automatically
- Configure reasonable pool sizes
- Use `pool_pre_ping` for health checks

---

## 12. Testing Strategy

### Decision
Implement comprehensive testing at multiple levels

### Rationale
- Ensure 90%+ intent accuracy
- Verify stateless architecture
- Catch regressions early

### Test Levels

**Unit Tests (pytest)**:
```python
def test_add_task_tool():
    tool = AddTaskTool()
    result = await tool.execute(title="Test task")
    assert result["success"] == True
    assert "task_id" in result
```

**Integration Tests**:
```python
async def test_chat_endpoint():
    response = await client.post("/api/chat", json={
        "message": "Add buy milk to my list"
    })
    assert response.status_code == 200
    assert "task" in response.json()
```

**Contract Tests**:
```python
def test_chat_api_contract():
    # Verify API matches OpenAPI spec
    pass
```

**Accuracy Tests**:
```python
def test_intent_classification():
    test_cases = [
        ("Add buy milk", "create_task"),
        ("What's on my list?", "list_tasks"),
        ("Mark milk as done", "complete_task")
    ]
    for input, expected_intent in test_cases:
        intent = classify_intent(input)
        assert intent == expected_intent
```

---

## Summary

All technology choices are mandated by the Phase III constitution. This research document captures best practices and implementation patterns for each technology to ensure successful implementation.

**Key Takeaways**:
1. Stateless architecture is critical - fetch conversation from DB each request
2. MCP tools provide clean separation between AI and data layers
3. OpenAI Agents SDK handles all natural language understanding
4. Error handling at multiple layers ensures graceful degradation
5. Performance optimization through caching, indexing, and async operations

**Next Steps**:
- Generate data-model.md with database schema
- Generate contracts/ with API specifications
- Generate quickstart.md with local development guide
