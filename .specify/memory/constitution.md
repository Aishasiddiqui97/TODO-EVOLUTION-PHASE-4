<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles: None (existing principles preserved)
- Added sections: Phase III: AI-Powered Todo Chatbot (Purpose, Core Principles, Architectural Constraints, Behavioral Rules, Stateless Guarantee)
- Removed sections: None
- Templates requiring updates:
  ✅ constitution.md - updated
  ⚠ plan-template.md - review for Phase III architectural constraints
  ⚠ tasks-template.md - review for MCP tooling and stateless requirements
- Follow-up TODOs: None
- Rationale: MINOR version bump - added new phase-specific section with architectural constraints and principles without breaking existing governance
-->

# Todo Evolution App Constitution

**Version**: 1.1.0
**Ratified**: 2025-12-31
**Last Amended**: 2026-01-22

## Core Principles

### 1. User-Centric Design
The application must prioritize user experience, clarity, and accessibility. Every feature should deliver clear value to users and be intuitive to use.

### 2. Reliability & Security
All data handling must be secure, validated, and reliable. User data must be protected, and authentication must be enforced for all operations.

### 3. Maintainable Code
Code should be clean, modular, and well-documented. Follow established patterns and conventions to ensure long-term maintainability.

### 4. AI-Assisted Development
AI tools are used to accelerate development while keeping human oversight. All AI-generated code must be reviewed and validated.

### 5. Iterative Delivery
Features are delivered in small, testable increments. Each phase builds upon the previous phase with clear boundaries and deliverables.

---

## Phase III: AI-Powered Todo Chatbot

### Purpose
Phase III introduces an AI-powered Todo Chatbot that enables users to manage tasks through natural language conversation using the Model Context Protocol (MCP).

### Core Principles

#### Stateless Server Architecture
- The server MUST be stateless - no session or conversation state stored in memory
- Every request MUST be independent and self-contained
- Conversation history MUST be fetched from the database for each request

**Rationale**: Stateless architecture ensures scalability, reliability, and simplifies deployment across multiple instances.

#### AI Logic Separation
- AI logic MUST be handled exclusively through OpenAI Agents SDK
- The AI agent MUST NOT directly access the database
- All database operations MUST go through MCP tools

**Rationale**: Clear separation of concerns ensures the AI layer remains focused on natural language understanding while data operations are handled by specialized, testable tools.

#### MCP Tool-Based Operations
- All task operations (create, read, update, delete) MUST be performed through MCP tools
- MCP tools MUST be stateless functions
- Each MCP tool MUST persist state changes to the database immediately

**Rationale**: MCP provides a standardized protocol for tool execution, enabling better observability, testing, and integration with AI agents.

#### Conversation State Persistence
- Conversation state MUST be persisted in the database
- Conversation history MUST be maintained across sessions
- Users MUST be able to reference previous context (e.g., "that task")

**Rationale**: Persistent conversation state enables natural, context-aware interactions while maintaining the stateless server principle.

### Architectural Constraints

The following technology choices are mandated for Phase III:

- **Backend Framework**: FastAPI (Python)
- **AI Framework**: OpenAI Agents SDK
- **MCP Server**: Official MCP SDK
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: Better Auth
- **Frontend**: OpenAI ChatKit

**Rationale**: These technologies are chosen for their maturity, integration capabilities, and alignment with the stateless, MCP-based architecture.

### Behavioral Rules

#### User Confirmations
- Every task operation (create, update, delete) MUST provide a friendly confirmation message
- Confirmations MUST clearly state what action was taken
- Confirmations MUST be conversational, not robotic

**Rationale**: Clear confirmations build user trust and provide feedback that the system understood their intent correctly.

#### Error Handling
- Errors MUST be handled gracefully without exposing technical details
- Error messages MUST be clear, actionable, and user-friendly
- Common errors (task not found, invalid input) MUST have specific, helpful messages

**Rationale**: Graceful error handling improves user experience and reduces support burden.

### Stateless Guarantee

The following rules ensure the server remains stateless:

1. **No In-Memory State**: Server memory MUST NOT store any user session, conversation state, or task data
2. **Database as Source of Truth**: All state MUST be persisted to and retrieved from the database
3. **Independent Requests**: Each API request MUST be processable without relying on previous requests in memory
4. **Conversation History Retrieval**: Conversation context MUST be loaded from the database for each request

**Rationale**: Stateless servers are horizontally scalable, fault-tolerant, and simplify deployment and maintenance.

---

## Governance

### Amendment Procedure
1. Propose changes via pull request with rationale
2. Review by project maintainers
3. Update version according to semantic versioning
4. Update dependent templates and documentation
5. Create Architecture Decision Record (ADR) for significant changes

### Versioning Policy
- **MAJOR**: Backward incompatible governance or principle removals/redefinitions
- **MINOR**: New principles, sections, or material expansions
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review
- All specifications MUST align with constitution principles
- All implementation plans MUST respect architectural constraints
- All code reviews MUST verify adherence to behavioral rules
