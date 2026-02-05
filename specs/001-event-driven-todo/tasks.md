# Tasks: Event-Driven Todo Chatbot with Advanced Features

**Input**: Design documents from `/specs/001-event-driven-todo/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Microservices**: `backend/src/services/{service-name}/`
- **Shared code**: `backend/src/shared/`
- **Frontend**: `frontend/src/`
- **Kubernetes**: `k8s/`
- **Dapr configs**: `k8s/dapr/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create microservices directory structure in backend/src/services/ (chat-api, recurring-task, notification, audit-log, websocket-sync)
- [x] T002 Create shared code directory structure in backend/src/shared/ (models, events, dapr_client, utils)
- [x] T003 [P] Create MCP tools directory in backend/src/mcp/tools/
- [x] T004 [P] Create Kubernetes manifests directory structure in k8s/ (base, dapr, local, cloud)
- [x] T005 [P] Initialize Python project for Chat API service with requirements.txt in backend/src/services/chat-api/
- [x] T006 [P] Initialize Python project for Recurring Task service with requirements.txt in backend/src/services/recurring-task/
- [x] T007 [P] Initialize Python project for Notification service with requirements.txt in backend/src/services/notification/
- [x] T008 [P] Initialize Python project for Audit Log service with requirements.txt in backend/src/services/audit-log/
- [x] T009 [P] Initialize Python project for WebSocket Sync service with requirements.txt in backend/src/services/websocket-sync/
- [x] T010 [P] Create shared models package in backend/src/shared/models/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create Dapr PubSub component configuration for local in k8s/dapr/pubsub-local.yaml
- [ ] T012 [P] Create Dapr State Store component configuration for local in k8s/dapr/statestore-local.yaml
- [ ] T013 [P] Create Dapr Secrets component configuration for local in k8s/dapr/secretstore-local.yaml
- [ ] T014 [P] Create Kubernetes secrets for local environment in k8s/dapr/local-secrets.yaml
- [ ] T015 [P] Create Dapr Jobs component configuration in k8s/dapr/jobs-config.yaml
- [ ] T016 [P] Create Dapr resiliency configuration in k8s/dapr/resiliency.yaml
- [ ] T017 [P] Create Dapr tracing configuration in k8s/dapr/tracing.yaml
- [ ] T018 Implement Dapr client wrapper in backend/src/shared/dapr_client/client.py
- [ ] T019 [P] Implement event publisher utility in backend/src/shared/events/publisher.py
- [ ] T020 [P] Implement event schemas in backend/src/shared/events/schemas.py
- [ ] T021 [P] Create base Task model in backend/src/shared/models/task.py
- [ ] T022 [P] Create RecurrencePattern model in backend/src/shared/models/recurrence.py
- [ ] T023 [P] Create Notification model in backend/src/shared/models/notification.py
- [ ] T024 [P] Create TaskEvent model in backend/src/shared/models/task_event.py
- [ ] T025 [P] Create UserPreferences model in backend/src/shared/models/preferences.py
- [ ] T026 [P] Create Conversation model in backend/src/shared/models/conversation.py
- [ ] T027 Implement state key generator utility in backend/src/shared/utils/state_keys.py
- [ ] T028 [P] Implement idempotency checker utility in backend/src/shared/utils/idempotency.py
- [ ] T029 [P] Implement structured logging utility in backend/src/shared/utils/logging.py
- [ ] T030 Deploy PostgreSQL to Kubernetes in k8s/local/postgres.yaml
- [ ] T031 [P] Deploy Redpanda (Kafka) to Kubernetes in k8s/local/redpanda.yaml
- [ ] T032 [P] Deploy MailHog (email testing) to Kubernetes in k8s/local/mailhog.yaml
- [ ] T033 Create Dapr event subscription for Chat API in k8s/dapr/subscription-chat-api.yaml
- [ ] T034 [P] Create Dapr event subscription for Recurring Task service in k8s/dapr/subscription-recurring-task.yaml
- [ ] T035 [P] Create Dapr event subscription for Notification service in k8s/dapr/subscription-notification.yaml
- [ ] T036 [P] Create Dapr event subscription for Audit Log service in k8s/dapr/subscription-audit-log.yaml
- [ ] T037 [P] Create Dapr event subscription for WebSocket Sync service in k8s/dapr/subscription-websocket-sync.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task Management with Priorities and Due Dates (Priority: P1) 🎯 MVP

**Goal**: Users can create, update, and manage tasks through natural language conversation with priorities and due dates

**Independent Test**: Create task via chat with "Create a high-priority task to review proposal by Friday", verify task created with correct attributes, confirm updates work

### Implementation for User Story 1

- [ ] T038 [P] [US1] Implement create_task MCP tool in backend/src/mcp/tools/create_task.py
- [ ] T039 [P] [US1] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py
- [ ] T040 [P] [US1] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py
- [ ] T041 [P] [US1] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py
- [ ] T042 [P] [US1] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py
- [ ] T043 [US1] Implement Chat API main application in backend/src/services/chat-api/main.py
- [ ] T044 [US1] Implement chat message endpoint in backend/src/services/chat-api/routes/chat.py
- [ ] T045 [US1] Implement tasks list endpoint in backend/src/services/chat-api/routes/tasks.py
- [ ] T046 [US1] Implement task detail endpoint in backend/src/services/chat-api/routes/tasks.py
- [ ] T047 [US1] Implement OpenAI Agents SDK integration in backend/src/services/chat-api/ai/agent.py
- [ ] T048 [US1] Implement MCP server integration in backend/src/services/chat-api/mcp/server.py
- [ ] T049 [US1] Implement conversation state management in backend/src/services/chat-api/services/conversation_service.py
- [ ] T050 [US1] Implement task state management in backend/src/services/chat-api/services/task_service.py
- [ ] T051 [US1] Implement event publishing after task operations in backend/src/services/chat-api/services/task_service.py
- [ ] T052 [US1] Create Dockerfile for Chat API service in backend/src/services/chat-api/Dockerfile
- [ ] T053 [US1] Create Kubernetes deployment for Chat API in k8s/base/chat-api/deployment.yaml
- [ ] T054 [US1] Create Kubernetes service for Chat API in k8s/base/chat-api/service.yaml
- [ ] T055 [US1] Implement health check endpoint in backend/src/services/chat-api/routes/health.py
- [ ] T056 [US1] Implement user preferences endpoint GET in backend/src/services/chat-api/routes/preferences.py
- [ ] T057 [US1] Implement user preferences endpoint PUT in backend/src/services/chat-api/routes/preferences.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Recurring Tasks (Priority: P2)

**Goal**: Users can create tasks that automatically repeat on a schedule (daily, weekly, custom)

**Independent Test**: Create recurring task with "Remind me to review emails every weekday at 9am", verify task appears, confirm next instance auto-created after completion

### Implementation for User Story 2

- [ ] T058 [P] [US2] Implement recurrence pattern parser in backend/src/shared/utils/recurrence_parser.py
- [ ] T059 [P] [US2] Implement next occurrence calculator in backend/src/shared/utils/recurrence_calculator.py
- [ ] T060 [US2] Extend create_task MCP tool to support recurrence patterns in backend/src/mcp/tools/create_task.py
- [ ] T061 [US2] Extend update_task MCP tool to support recurrence pattern updates in backend/src/mcp/tools/update_task.py
- [ ] T062 [US2] Implement Recurring Task service main application in backend/src/services/recurring-task/main.py
- [ ] T063 [US2] Implement task.completed event handler in backend/src/services/recurring-task/handlers/task_completed.py
- [ ] T064 [US2] Implement next instance creation logic in backend/src/services/recurring-task/services/recurrence_service.py
- [ ] T065 [US2] Implement Dapr Jobs API integration for scheduling in backend/src/services/recurring-task/services/scheduler_service.py
- [ ] T066 [US2] Create Dockerfile for Recurring Task service in backend/src/services/recurring-task/Dockerfile
- [ ] T067 [US2] Create Kubernetes deployment for Recurring Task service in k8s/base/recurring-task/deployment.yaml
- [ ] T068 [US2] Create Kubernetes service for Recurring Task service in k8s/base/recurring-task/service.yaml
- [ ] T069 [US2] Implement health check endpoint in backend/src/services/recurring-task/routes/health.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Tags and Organization (Priority: P3)

**Goal**: Users can add tags to tasks for flexible categorization and filtering

**Independent Test**: Create task with tags "Create a task to review proposal tagged with work and urgent", verify tags stored, confirm filtering works

### Implementation for User Story 3

- [ ] T070 [US3] Extend Task model to include tags field in backend/src/shared/models/task.py
- [ ] T071 [US3] Extend create_task MCP tool to support tags in backend/src/mcp/tools/create_task.py
- [ ] T072 [US3] Extend update_task MCP tool to support tag operations in backend/src/mcp/tools/update_task.py
- [ ] T073 [US3] Extend list_tasks MCP tool to support tag filtering in backend/src/mcp/tools/list_tasks.py
- [ ] T074 [US3] Implement tag validation utility in backend/src/shared/utils/tag_validator.py
- [ ] T075 [US3] Update tasks list endpoint to support tag filtering in backend/src/services/chat-api/routes/tasks.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Real-Time Notifications and Reminders (Priority: P4)

**Goal**: Users receive timely notifications when task due dates approach or arrive

**Independent Test**: Create task with due date in 5 minutes, wait for reminder time, verify notification delivered

### Implementation for User Story 4

- [ ] T076 [P] [US4] Implement reminder scheduling logic in backend/src/services/chat-api/services/reminder_service.py
- [ ] T077 [US4] Extend create_task to schedule reminders in backend/src/services/chat-api/services/task_service.py
- [ ] T078 [US4] Extend update_task to reschedule reminders in backend/src/services/chat-api/services/task_service.py
- [ ] T079 [US4] Implement Notification service main application in backend/src/services/notification/main.py
- [ ] T080 [US4] Implement reminder.due event handler in backend/src/services/notification/handlers/reminder_due.py
- [ ] T081 [US4] Implement in-app notification sender in backend/src/services/notification/services/inapp_notifier.py
- [ ] T082 [US4] Implement email notification sender in backend/src/services/notification/services/email_notifier.py
- [ ] T083 [US4] Implement notification consolidation logic in backend/src/services/notification/services/consolidator.py
- [ ] T084 [US4] Implement retry logic with exponential backoff in backend/src/services/notification/services/retry_handler.py
- [ ] T085 [US4] Implement Dapr Secrets API integration for email config in backend/src/services/notification/config/secrets.py
- [ ] T086 [US4] Create Dockerfile for Notification service in backend/src/services/notification/Dockerfile
- [ ] T087 [US4] Create Kubernetes deployment for Notification service in k8s/base/notification/deployment.yaml
- [ ] T088 [US4] Create Kubernetes service for Notification service in k8s/base/notification/service.yaml
- [ ] T089 [US4] Implement health check endpoint in backend/src/services/notification/routes/health.py
- [ ] T090 [US4] Update user preferences to include notification settings in backend/src/services/chat-api/routes/preferences.py

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Advanced Search and Filtering (Priority: P5)

**Goal**: Users can search and filter tasks using natural language queries with multiple criteria

**Independent Test**: Create multiple tasks with various attributes, search with "Show me high-priority tasks tagged with work that are due this week", verify correct results

### Implementation for User Story 5

- [ ] T091 [P] [US5] Implement search_tasks MCP tool in backend/src/mcp/tools/search_tasks.py
- [ ] T092 [US5] Implement full-text search utility in backend/src/shared/utils/search.py
- [ ] T093 [US5] Implement complex query parser in backend/src/shared/utils/query_parser.py
- [ ] T094 [US5] Extend list_tasks MCP tool to support complex filtering in backend/src/mcp/tools/list_tasks.py
- [ ] T095 [US5] Implement date range filtering utility in backend/src/shared/utils/date_filters.py
- [ ] T096 [US5] Implement sorting utility in backend/src/shared/utils/sorter.py

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Real-Time Sync Across Clients (Priority: P6)

**Goal**: Users see task updates in real-time across all connected devices without manual refresh

**Independent Test**: Open chat in two browser tabs, create task in tab 1, verify it appears in tab 2 within 1 second without refresh

### Implementation for User Story 6

- [ ] T097 [P] [US6] Implement WebSocket connection manager in backend/src/services/websocket-sync/connection_manager.py
- [ ] T098 [US6] Implement WebSocket Sync service main application in backend/src/services/websocket-sync/main.py
- [ ] T099 [US6] Implement WebSocket endpoint in backend/src/services/websocket-sync/routes/websocket.py
- [ ] T100 [US6] Implement task-updates event handler in backend/src/services/websocket-sync/handlers/task_updates.py
- [ ] T101 [US6] Implement broadcast logic to connected clients in backend/src/services/websocket-sync/services/broadcaster.py
- [ ] T102 [US6] Implement reconnection handling in backend/src/services/websocket-sync/services/reconnection_handler.py
- [ ] T103 [US6] Implement sequence number tracking in backend/src/services/websocket-sync/services/sequence_tracker.py
- [ ] T104 [US6] Implement missed events sync in backend/src/services/websocket-sync/services/sync_service.py
- [ ] T105 [US6] Extend Chat API to publish sync events after task operations in backend/src/services/chat-api/services/task_service.py
- [ ] T106 [US6] Create Dockerfile for WebSocket Sync service in backend/src/services/websocket-sync/Dockerfile
- [ ] T107 [US6] Create Kubernetes deployment for WebSocket Sync service in k8s/base/websocket-sync/deployment.yaml
- [ ] T108 [US6] Create Kubernetes service for WebSocket Sync service in k8s/base/websocket-sync/service.yaml
- [ ] T109 [US6] Implement health check endpoint in backend/src/services/websocket-sync/routes/health.py
- [ ] T110 [US6] Implement WebSocket client in frontend in frontend/src/services/websocket.ts
- [ ] T111 [US6] Integrate WebSocket client with ChatKit component in frontend/src/components/ChatKit.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 9: Audit Log Service (Cross-Cutting)

**Purpose**: Maintain immutable audit trail of all task events

- [ ] T112 [P] Implement Audit Log service main application in backend/src/services/audit-log/main.py
- [ ] T113 [P] Implement task-events event handler in backend/src/services/audit-log/handlers/task_events.py
- [ ] T114 [P] Implement audit log persistence in backend/src/services/audit-log/services/audit_service.py
- [ ] T115 [P] Implement audit log query endpoint in backend/src/services/audit-log/routes/audit.py
- [ ] T116 [P] Create Dockerfile for Audit Log service in backend/src/services/audit-log/Dockerfile
- [ ] T117 [P] Create Kubernetes deployment for Audit Log service in k8s/base/audit-log/deployment.yaml
- [ ] T118 [P] Create Kubernetes service for Audit Log service in k8s/base/audit-log/service.yaml
- [ ] T119 [P] Implement health check endpoint in backend/src/services/audit-log/routes/health.py

---

## Phase 10: Cloud Deployment Configuration

**Purpose**: Enable deployment to cloud Kubernetes (AKS/GKE/OKE)

- [ ] T120 [P] Create Dapr PubSub component for cloud in k8s/dapr/pubsub-cloud.yaml
- [ ] T121 [P] Create Dapr State Store component for cloud in k8s/dapr/statestore-cloud.yaml
- [ ] T122 [P] Create Dapr Secrets component for cloud (Azure Key Vault) in k8s/dapr/secretstore-cloud-azure.yaml
- [ ] T123 [P] Create Dapr Secrets component for cloud (AWS Secrets Manager) in k8s/dapr/secretstore-cloud-aws.yaml
- [ ] T124 [P] Create Kustomization for local environment in k8s/local/kustomization.yaml
- [ ] T125 [P] Create Kustomization for cloud environment in k8s/cloud/kustomization.yaml
- [ ] T126 [P] Create GitHub Actions CI workflow in .github/workflows/ci.yml
- [ ] T127 [P] Create GitHub Actions CD workflow in .github/workflows/cd.yml

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T128 [P] Add Prometheus metrics to all services using Dapr metrics
- [ ] T129 [P] Configure distributed tracing with Zipkin
- [ ] T130 [P] Implement rate limiting middleware in Chat API in backend/src/services/chat-api/middleware/rate_limiter.py
- [ ] T131 [P] Implement CORS configuration in Chat API in backend/src/services/chat-api/middleware/cors.py
- [ ] T132 [P] Implement error handling middleware in all services
- [ ] T133 [P] Add input validation for all MCP tools
- [ ] T134 [P] Implement dead letter queue handling for failed events
- [ ] T135 [P] Add API documentation with OpenAPI/Swagger
- [ ] T136 [P] Create deployment scripts for Minikube in scripts/deploy-local.sh
- [ ] T137 [P] Create deployment scripts for cloud in scripts/deploy-cloud.sh
- [ ] T138 [P] Update README.md with Phase V architecture and setup instructions
- [ ] T139 [P] Run quickstart.md validation to ensure all steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Audit Log (Phase 9)**: Can be implemented in parallel with user stories (independent)
- **Cloud Deployment (Phase 10)**: Can be implemented after any user story is complete
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses US1 tasks but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Syncs US1 tasks but independently testable

### Within Each User Story

- MCP tools before Chat API integration
- Models before services
- Services before endpoints
- Core implementation before Kubernetes deployment
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T010) can run in parallel
- All Foundational tasks marked [P] (T012-T029, T031-T037) can run in parallel within Phase 2
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All MCP tools within a story marked [P] can run in parallel
- All Kubernetes manifests marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Audit Log service (Phase 9) can be implemented in parallel with user stories

---

## Parallel Example: User Story 1

```bash
# Launch all MCP tools for User Story 1 together:
Task T038: "Implement create_task MCP tool in backend/src/mcp/tools/create_task.py"
Task T039: "Implement update_task MCP tool in backend/src/mcp/tools/update_task.py"
Task T040: "Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py"
Task T041: "Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py"
Task T042: "Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T037) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T038-T057)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy to Minikube and validate end-to-end
6. Demo MVP to stakeholders

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T038-T057)
   - Developer B: User Story 2 (T058-T069)
   - Developer C: User Story 3 (T070-T075)
   - Developer D: Audit Log Service (T112-T119)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group with Task ID reference
- Stop at any checkpoint to validate story independently
- All services use Dapr for infrastructure abstraction (no direct Kafka/DB SDKs)
- Environment parity: same code runs on Minikube and cloud with different Dapr configs
- Observability enabled by default via Dapr (logs, metrics, traces)

---

## Task Summary

- **Total Tasks**: 139
- **Setup Phase**: 10 tasks
- **Foundational Phase**: 27 tasks (CRITICAL - blocks all user stories)
- **User Story 1 (P1)**: 20 tasks
- **User Story 2 (P2)**: 12 tasks
- **User Story 3 (P3)**: 6 tasks
- **User Story 4 (P4)**: 15 tasks
- **User Story 5 (P5)**: 6 tasks
- **User Story 6 (P6)**: 15 tasks
- **Audit Log Service**: 8 tasks
- **Cloud Deployment**: 8 tasks
- **Polish & Cross-Cutting**: 12 tasks

**Parallel Opportunities**: 87 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 57 tasks

**Independent Test Criteria**:
- US1: Create/update/complete tasks via chat with priorities and due dates
- US2: Create recurring tasks, verify auto-creation of next instance
- US3: Add/remove tags, filter tasks by tags
- US4: Schedule reminders, verify notifications delivered
- US5: Search tasks with complex queries
- US6: Open multiple tabs, verify real-time sync
