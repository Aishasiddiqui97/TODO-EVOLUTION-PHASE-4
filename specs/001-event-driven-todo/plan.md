# Implementation Plan: Event-Driven Todo Chatbot with Advanced Features

**Branch**: `001-event-driven-todo` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-event-driven-todo/spec.md`

**Note**: This plan follows Phase V constitution requirements for event-driven architecture with Dapr on Kubernetes.

## Summary

Implement production-grade Todo Chatbot with advanced features (recurring tasks, notifications, tags, search, real-time sync) using event-driven microservices architecture. Five independent services communicate asynchronously via Dapr PubSub over Kafka-compatible broker. All services use Dapr building blocks for infrastructure abstraction (state, secrets, jobs, service invocation). System runs identically on Minikube (local) and cloud Kubernetes (AKS/GKE/OKE) with zero code changes.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI 0.109+, Dapr SDK for Python 1.12+, SQLModel 0.0.14+, OpenAI Agents SDK, Pydantic 2.5+
**Storage**: PostgreSQL 15+ (accessed via Dapr State API), Kafka-compatible broker (Redpanda/Confluent/Strimzi) for events
**Testing**: pytest 7.4+, pytest-asyncio for async tests, testcontainers for integration tests
**Target Platform**: Kubernetes 1.28+ (Minikube for local, AKS/GKE/OKE for cloud)
**Project Type**: Microservices (5 services: Chat API, Recurring Task Service, Notification Service, Audit Log Service, WebSocket Sync Service)
**Performance Goals**:
- Event publishing: <100ms per operation
- Event processing latency: <500ms p95
- Real-time sync: <1s update propagation
- Search queries: <500ms for 10k tasks
- Support 1000 concurrent users
**Constraints**:
- No direct Kafka SDK usage (Dapr PubSub only)
- No direct database SDK usage (Dapr State API only)
- Same code runs on Minikube and cloud without modifications
- All secrets via Dapr Secrets API
- Observability via Dapr (logs, metrics, traces)
**Scale/Scope**:
- 1000 concurrent users
- 50,000 tasks per user
- 5 microservices
- 3 Kafka topics (task-events, reminders, task-updates)
- Support for local (Minikube) and cloud (AKS/GKE/OKE) deployments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase V Requirements

#### ✅ Spec-Driven Development (SDD) Only
- Specification created and approved: `specs/001-event-driven-todo/spec.md`
- Following Spec → Plan → Tasks → Implement lifecycle
- All requirements documented before implementation

#### ✅ Agentic Execution
- All code will be written by Claude Code via Spec-KitPlus MCP
- Human role: specification author, reviewer, validator, auditor
- PHRs will be created for all AI interactions

#### ✅ Event-Driven Architecture
- All inter-service communication via asynchronous events
- No direct synchronous service-to-service calls (except via Dapr Service Invocation when necessary)
- Events published to Dapr PubSub components
- Event schemas will be versioned and documented

#### ✅ Infrastructure Abstraction
- No direct Kafka SDK usage - Dapr PubSub only
- No direct PostgreSQL SDK usage - Dapr State API only
- State management via Dapr State API
- Secrets via Dapr Secrets API
- Service invocation via Dapr Service Invocation

#### ✅ Environment Parity
- Same application code runs on Minikube and cloud Kubernetes
- Dapr components configurable per environment
- Infrastructure differences handled through Dapr component YAML only

#### ✅ Observability First
- Structured logging enabled by default
- Metrics exposed via Dapr metrics endpoint
- Distributed tracing via Dapr
- No code changes required for observability configuration

### Phase III Compatibility

#### ✅ Stateless Server Architecture
- Chat API service remains stateless
- Conversation history fetched from Dapr State API per request
- No in-memory session state

#### ✅ AI Logic Separation
- AI logic handled through OpenAI Agents SDK
- AI agent does not directly access state
- All state operations through MCP tools that use Dapr State API

#### ✅ MCP Tool-Based Operations
- Task operations performed through MCP tools
- MCP tools use Dapr State API for persistence
- Each tool publishes events via Dapr PubSub after state changes

### Quality Gates

- ✅ Every commit will reference Task ID
- ✅ Every service will have Dapr sidecar configured
- ✅ Every feature maps to acceptance criteria in spec.md
- ✅ Every service emits logs, metrics, traces via Dapr
- ✅ Every published event has documented schema

**Gate Status**: ✅ PASSED - All Phase V constitution requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-event-driven-todo/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── events/          # Event schemas
│   ├── api/             # REST API contracts
│   └── dapr/            # Dapr component configurations
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── services/
│   │   ├── chat-api/           # Chat API service (MCP-enabled)
│   │   ├── recurring-task/     # Recurring Task Service
│   │   ├── notification/       # Notification Service
│   │   ├── audit-log/          # Audit Log Service
│   │   └── websocket-sync/     # WebSocket Sync Service
│   ├── shared/
│   │   ├── models/             # Shared data models
│   │   ├── events/             # Event schemas and publishers
│   │   ├── dapr_client/        # Dapr SDK wrappers
│   │   └── utils/              # Shared utilities
│   └── mcp/
│       └── tools/              # MCP tools for Chat API
└── tests/
    ├── contract/               # Contract tests for events and APIs
    ├── integration/            # Integration tests with Dapr
    └── unit/                   # Unit tests

frontend/
├── src/
│   ├── components/
│   │   └── ChatKit.tsx         # Existing chat interface (Phase III)
│   ├── pages/
│   └── services/
│       └── websocket.ts        # WebSocket client for real-time sync
└── tests/

k8s/
├── base/                       # Base Kubernetes manifests
│   ├── chat-api/
│   ├── recurring-task/
│   ├── notification/
│   ├── audit-log/
│   └── websocket-sync/
├── dapr/                       # Dapr component configurations
│   ├── pubsub.yaml             # Kafka PubSub component
│   ├── statestore.yaml         # PostgreSQL State Store component
│   ├── secretstore.yaml        # Secrets component
│   └── subscriptions/          # Event subscriptions per service
├── local/                      # Minikube-specific overlays
│   └── kustomization.yaml
└── cloud/                      # Cloud-specific overlays (AKS/GKE/OKE)
    └── kustomization.yaml

.github/
└── workflows/
    ├── ci.yml                  # CI pipeline
    └── cd.yml                  # CD pipeline (deploy to K8s)
```

**Structure Decision**: Microservices architecture with 5 independent services in `backend/src/services/`. Each service is a separate Python application with its own dependencies and Dockerfile. Shared code (models, events, Dapr wrappers) in `backend/src/shared/`. Kubernetes manifests organized by service with Dapr component configurations separate. Frontend remains in existing `frontend/` directory from Phase III. This structure supports independent service deployment and clear separation of concerns.

## Complexity Tracking

> No constitution violations - all requirements satisfied by design.

