---
id: 003
title: amend-constitution-phase-iii-chatbot
stage: constitution
date: 2026-01-22
surface: agent
model: claude-sonnet-4-5
feature: 003-ai-chatbot-mcp
branch: 003-ai-chatbot-mcp
user: Aishasiddiqui97
command: /sp.constitution
labels: ["constitution", "phase-3", "ai-chatbot", "mcp", "stateless-architecture"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Constitution version validation (1.0.0 → 1.1.0)
---

## Prompt

# SP Constitution – Todo AI Chatbot (Phase III)

## 1. Purpose
Is phase ka goal ek AI-powered Todo Chatbot banana hai jo natural language
ke zariye tasks manage kare using MCP (Model Context Protocol).

## 2. Core Principles
- Server MUST be stateless
- AI logic OpenAI Agents SDK se handle hogi
- Task operations sirf MCP tools ke through hongi
- Conversation state database mein persist hogi
- AI kabhi directly database access nahi karega

## 3. Architectural Constraints
- Backend: FastAPI (Python)
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Auth: Better Auth
- Frontend: OpenAI ChatKit

## 4. Behavioral Rules
- User ke har action par friendly confirmation zaroori hai
- Errors gracefully handle hongi
- Task not found ya invalid input ka clear message diya jayega

## 5. Stateless Guarantee
- Har request independent hogi
- Conversation history database se fetch hogi
- Server memory mein koi session/state store nahi hoga

## Response snapshot

Updated project constitution to version 1.1.0 with Phase III AI-Powered Todo Chatbot principles and architectural constraints.

**Version Change**: 1.0.0 → 1.1.0 (MINOR bump)

**Rationale**: Added new phase-specific section without breaking existing governance. This is a material expansion that introduces new architectural principles and constraints for Phase III.

**Changes Made**:
- Added "Phase III: AI-Powered Todo Chatbot" section with:
  - Purpose statement
  - 4 Core Principles (Stateless Server, AI Logic Separation, MCP Tool-Based Operations, Conversation State Persistence)
  - Architectural Constraints (technology stack mandates)
  - Behavioral Rules (User Confirmations, Error Handling)
  - Stateless Guarantee (4 specific rules)
- Preserved all existing 5 core principles
- Added Governance section with amendment procedure, versioning policy, and compliance review

**Key Principles Documented**:
1. **Stateless Server Architecture**: No in-memory state, database as source of truth
2. **AI Logic Separation**: OpenAI Agents SDK handles AI, MCP tools handle data
3. **MCP Tool-Based Operations**: All CRUD operations through stateless MCP tools
4. **Conversation State Persistence**: History maintained in database across sessions

**Templates Requiring Review**:
- ⚠ plan-template.md - review for Phase III architectural constraints
- ⚠ tasks-template.md - review for MCP tooling and stateless requirements

## Outcome

- ✅ Impact: Constitution updated with Phase III governance, establishing clear architectural principles for AI chatbot development
- 🧪 Tests: Version validation passed (semantic versioning rules followed)
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: `/sp.plan` to create implementation plan following constitutional constraints
- 🧠 Reflection: Constitution now provides clear governance for stateless, MCP-based AI chatbot architecture. All principles include rationale for better understanding and compliance.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Version bump validation - PASS (MINOR bump appropriate for new section)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Proceed to `/sp.plan` with constitutional constraints in place
