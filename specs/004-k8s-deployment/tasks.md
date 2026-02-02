# Tasks: Kubernetes Deployment for Cloud-Native Todo Chatbot

**Input**: Design documents from `/specs/004-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Deployment artifacts**: `deployment/` at repository root
- **Dockerfiles**: `deployment/dockerfiles/`
- **Helm charts**: `deployment/helm/todo-chatbot/`
- **Scripts**: `deployment/scripts/`
- **Documentation**: `deployment/docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Kubernetes environment and project structure

- [X] T001 Create deployment directory structure: `deployment/{dockerfiles,helm,scripts,docs/{ai-prompts,}}`
- [ ] T002 [P] Start Minikube cluster with resources: `minikube start --cpus=4 --memory=8192 --disk-size=20g` ⚠️ REQUIRES LOCAL EXECUTION
- [ ] T003 Configure Docker environment for Minikube: `eval $(minikube docker-env)` ⚠️ REQUIRES LOCAL EXECUTION
- [ ] T004 [P] Verify cluster accessibility: `kubectl cluster-info` and `kubectl get nodes` ⚠️ REQUIRES LOCAL EXECUTION
- [ ] T005 [P] Verify Helm installation: `helm version` (v3.x required) ⚠️ REQUIRES LOCAL EXECUTION

**Checkpoint**: Minikube cluster running, kubectl configured, deployment structure ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Generate and build container images (AI-driven)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Task Group A: Containerization

- [X] T006 [P] [Foundation] Generate backend Dockerfile via Docker AI or Claude Code in `deployment/dockerfiles/backend.Dockerfile`
  - Prompt: "Generate production-ready Dockerfile for Python 3.11 FastAPI backend with multi-stage build, non-root user, health check on /health"
  - Base image: python:3.11-alpine
  - Dependencies: backend/requirements.txt
  - Entry point: uvicorn main:app --host 0.0.0.0 --port 8000
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-docker-ai-backend-dockerfile.md`

- [X] T007 [P] [Foundation] Generate frontend Dockerfile via Docker AI or Claude Code in `deployment/dockerfiles/frontend.Dockerfile`
  - Prompt: "Generate production-ready Dockerfile for React frontend with Node.js build stage and nginx runtime, non-root user"
  - Base image: node:18-alpine (build), nginx:alpine (runtime)
  - Dependencies: frontend/package.json
  - Build command: npm run build
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-docker-ai-frontend-dockerfile.md`

- [X] T008 [Foundation] Review and commit generated Dockerfiles to Git
  - Validate Dockerfile syntax
  - Verify multi-stage builds, non-root users, health checks
  - Commit with message: "feat(deploy): add AI-generated Dockerfiles for backend and frontend"

- [ ] T009 [Foundation] Build backend container image in Minikube Docker context ⚠️ REQUIRES LOCAL EXECUTION
  - Command: `docker build -t todo-backend:v1.0.0 -f deployment/dockerfiles/backend.Dockerfile ./backend`
  - Verify image exists: `docker images | grep todo-backend`
  - Log build output to: `deployment/docs/deployment-log.md`

- [ ] T010 [Foundation] Build frontend container image in Minikube Docker context ⚠️ REQUIRES LOCAL EXECUTION
  - Command: `docker build -t todo-frontend:v1.0.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend`
  - Verify image exists: `docker images | grep todo-frontend`
  - Log build output to: `deployment/docs/deployment-log.md`

- [ ] T011 [P] [Foundation] Validate backend container startup locally ⚠️ REQUIRES LOCAL EXECUTION
  - Run: `docker run -d -p 8000:8000 todo-backend:v1.0.0`
  - Test health check: `curl http://localhost:8000/health`
  - Stop container after validation

- [ ] T012 [P] [Foundation] Validate frontend container startup locally ⚠️ REQUIRES LOCAL EXECUTION
  - Run: `docker run -d -p 8080:80 todo-frontend:v1.0.0`
  - Test access: `curl http://localhost:8080`
  - Stop container after validation

**Checkpoint**: Foundation ready - container images built and validated, user story implementation can now begin

---

## Phase 3: User Story 1 - Deploy Application Locally (Priority: P1) 🎯 MVP

**Goal**: Deploy complete application to local Kubernetes cluster with single command

**Independent Test**: Execute deployment command, verify frontend and backend accessible, create task through chatbot

### Task Group C: Helm Packaging

- [X] T013 [US1] Generate Helm chart structure via kubectl-ai or Claude Code
  - Prompt: "Generate Helm chart named 'todo-chatbot' with Chart.yaml, values.yaml, and templates directory"
  - Chart version: 1.0.0
  - App version: v1.0.0
  - Output to: `deployment/helm/todo-chatbot/`
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-kubectl-ai-helm-chart.md`

- [X] T014 [P] [US1] Generate backend Kubernetes manifests via kubectl-ai
  - Prompt: "Generate Kubernetes Deployment and Service for backend component"
  - Deployment: 3 replicas, image todo-backend:v1.0.0, port 8000, health check /health
  - Service: ClusterIP type, port 8000
  - Resources: requests 256Mi/250m CPU, limits 512Mi/500m CPU
  - Rolling update strategy: maxUnavailable 0, maxSurge 1
  - Output to: `deployment/helm/todo-chatbot/templates/backend-*.yaml`

- [X] T015 [P] [US1] Generate frontend Kubernetes manifests via kubectl-ai
  - Prompt: "Generate Kubernetes Deployment and Service for frontend component"
  - Deployment: 1 replica, image todo-frontend:v1.0.0, port 80, health check /
  - Service: NodePort type, port 80, nodePort 30080
  - Resources: requests 128Mi/100m CPU, limits 256Mi/200m CPU
  - Output to: `deployment/helm/todo-chatbot/templates/frontend-*.yaml`

- [X] T016 [US1] Parameterize Helm chart values in `deployment/helm/todo-chatbot/values.yaml`
  - Backend: replicas, image tag, resources, service port
  - Frontend: replicas, image tag, resources, service port, nodePort
  - Environment variables: database URL, API keys (from Phase III)

- [X] T017 [US1] Review and commit Helm chart to Git
  - Validate with: `helm lint deployment/helm/todo-chatbot/`
  - Verify templates render: `helm template todo-chatbot deployment/helm/todo-chatbot/`
  - Commit with message: "feat(deploy): add AI-generated Helm chart for todo-chatbot"

### Task Group D: AI-Assisted Deployment

- [ ] T018 [US1] Deploy application via kubectl-ai
  - Prompt: "Install todo-chatbot Helm chart to default namespace, wait for all pods ready (timeout 5m)"
  - Command: `helm install todo-chatbot deployment/helm/todo-chatbot/ --namespace default --wait --timeout 5m`
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-kubectl-ai-deploy.md`
  - Log deployment event to: `deployment/docs/deployment-log.md`

- [ ] T019 [US1] Analyze cluster health using kagent
  - Prompt: "Check health of todo-chatbot deployment in default namespace, analyze all components"
  - Verify: All pods running, services active, endpoints assigned
  - Save health report to: `deployment/docs/deployment-log.md`

- [ ] T020 [US1] Get frontend URL and validate accessibility
  - Command: `minikube service todo-chatbot-frontend --url`
  - Test: Access frontend URL in browser
  - Verify: ChatKit UI loads successfully

- [ ] T021 [US1] Validate end-to-end functionality
  - Test: Create task through chatbot interface
  - Verify: Backend processes request, data persisted to database
  - Verify: Task appears in chatbot response

**Checkpoint**: User Story 1 complete - application deployed and fully functional locally

---

## Phase 4: User Story 2 - Scale Application Components (Priority: P2)

**Goal**: Horizontally scale backend to handle increased load

**Independent Test**: Deploy application (US1), scale backend to 5 replicas, verify load distribution

- [ ] T022 [US2] Scale backend to 5 replicas via kubectl-ai
  - Prompt: "Scale backend component of todo-chatbot deployment to 5 replicas in default namespace"
  - Command: `kubectl scale deployment/todo-chatbot-backend --replicas=5 --namespace=default`
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-kubectl-ai-scale-up.md`
  - Log scale event to: `deployment/docs/deployment-log.md`

- [ ] T023 [US2] Validate scaled deployment using kagent
  - Prompt: "Check health of todo-chatbot backend, verify 5 replicas running and ready"
  - Verify: 5 backend pods in Running state
  - Verify: Service has 5 endpoints
  - Save health report to: `deployment/docs/deployment-log.md`

- [ ] T024 [US2] Test load distribution across backend replicas
  - Send multiple requests to backend service
  - Verify: Requests distributed across all 5 pods (check pod logs)
  - Document: Load balancing behavior

- [ ] T025 [US2] Scale backend down to 2 replicas via kubectl-ai
  - Prompt: "Scale backend component of todo-chatbot deployment to 2 replicas in default namespace"
  - Verify: No service interruption during scale-down
  - Verify: Only 2 backend pods remain running
  - Log scale event to: `deployment/docs/deployment-log.md`

**Checkpoint**: User Story 2 complete - scaling operations validated, load balancing confirmed

---

## Phase 5: User Story 3 - Update Application Without Downtime (Priority: P3)

**Goal**: Deploy new version with zero failed requests during rolling update

**Independent Test**: Deploy v1.0.0, generate traffic, deploy v1.1.0, verify zero failures

- [ ] T026 [US3] Build new version container images (v1.1.0)
  - Build backend: `docker build -t todo-backend:v1.1.0 -f deployment/dockerfiles/backend.Dockerfile ./backend`
  - Build frontend: `docker build -t todo-frontend:v1.1.0 -f deployment/dockerfiles/frontend.Dockerfile ./frontend`
  - Verify images exist in Minikube Docker daemon

- [ ] T027 [US3] Upgrade Helm release to v1.1.0 via kubectl-ai
  - Prompt: "Upgrade todo-chatbot Helm release to use backend image v1.1.0 and frontend image v1.1.0, wait for rolling update"
  - Command: `helm upgrade todo-chatbot deployment/helm/todo-chatbot/ --set backend.image.tag=v1.1.0 --set frontend.image.tag=v1.1.0 --wait`
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-kubectl-ai-upgrade.md`
  - Log upgrade event to: `deployment/docs/deployment-log.md`

- [ ] T028 [US3] Monitor rolling update progress
  - Watch: `kubectl rollout status deployment/todo-chatbot-backend`
  - Verify: Old and new pods coexist during transition
  - Verify: No pod failures during update

- [ ] T029 [US3] Validate updated deployment using kagent
  - Prompt: "Check health of todo-chatbot deployment, verify all pods running v1.1.0"
  - Verify: All pods running new version
  - Verify: No pods from old version remain
  - Save health report to: `deployment/docs/deployment-log.md`

- [ ] T030 [US3] Verify zero-downtime during update
  - Review deployment logs for failed requests
  - Verify: No 5xx errors during rolling update
  - Document: Update duration and behavior

**Checkpoint**: User Story 3 complete - zero-downtime updates validated

---

## Phase 6: User Story 4 - Rollback Failed Deployments (Priority: P4)

**Goal**: Automatically revert to previous version when deployment fails

**Independent Test**: Deploy working version, deploy broken version, verify automatic rollback

- [ ] T031 [US4] Simulate failed deployment (intentional)
  - Deploy broken version: Use invalid image tag or failing health check
  - Command: `helm upgrade todo-chatbot deployment/helm/todo-chatbot/ --set backend.image.tag=broken`
  - Observe: Deployment fails validation

- [ ] T032 [US4] Diagnose failure using kagent
  - Prompt: "Diagnose why todo-chatbot-backend deployment failed in default namespace"
  - Verify: Root cause identified (image not found or health check failure)
  - Save diagnosis to: `deployment/docs/deployment-log.md`

- [ ] T033 [US4] Execute rollback via kubectl-ai
  - Prompt: "Rollback todo-chatbot deployment to previous revision in default namespace, wait for completion"
  - Command: `helm rollback todo-chatbot --namespace=default --wait`
  - Save AI prompt to: `deployment/docs/ai-prompts/YYYY-MM-DD-HH-MM-SS-kubectl-ai-rollback.md`
  - Log rollback event to: `deployment/docs/deployment-log.md`

- [ ] T034 [US4] Validate rollback success using kagent
  - Prompt: "Check health of todo-chatbot deployment after rollback"
  - Verify: All pods running previous working version
  - Verify: Application functional
  - Measure: Rollback completion time (<2 minutes)

- [ ] T035 [US4] Verify deployment history
  - Command: `helm history todo-chatbot`
  - Verify: Rollback event logged with timestamp and reason
  - Document: Rollback procedure and timing

**Checkpoint**: User Story 4 complete - rollback procedures validated

---

## Phase 7: Error Handling & Recovery (Cross-Cutting Concerns)

**Purpose**: Implement automated error detection and recovery workflows

### Task Group E: Error Handling & Recovery

- [ ] T036 [P] [Recovery] Create deployment validation script in `deployment/scripts/validate-deployment.sh`
  - Check: All pods running
  - Check: Services have endpoints
  - Check: Health checks passing
  - Exit code: 0 (success) or 1 (failure)

- [ ] T037 [P] [Recovery] Create failure detection script in `deployment/scripts/detect-failure.sh`
  - Monitor: Pod status (CrashLoopBackOff, ImagePullBackOff, Pending)
  - Monitor: Service endpoints (no endpoints = failure)
  - Trigger: Alert when failure detected

- [ ] T038 [Recovery] Create automated diagnosis workflow
  - On failure detection, invoke kagent for diagnosis
  - Prompt: "Diagnose failure in todo-chatbot deployment, provide root cause and recommended actions"
  - Save diagnosis to: `deployment/docs/deployment-log.md`

- [ ] T039 [Recovery] Create automated recovery workflow
  - Based on diagnosis category:
    - Image failure → Rebuild images and retry
    - Resource failure → Scale down or alert for resource increase
    - Configuration failure → Rollback to previous version
  - Execute recovery actions via kubectl-ai
  - Log recovery attempt to: `deployment/docs/deployment-log.md`

- [ ] T040 [Recovery] Create rollback script in `deployment/scripts/rollback.sh`
  - Wrapper for: `helm rollback todo-chatbot --wait`
  - Log rollback event
  - Validate rollback success

- [ ] T041 [Recovery] Test error handling workflows
  - Simulate: Image not found
  - Simulate: Resource exhaustion
  - Simulate: Configuration error
  - Verify: Automated diagnosis and recovery for each scenario

**Checkpoint**: Error handling complete - automated recovery workflows validated

---

## Phase 8: Documentation & Auditability

**Purpose**: Complete audit trail and deployment documentation

- [ ] T042 [P] [Docs] Create deployment automation script in `deployment/scripts/deploy.sh`
  - Orchestrate: Dockerfile generation → Image build → Helm chart generation → Deployment
  - Include: AI prompt recording at each step
  - Include: Validation gates between steps

- [ ] T043 [P] [Docs] Create scaling script in `deployment/scripts/scale.sh`
  - Parameters: component (backend/frontend), replicas (1-10)
  - Execute: kubectl-ai scale command
  - Log: Scale event to deployment log

- [ ] T044 [P] [Docs] Initialize deployment log in `deployment/docs/deployment-log.md`
  - Template: Timestamp, action, tool, status, notes
  - Include: All deployment events from testing

- [ ] T045 [Docs] Document all AI prompts used during implementation
  - Organize: `deployment/docs/ai-prompts/` by timestamp and tool
  - Include: Prompt text, tool output, review notes, commit hash

- [ ] T046 [Docs] Create deployment runbook in `deployment/docs/runbook.md`
  - Procedures: Deploy, scale, update, rollback
  - Troubleshooting: Common issues and resolutions
  - AI tool usage: Examples for each operation

- [ ] T047 [Docs] Update quickstart.md with actual deployment results
  - Include: Actual timings, resource usage, URLs
  - Include: Screenshots or output examples
  - Include: Lessons learned

**Checkpoint**: Documentation complete - full audit trail established

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **User Story 3 (Phase 5)**: Depends on User Story 1 completion (can run parallel with US2)
- **User Story 4 (Phase 6)**: Depends on User Story 1 completion (can run parallel with US2/US3)
- **Error Handling (Phase 7)**: Can start after Foundational, runs parallel with user stories
- **Documentation (Phase 8)**: Runs throughout, finalized after all user stories complete

### Task Dependencies Within Phases

**Phase 2 (Foundational)**:
- T006, T007 (Dockerfile generation) → T008 (review/commit) → T009, T010 (build images) → T011, T012 (validate)

**Phase 3 (User Story 1)**:
- T013 (Helm structure) → T014, T015 (manifests) → T016 (parameterize) → T017 (review/commit) → T018 (deploy) → T019, T020, T021 (validate)

**Phase 4-6 (User Stories 2-4)**:
- Each phase is sequential within itself
- Phases can run in parallel after US1 completes

### Parallel Opportunities

- Phase 1: T002, T004, T005 can run in parallel
- Phase 2: T006, T007 can run in parallel; T011, T012 can run in parallel
- Phase 3: T014, T015 can run in parallel
- Phase 7: T036, T037 can run in parallel
- Phase 8: T042, T043, T044 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test deployment independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (blocking for others)
   - Developer B: Error Handling (Phase 7)
   - Developer C: Documentation (Phase 8)
3. After US1 complete:
   - Developer A: User Story 2
   - Developer B: User Story 3
   - Developer C: User Story 4
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All AI interactions must be recorded with prompts and outputs
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- Avoid: manual infrastructure code, skipping AI tool usage, missing audit trail
