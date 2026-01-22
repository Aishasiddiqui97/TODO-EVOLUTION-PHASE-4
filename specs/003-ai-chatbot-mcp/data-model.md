# Data Model: AI-Powered Todo Chatbot (Phase III)

**Date**: 2026-01-22
**Feature**: 003-ai-chatbot-mcp
**Purpose**: Define database schema and entity relationships

## Overview

The Phase III data model extends Phase II with conversation and message entities to support stateless chat functionality. All entities use SQLModel for ORM mapping.

---

## Entity Relationship Diagram

```
User (from Phase II)
  ├── 1:N → Task (from Phase II)
  └── 1:N → Conversation (new)
                └── 1:N → Message (new)
```

---

## Entities

### 1. User (Existing from Phase II)

**Purpose**: Represents an authenticated user

**Fields**:
- `id`: Integer, Primary Key, Auto-increment
- `email`: String(255), Unique, Not Null
- `username`: String(100), Unique, Not Null
- `password_hash`: String(255), Not Null
- `created_at`: DateTime, Default: UTC now
- `updated_at`: DateTime, Default: UTC now, Auto-update

**Relationships**:
- Has many `Task` (1:N)
- Has many `Conversation` (1:N)

**Indexes**:
- Primary key on `id`
- Unique index on `email`
- Unique index on `username`

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    username: str = Field(max_length=100, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")
```

---

### 2. Task (Existing from Phase II, Extended)

**Purpose**: Represents a todo item

**Fields**:
- `id`: Integer, Primary Key, Auto-increment
- `user_id`: Integer, Foreign Key → User.id, Not Null
- `title`: String(500), Not Null
- `description`: Text, Nullable
- `completed`: Boolean, Default: False
- `priority`: String(20), Nullable (values: "low", "medium", "high")
- `due_date`: DateTime, Nullable
- `created_at`: DateTime, Default: UTC now
- `updated_at`: DateTime, Default: UTC now, Auto-update

**Relationships**:
- Belongs to `User` (N:1)

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for user's task queries)
- Index on `due_date` (for date-based filtering)
- Index on `completed` (for status filtering)
- Composite index on `(user_id, completed, due_date)` (for common queries)

**Validation Rules**:
- `title` must not be empty
- `priority` must be one of: "low", "medium", "high", or null
- `due_date` must be in the future (at creation time)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: str | None = None
    completed: bool = Field(default=False, index=True)
    priority: TaskPriority | None = None
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

---

### 3. Conversation (New for Phase III)

**Purpose**: Represents a chat session between user and AI chatbot

**Fields**:
- `id`: UUID, Primary Key
- `user_id`: Integer, Foreign Key → User.id, Not Null
- `title`: String(200), Nullable (auto-generated from first message)
- `created_at`: DateTime, Default: UTC now
- `updated_at`: DateTime, Default: UTC now, Auto-update
- `last_message_at`: DateTime, Nullable (timestamp of last message)

**Relationships**:
- Belongs to `User` (N:1)
- Has many `Message` (1:N)

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for user's conversation list)
- Index on `last_message_at` (for sorting by recency)
- Composite index on `(user_id, last_message_at)` (for user's recent conversations)

**Business Rules**:
- Conversation is created on first message
- `title` is auto-generated from first user message (first 50 chars)
- `last_message_at` is updated whenever a message is added
- Conversations are soft-deleted (archived) after 30 days of inactivity

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime | None = Field(default=None, index=True)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 4. Message (New for Phase III)

**Purpose**: Represents a single message in a conversation (user or assistant)

**Fields**:
- `id`: Integer, Primary Key, Auto-increment
- `conversation_id`: UUID, Foreign Key → Conversation.id, Not Null
- `role`: String(20), Not Null (values: "user", "assistant")
- `content`: Text, Not Null
- `tool_calls`: JSON, Nullable (stores MCP tool calls made by assistant)
- `created_at`: DateTime, Default: UTC now

**Relationships**:
- Belongs to `Conversation` (N:1)

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` (for conversation history retrieval)
- Index on `created_at` (for chronological ordering)
- Composite index on `(conversation_id, created_at)` (for efficient history queries)

**Business Rules**:
- `role` must be either "user" or "assistant"
- `content` must not be empty
- `tool_calls` is populated only for assistant messages that triggered tools
- Messages are immutable (never updated, only created)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

---

## Database Schema SQL

```sql
-- Users table (from Phase II)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Tasks table (from Phase II, extended)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high')),
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed_due ON tasks(user_id, completed, due_date);

-- Conversations table (new for Phase III)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at);
CREATE INDEX idx_conversations_user_last_message ON conversations(user_id, last_message_at);

-- Messages table (new for Phase III)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

---

## Data Access Patterns

### Pattern 1: Fetch Conversation History (Most Common)

**Query**:
```python
# Get last 20 messages for a conversation
messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(20)
).all()

# Reverse to chronological order
messages = list(reversed(messages))
```

**Performance**: O(log n) with index on `(conversation_id, created_at)`

---

### Pattern 2: List User's Tasks with Filtering

**Query**:
```python
# Get pending tasks due today
from datetime import date

today_start = datetime.combine(date.today(), datetime.min.time())
today_end = datetime.combine(date.today(), datetime.max.time())

tasks = await session.exec(
    select(Task)
    .where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date >= today_start,
        Task.due_date <= today_end
    )
    .order_by(Task.due_date)
).all()
```

**Performance**: O(log n) with composite index on `(user_id, completed, due_date)`

---

### Pattern 3: Create Task from Chat

**Query**:
```python
# Create task and return with ID
task = Task(
    user_id=user_id,
    title=title,
    description=description,
    due_date=due_date,
    priority=priority
)
session.add(task)
await session.commit()
await session.refresh(task)
return task
```

**Performance**: O(1) insert

---

### Pattern 4: Resume Conversation

**Query**:
```python
# Get user's recent conversations
conversations = await session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.last_message_at.desc())
    .limit(10)
).all()
```

**Performance**: O(log n) with index on `(user_id, last_message_at)`

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# alembic/versions/001_add_conversation_tables.py

def upgrade():
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_last_message', 'conversations', ['last_message_at'])

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Data Retention Policy

### Conversations
- Active conversations: Retained indefinitely
- Inactive conversations (no messages for 30+ days): Archived
- Archived conversations: Retained for 90 days, then deleted

### Messages
- Messages in active conversations: Retained indefinitely
- Messages in archived conversations: Deleted with conversation

### Tasks
- Completed tasks: Retained for 1 year
- Deleted tasks: Soft delete with 30-day recovery period

---

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| User | email | Valid email format, unique |
| User | username | 3-100 chars, alphanumeric + underscore, unique |
| Task | title | 1-500 chars, not empty |
| Task | priority | One of: low, medium, high, or null |
| Task | due_date | Future date (at creation) |
| Conversation | id | Valid UUID v4 |
| Message | role | One of: user, assistant |
| Message | content | Not empty |

---

## Performance Considerations

### Indexing Strategy
- All foreign keys are indexed
- Frequently queried fields have indexes
- Composite indexes for common query patterns
- Avoid over-indexing (impacts write performance)

### Query Optimization
- Limit conversation history to last 20 messages
- Use pagination for large task lists
- Eager load relationships when needed
- Use database-level filtering instead of application-level

### Scaling Considerations
- Neon Serverless PostgreSQL handles connection pooling
- Read replicas for heavy read workloads (future)
- Partition messages table by date (if >10M messages)
- Archive old conversations to separate table (if needed)

---

## Next Steps

1. Create Alembic migration for conversation tables
2. Implement SQLModel models in `backend/src/models/`
3. Create database seeding script for development
4. Write unit tests for model validation
5. Document API contracts in `contracts/chat-api.yaml`
