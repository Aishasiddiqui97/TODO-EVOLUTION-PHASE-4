# Implementation Plan: AI-Powered Todo Chatbot (Phase III)

**Branch**: `003-ai-chatbot-mcp` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot-mcp/spec.md`

## Summary

Phase III introduces an AI-powered Todo Chatbot that enables users to manage tasks through natural language conversation. The system uses the Model Context Protocol (MCP) to provide a stateless, scalable architecture where AI agents interact with task data through standardized tools. Users can create, view, update, and delete tasks by simply chatting with the bot, which interprets natural language and executes appropriate operations.

**Technical Approach**: Stateless FastAPI backend with OpenAI Agents SDK for natural language understanding, MCP tools for all database operations, Neon Serverless PostgreSQL for persistence, and OpenAI ChatKit frontend for the conversational interface.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.0+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.115+, OpenAI Agents SDK, MCP SDK (official), SQLModel 0.0.22+, Better Auth
- Frontend: Next.js 16+, OpenAI ChatKit, React 19+

**Storage**: Neon Serverless PostgreSQL (cloud-hosted, serverless)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (separate backend and frontend)

**Performance Goals**:
- Chat response time: <2 seconds for 95% of requests
- Support 100+ concurrent conversations
- Database queries: <500ms completion time

**Constraints**:
- Server MUST be stateless (no in-memory session/conversation state)
- AI agent MUST NOT directly access database (only through MCP tools)
- All task operations MUST go through MCP tools
- Conversation history MUST be fetched from database each request

**Scale/Scope**:
- Support 1000+ users
- Handle 100+ concurrent conversations
- Maintain conversation history (30+ days retention)
- 5 MCP tools (add, list, complete, update, delete tasks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Constitutional Requirements

✅ **Stateless Server Architecture**
- Server will not store session/conversation state in memory
- Each request fetches conversation history from database
- Implementation: Conversation service loads history per request

✅ **AI Logic Separation**
- OpenAI Agents SDK handles all natural language understanding
- AI agent never directly accesses database
- Implementation: Agent only calls MCP tools, tools handle database

✅ **MCP Tool-Based Operations**
- All CRUD operations through MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- Tools are stateless functions
- Implementation: Each tool persists changes immediately to database

✅ **Conversation State Persistence**
- Conversation and message models in database
- History maintained across sessions
- Implementation: ConversationService and MessageService handle persistence

✅ **User Confirmations**
- Every operation returns friendly confirmation
- Implementation: AI response formatter creates conversational confirmations

✅ **Error Handling**
- Graceful error handling without technical details
- Implementation: Error handler middleware + AI-friendly error messages

**GATE STATUS**: ✅ PASS - All constitutional requirements can be met with proposed architecture

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-mcp/
├── plan.md              # This file
├── research.md          # Technology decisions and best practices
├── data-model.md        # Database schema and entities
├── quickstart.md        # Local development and testing guide
├── contracts/           # API contracts (OpenAPI specs)
│   └── chat-api.yaml
├── spec.md              # Feature specification (already exists)
├── tasks.md             # Implementation tasks (already exists)
└── checklists/
    └── requirements.md  # Quality checklist (already exists)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # FastAPI application entry
│   ├── db.py                      # Neon PostgreSQL connection
│   ├── config.py                  # Environment configuration
│   │
│   ├── models/                    # SQLModel entities
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── conversation.py
│   │   └── message.py
│   │
│   ├── api/                       # FastAPI routes
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Better Auth integration
│   │   │   └── chat.py           # Stateless chat endpoint
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── rate_limiter.py
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── task_service.py       # Task CRUD operations
│   │   ├── conversation_service.py
│   │   ├── message_service.py
│   │   ├── task_filter.py
│   │   └── task_matcher.py
│   │
│   ├── mcp/                       # MCP server and tools
│   │   ├── __init__.py
│   │   ├── server.py             # MCP server setup
│   │   ├── registry.py           # Tool registry
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── add_task.py
│   │   │   ├── list_tasks.py
│   │   │   ├── complete_task.py
│   │   │   ├── update_task.py
│   │   │   └── delete_task.py
│   │
│   ├── ai/                        # OpenAI Agents SDK integration
│   │   ├── __init__.py
│   │   ├── agent.py              # Agent initialization
│   │   ├── intent_classifier.py  # Intent detection
│   │   ├── date_parser.py        # Natural language date parsing
│   │   ├── error_handler.py      # AI-friendly error handling
│   │   ├── intents/              # Intent handlers
│   │   │   ├── __init__.py
│   │   │   ├── create_task.py
│   │   │   ├── list_tasks.py
│   │   │   ├── complete_task.py
│   │   │   ├── update_task.py
│   │   │   ├── delete_task.py
│   │   │   └── search_tasks.py
│   │   ├── extractors/           # Data extraction from NL
│   │   │   ├── __init__.py
│   │   │   └── task_extractor.py
│   │   ├── formatters/           # Response formatting
│   │   │   ├── __init__.py
│   │   │   ├── task_list_formatter.py
│   │   │   └── search_results_formatter.py
│   │   └── responses/            # Response templates
│   │       ├── __init__.py
│   │       ├── confirmations.py
│   │       ├── update_confirmations.py
│   │       ├── delete_confirmations.py
│   │       ├── empty_list.py
│   │       └── no_results.py
│   │
│   ├── auth/                      # Better Auth integration
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── middleware.py
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── metrics.py
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                         # Backend tests
│   ├── unit/
│   ├── integration/
│   └── contract/
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md

frontend/
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Landing page
│   │   └── chat/
│   │       └── page.tsx          # Chat interface
│   │
│   ├── components/                # React components
│   │   ├── ChatKit.tsx           # OpenAI ChatKit wrapper
│   │   ├── MessageRenderer.tsx
│   │   ├── TaskCreationFeedback.tsx
│   │   ├── TaskListDisplay.tsx
│   │   ├── TaskUpdateFeedback.tsx
│   │   ├── TaskDeletionFeedback.tsx
│   │   ├── SearchResultsDisplay.tsx
│   │   ├── ConversationResume.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── MessageRetry.tsx
│   │   └── TypingIndicator.tsx
│   │
│   ├── lib/                       # Utilities
│   │   ├── api.ts                # API client
│   │   ├── auth.ts               # Better Auth integration
│   │   └── types.ts              # TypeScript types
│   │
│   └── styles/
│       └── globals.css
│
├── tests/                         # Frontend tests
├── package.json
├── tsconfig.json
├── next.config.js
└── .env.local.example

docs/
├── api.md                         # API documentation
├── deployment.md                  # Deployment guide
├── mcp-tools.md                   # MCP tools documentation
└── user-guide.md                  # User guide for chatbot
```

**Structure Decision**: Web application structure with separate backend (FastAPI/Python) and frontend (Next.js/TypeScript). Backend follows layered architecture: API → Services → MCP Tools → Database. AI layer (OpenAI Agents SDK) sits alongside and calls MCP tools. Frontend uses OpenAI ChatKit for conversational UI.

## Complexity Tracking

No constitutional violations. All requirements align with Phase III principles.

## Execution Roadmap

### Phase 1: Foundation
**Goal**: Set up project structure, environment, and database schema

**Tasks**:
- Initialize backend FastAPI project with dependencies
- Initialize frontend Next.js project with ChatKit
- Configure Neon Serverless PostgreSQL connection
- Set up SQLModel base models
- Initialize Alembic for migrations
- Create initial database schema migration
- Configure Better Auth for both backend and frontend
- Set up environment configuration management

**Deliverables**:
- Working project structure
- Database connection established
- Authentication configured
- Environment variables documented

**Checkpoint**: Can run both backend and frontend locally, database accessible

---

### Phase 2: MCP Layer
**Goal**: Implement MCP server and all task operation tools

**Tasks**:
- Set up MCP SDK and server
- Create MCP tool base class
- Implement add_task tool (create tasks)
- Implement list_tasks tool (retrieve tasks with filtering)
- Implement complete_task tool (mark tasks complete)
- Implement update_task tool (modify task details)
- Implement delete_task tool (remove tasks)
- Create tool registry
- Add tool call logging

**Deliverables**:
- 5 working MCP tools
- Tool registry with all tools registered
- Tool call logging infrastructure

**Checkpoint**: Can call MCP tools directly and verify database operations

---

### Phase 3: AI Agent
**Goal**: Integrate OpenAI Agents SDK and implement natural language understanding

**Tasks**:
- Set up OpenAI Agents SDK
- Create agent initialization and configuration
- Implement intent classification system
- Implement natural language date parser
- Create intent handlers for each operation (create, list, update, complete, delete, search)
- Implement task detail extraction from natural language
- Create response formatters for conversational output
- Implement clarification question logic for ambiguous requests
- Create error handler for AI-friendly error messages
- Bind MCP tools to agent

**Deliverables**:
- Working AI agent that understands natural language
- Intent classification with 90%+ accuracy
- Date parsing from natural language
- Conversational response generation
- Tool bindings configured

**Checkpoint**: Can send natural language to agent and get appropriate tool calls

---

### Phase 4: Chat API
**Goal**: Create stateless chat endpoint with conversation management

**Tasks**:
- Implement stateless chat endpoint (POST /api/{user_id}/chat)
- Create conversation persistence service
- Create message history handler
- Implement conversation lifecycle management
- Add conversation history retrieval (fetch from DB each request)
- Implement message persistence
- Add authentication middleware
- Add rate limiting
- Implement graceful error handling

**Deliverables**:
- Working chat API endpoint
- Conversation state persisted in database
- Message history maintained
- Stateless architecture verified

**Checkpoint**: Can send messages via API, conversation persists, history loads correctly

---

### Phase 5: Frontend
**Goal**: Build ChatKit UI and integrate with backend

**Tasks**:
- Set up OpenAI ChatKit component
- Integrate Better Auth in frontend
- Create API client for chat endpoint
- Implement message rendering
- Add task creation feedback UI
- Add task list display
- Add task update/delete feedback
- Implement conversation resume support
- Add loading states and error boundaries
- Add message retry functionality
- Add typing indicators
- Polish UX (animations, transitions, responsive design)

**Deliverables**:
- Working chat interface
- Authentication flow
- Message rendering with feedback
- Conversation resume
- Error handling and retry

**Checkpoint**: Can use chatbot through UI, all operations work end-to-end

---

### Phase 6: Testing & Validation
**Goal**: Validate system behavior and edge cases

**Tasks**:
- Test tool accuracy (verify correct tool called for each intent)
- Test conversation recovery (resume from previous session)
- Test error scenarios (task not found, invalid input, AI service down)
- Test ambiguous requests (clarification questions)
- Test concurrent conversations
- Test stateless architecture (verify no in-memory state)
- Performance testing (response time, concurrent users)
- Security testing (authentication, authorization, input validation)

**Deliverables**:
- Test results documenting accuracy and performance
- Edge cases handled gracefully
- Performance meets success criteria (<2s response time)

**Checkpoint**: All acceptance scenarios from spec.md pass

---

### Phase 7: Deployment
**Goal**: Deploy to production and validate

**Tasks**:
- Deploy backend to production environment
- Run database migrations on production database
- Configure production environment variables
- Deploy frontend to Vercel
- Set up monitoring and logging
- Configure rate limiting for production
- Create deployment documentation
- Final demo and user acceptance testing

**Deliverables**:
- Production deployment
- Monitoring configured
- Documentation complete
- Demo successful

**Checkpoint**: System running in production, users can access chatbot

---

## Key Design Decisions

### 1. Stateless Architecture
**Decision**: Server stores no session or conversation state in memory
**Rationale**: Enables horizontal scaling, fault tolerance, and simplified deployment
**Implementation**: Conversation service fetches history from database on each request

### 2. MCP Tool-Based Operations
**Decision**: All database operations go through MCP tools, AI agent never accesses DB directly
**Rationale**: Clear separation of concerns, better testability, standardized tool protocol
**Implementation**: 5 MCP tools (add, list, complete, update, delete) handle all task operations

### 3. OpenAI Agents SDK for NLP
**Decision**: Use OpenAI Agents SDK for natural language understanding
**Rationale**: Mature framework with tool calling support, high accuracy, maintained by OpenAI
**Implementation**: Agent classifies intent, extracts details, calls appropriate MCP tool

### 4. Neon Serverless PostgreSQL
**Decision**: Use Neon for database instead of self-hosted PostgreSQL
**Rationale**: Serverless scaling, automatic backups, connection pooling, cost-effective
**Implementation**: SQLModel ORM with Neon connection string

### 5. Better Auth
**Decision**: Use Better Auth for authentication
**Rationale**: Modern auth solution with good DX, supports both backend and frontend
**Implementation**: Middleware in backend, auth hooks in frontend

### 6. OpenAI ChatKit for Frontend
**Decision**: Use OpenAI ChatKit instead of custom chat UI
**Rationale**: Pre-built conversational UI, optimized for AI interactions, maintained by OpenAI
**Implementation**: ChatKit component with custom message renderers

---

## Risk Mitigation

### Risk 1: OpenAI API Latency
**Impact**: Response time >2s violates success criteria
**Mitigation**:
- Implement timeout handling
- Add graceful degradation (fallback responses)
- Cache common responses
- Monitor p95 latency

### Risk 2: Conversation History Growth
**Impact**: Large conversation histories slow down requests
**Mitigation**:
- Implement pagination for history retrieval
- Limit context window (e.g., last 20 messages)
- Archive old conversations
- Add database indexing

### Risk 3: Intent Classification Accuracy
**Impact**: <90% accuracy violates success criteria
**Mitigation**:
- Comprehensive prompt engineering
- Few-shot examples in prompts
- Fallback to clarification questions
- Continuous monitoring and improvement

### Risk 4: MCP Tool Failures
**Impact**: Operations fail, poor user experience
**Mitigation**:
- Comprehensive error handling in tools
- Retry logic for transient failures
- Clear error messages to AI agent
- Tool call logging for debugging

---

## Success Metrics

From spec.md success criteria:

- **SC-001**: Task creation <10 seconds ✓ (measured end-to-end)
- **SC-002**: Intent accuracy 90%+ ✓ (measured via test suite)
- **SC-003**: Detail extraction 85%+ ✓ (measured via test suite)
- **SC-004**: Complete flow without forms ✓ (verified in testing)
- **SC-005**: Response time <2s ✓ (measured p95 latency)
- **SC-006**: 95% operation success ✓ (measured via metrics)
- **SC-007**: 100+ concurrent conversations ✓ (load testing)
- **SC-008**: Context maintained across sessions ✓ (verified in testing)
- **SC-009**: 90% self-recovery from errors ✓ (user testing)
- **SC-010**: 50% faster than forms ✓ (comparative testing)

---

## Next Steps

1. **Phase 0**: Generate research.md with technology best practices
2. **Phase 1**: Generate data-model.md, contracts/, and quickstart.md
3. **Phase 2**: Begin implementation following tasks.md
4. **Continuous**: Update plan as learnings emerge

---

**Plan Status**: ✅ Complete - Ready for Phase 0 research
