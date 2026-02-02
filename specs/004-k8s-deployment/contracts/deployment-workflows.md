# Deployment Workflow API

**Feature**: 004-k8s-deployment
**Date**: 2026-02-03
**Purpose**: Define the deployment workflow processes and their contracts

## Overview

This document specifies the deployment workflow processes that orchestrate AI tool interactions to achieve deployment goals. Each workflow is a sequence of AI tool calls with defined inputs, outputs, and validation steps.

## Workflow 1: Initial Deployment

**Purpose**: Deploy the application for the first time to a clean Minikube cluster

**Prerequisites**:
- Minikube cluster running and accessible
- kubectl configured to use minikube context
- Application source code available (backend/, frontend/)
- AI tools installed and configured

**Input Parameters**:
```yaml
app_version: string              # Application version (e.g., "v1.0.0")
backend_replicas: integer        # Initial backend replica count (default: 1)
frontend_replicas: integer       # Initial frontend replica count (default: 1)
namespace: string                # Kubernetes namespace (default: "default")
```

**Workflow Steps**:

### Step 1: Generate Dockerfiles
```yaml
action: docker-ai.generate-dockerfile
inputs:
  - component: backend
    base_image: python:3.11-alpine
    application_type: fastapi
    dependencies_file: backend/requirements.txt
    entry_point: uvicorn main:app --host 0.0.0.0 --port 8000
    port: 8000
    health_check_path: /health
    optimization_level: production

  - component: frontend
    base_image: node:18-alpine
    application_type: react-spa
    dependencies_file: frontend/package.json
    entry_point: nginx
    port: 80
    health_check_path: /
    optimization_level: production

outputs:
  - deployment/dockerfiles/backend.Dockerfile
  - deployment/dockerfiles/frontend.Dockerfile

validation:
  - Dockerfiles must be valid syntax
  - Must include HEALTHCHECK instructions
  - Must run as non-root user
  - Must use multi-stage builds

audit:
  - Save prompts to deployment/docs/ai-prompts/
  - Commit Dockerfiles to Git
```

### Step 2: Build Container Images
```yaml
action: docker.build
inputs:
  - name: todo-backend
    tag: ${app_version}
    dockerfile: deployment/dockerfiles/backend.Dockerfile
    context: ./backend

  - name: todo-frontend
    tag: ${app_version}
    dockerfile: deployment/dockerfiles/frontend.Dockerfile
    context: ./frontend

outputs:
  - Container image: todo-backend:${app_version}
  - Container image: todo-frontend:${app_version}

validation:
  - Images must build successfully
  - Images must be available in Minikube's Docker daemon
  - Image sizes must be reasonable (<500MB backend, <100MB frontend)

audit:
  - Log build output to deployment/docs/deployment-log.md
  - Record image digests and sizes
```

### Step 3: Generate Helm Chart
```yaml
action: kubectl-ai.generate-helm-chart
inputs:
  chart_name: todo-chatbot
  chart_version: 1.0.0
  app_version: ${app_version}
  components:
    - name: backend
      image: todo-backend:${app_version}
      replicas: ${backend_replicas}
      port: 8000
      service_type: ClusterIP
      health_check: /health
      resources:
        requests:
          memory: 256Mi
          cpu: 250m
        limits:
          memory: 512Mi
          cpu: 500m

    - name: frontend
      image: todo-frontend:${app_version}
      replicas: ${frontend_replicas}
      port: 80
      service_type: NodePort
      node_port: 30080
      health_check: /
      resources:
        requests:
          memory: 128Mi
          cpu: 100m
        limits:
          memory: 256Mi
          cpu: 200m

outputs:
  - deployment/helm/todo-chatbot/Chart.yaml
  - deployment/helm/todo-chatbot/values.yaml
  - deployment/helm/todo-chatbot/templates/*.yaml

validation:
  - Helm chart must pass `helm lint`
  - Templates must be valid Kubernetes YAML
  - Resource limits must be set for all containers

audit:
  - Save prompt to deployment/docs/ai-prompts/
  - Commit Helm chart to Git
```

### Step 4: Deploy to Kubernetes
```yaml
action: kubectl-ai.deploy
inputs:
  chart_path: deployment/helm/todo-chatbot/
  release_name: todo-chatbot
  namespace: ${namespace}
  values:
    backend:
      replicas: ${backend_replicas}
      image:
        tag: ${app_version}
    frontend:
      replicas: ${frontend_replicas}
      image:
        tag: ${app_version}
  wait: true
  timeout: 5m

outputs:
  release_info:
    name: todo-chatbot
    revision: 1
    status: deployed
  resources_created:
    - Deployment/todo-chatbot-backend
    - Service/todo-chatbot-backend
    - Deployment/todo-chatbot-frontend
    - Service/todo-chatbot-frontend

validation:
  - All pods must reach "Running" state
  - All containers must pass readiness probes
  - Services must have endpoints assigned
  - Deployment must complete within timeout

audit:
  - Save prompt to deployment/docs/ai-prompts/
  - Log deployment event to deployment/docs/deployment-log.md
  - Record deployment timestamp and version
```

### Step 5: Validate Deployment
```yaml
action: kagent.check-health
inputs:
  release_name: todo-chatbot
  namespace: ${namespace}
  components:
    - backend
    - frontend

outputs:
  status: healthy | degraded | unhealthy
  component_health: [...]
  service_health: [...]
  recommendations: [...]

validation:
  - Overall status must be "healthy"
  - All components must have status "healthy"
  - All services must be "active"
  - No critical recommendations

audit:
  - Save health report to deployment/docs/deployment-log.md
  - If unhealthy, trigger failure workflow
```

**Success Criteria**:
- All workflow steps complete successfully
- Application is accessible via frontend URL
- Health checks pass for all components
- Deployment logged with all artifacts

**Failure Handling**:
- If any step fails, log error and stop workflow
- Do not proceed to next step if validation fails
- Trigger diagnostic workflow to identify root cause
- Human intervention required to resolve and retry

**Output**:
```yaml
status: success | failure
deployment_id: string            # UUID
app_version: string
chart_version: string
deployment_time: string          # Duration in seconds
frontend_url: string             # e.g., http://192.168.49.2:30080
backend_url: string              # Internal ClusterIP
error_message: string            # Present if status is failure
```

---

## Workflow 2: Scale Application

**Purpose**: Horizontally scale application components

**Prerequisites**:
- Application already deployed
- Target replica count within limits (1-10)

**Input Parameters**:
```yaml
release_name: string             # Helm release name
component: string                # "backend" or "frontend"
replicas: integer                # Target replica count
namespace: string                # Kubernetes namespace
```

**Workflow Steps**:

### Step 1: Validate Current State
```yaml
action: kagent.check-health
inputs:
  release_name: ${release_name}
  namespace: ${namespace}
  components: [${component}]

validation:
  - Component must exist
  - Component must be healthy before scaling
  - Target replicas must be different from current

audit:
  - Log current state before scaling
```

### Step 2: Execute Scale Operation
```yaml
action: kubectl-ai.scale
inputs:
  release_name: ${release_name}
  component: ${component}
  replicas: ${replicas}
  namespace: ${namespace}

outputs:
  scaling_info:
    component: string
    previous_replicas: integer
    current_replicas: integer
    ready_replicas: integer

validation:
  - Deployment must update replica count
  - New pods must reach "Running" state
  - All pods must pass readiness probes

audit:
  - Save prompt to deployment/docs/ai-prompts/
  - Log scale event to deployment/docs/deployment-log.md
```

### Step 3: Validate Scaled State
```yaml
action: kagent.check-health
inputs:
  release_name: ${release_name}
  namespace: ${namespace}
  components: [${component}]

validation:
  - Component must have ${replicas} ready replicas
  - Component must be healthy
  - Service endpoints must match replica count

audit:
  - Log final state after scaling
```

**Success Criteria**:
- Component scaled to target replica count
- All replicas healthy and ready
- Service load-balancing across all replicas

**Failure Handling**:
- If scaling fails, attempt to scale back to previous count
- Log failure reason and diagnostics
- Human intervention required if rollback fails

**Output**:
```yaml
status: success | failure
component: string
previous_replicas: integer
current_replicas: integer
scaling_time: string             # Duration in seconds
error_message: string            # Present if status is failure
```

---

## Workflow 3: Update Application

**Purpose**: Deploy new version with zero-downtime rolling update

**Prerequisites**:
- Application already deployed
- New version container images built
- New version different from current version

**Input Parameters**:
```yaml
release_name: string             # Helm release name
new_version: string              # New application version
namespace: string                # Kubernetes namespace
```

**Workflow Steps**:

### Step 1: Build New Images
```yaml
action: docker.build
inputs:
  - name: todo-backend
    tag: ${new_version}
    dockerfile: deployment/dockerfiles/backend.Dockerfile
    context: ./backend

  - name: todo-frontend
    tag: ${new_version}
    dockerfile: deployment/dockerfiles/frontend.Dockerfile
    context: ./frontend

validation:
  - Images must build successfully
  - Images must be tagged with new version

audit:
  - Log build output
```

### Step 2: Upgrade Helm Release
```yaml
action: kubectl-ai.upgrade
inputs:
  release_name: ${release_name}
  chart_path: deployment/helm/todo-chatbot/
  namespace: ${namespace}
  values:
    backend:
      image:
        tag: ${new_version}
    frontend:
      image:
        tag: ${new_version}
  wait: true
  timeout: 5m

outputs:
  release_info:
    revision: integer            # Incremented revision
    status: deployed
    previous_version: string
    current_version: string

validation:
  - Rolling update must complete successfully
  - No failed requests during update
  - All pods must reach "Running" state

audit:
  - Save prompt to deployment/docs/ai-prompts/
  - Log upgrade event to deployment/docs/deployment-log.md
```

### Step 3: Validate Updated Deployment
```yaml
action: kagent.check-health
inputs:
  release_name: ${release_name}
  namespace: ${namespace}
  components:
    - backend
    - frontend

validation:
  - All components must be healthy
  - All pods must be running new version
  - No pods from old version should remain

audit:
  - Log health check results
  - Confirm version update successful
```

**Success Criteria**:
- New version deployed successfully
- Zero failed requests during update
- All components healthy with new version

**Failure Handling**:
- If update fails validation, trigger automatic rollback
- Log failure reason and diagnostics
- Restore previous working version

**Output**:
```yaml
status: success | failure
previous_version: string
current_version: string
revision: integer
update_time: string              # Duration in seconds
error_message: string            # Present if status is failure
```

---

## Workflow 4: Rollback Deployment

**Purpose**: Revert to previous working version after failed deployment

**Prerequisites**:
- Application deployed with at least 2 revisions
- Previous revision known to be working

**Input Parameters**:
```yaml
release_name: string             # Helm release name
target_revision: integer         # Optional, defaults to previous
namespace: string                # Kubernetes namespace
```

**Workflow Steps**:

### Step 1: Identify Target Revision
```yaml
action: kubectl-ai.get-history
inputs:
  release_name: ${release_name}
  namespace: ${namespace}

outputs:
  revisions:
    - revision: integer
      status: string
      chart_version: string
      app_version: string
      deployed_at: timestamp

validation:
  - Target revision must exist
  - Target revision must have status "superseded" or "deployed"

audit:
  - Log revision history
```

### Step 2: Execute Rollback
```yaml
action: kubectl-ai.rollback
inputs:
  release_name: ${release_name}
  revision: ${target_revision}
  namespace: ${namespace}
  wait: true

outputs:
  rollback_info:
    from_revision: integer
    to_revision: integer
    chart_version: string
    app_version: string

validation:
  - Rollback must complete successfully
  - All pods must reach "Running" state
  - Application must pass health checks

audit:
  - Save prompt to deployment/docs/ai-prompts/
  - Log rollback event to deployment/docs/deployment-log.md
```

### Step 3: Validate Rolled Back State
```yaml
action: kagent.check-health
inputs:
  release_name: ${release_name}
  namespace: ${namespace}
  components:
    - backend
    - frontend

validation:
  - All components must be healthy
  - All pods must be running target version
  - Services must be operational

audit:
  - Log health check results
  - Confirm rollback successful
```

**Success Criteria**:
- Application reverted to target revision
- All components healthy
- Services operational

**Failure Handling**:
- If rollback fails, log critical error
- Attempt rollback to last known good revision
- Escalate to human intervention if multiple rollbacks fail

**Output**:
```yaml
status: success | failure
from_revision: integer
to_revision: integer
from_version: string
to_version: string
rollback_time: string            # Duration in seconds
error_message: string            # Present if status is failure
```

---

## Workflow 5: Diagnose and Recover

**Purpose**: Analyze failed deployment and attempt automated recovery

**Prerequisites**:
- Deployment failure detected
- Failure type identified (image, resource, configuration, network)

**Input Parameters**:
```yaml
release_name: string             # Helm release name
namespace: string                # Kubernetes namespace
failure_type: string             # Category of failure
```

**Workflow Steps**:

### Step 1: Diagnose Root Cause
```yaml
action: kagent.diagnose-failure
inputs:
  release_name: ${release_name}
  namespace: ${namespace}
  failure_type: ${failure_type}

outputs:
  root_cause:
    category: string
    description: string
    evidence: array
  recommended_actions: array

validation:
  - Root cause must be identified
  - Recommended actions must be actionable

audit:
  - Save diagnosis to deployment/docs/deployment-log.md
```

### Step 2: Attempt Automated Recovery
```yaml
action: execute-recovery-actions
inputs:
  recommended_actions: array     # From diagnosis

logic:
  - If category is "image": Rebuild images and retry deployment
  - If category is "resource": Scale down or increase Minikube resources
  - If category is "configuration": Rollback to previous configuration
  - If category is "network": Restart affected services

validation:
  - Recovery actions must execute successfully
  - Application must pass health checks after recovery

audit:
  - Log recovery actions taken
  - Log recovery outcome
```

### Step 3: Validate Recovery
```yaml
action: kagent.check-health
inputs:
  release_name: ${release_name}
  namespace: ${namespace}

validation:
  - Application must be healthy after recovery
  - No critical issues remaining

audit:
  - Log final state after recovery
```

**Success Criteria**:
- Root cause identified
- Recovery actions executed
- Application restored to healthy state

**Failure Handling**:
- If automated recovery fails, escalate to human
- Provide detailed diagnosis and attempted actions
- Recommend manual intervention steps

**Output**:
```yaml
status: recovered | failed
root_cause: object
recovery_actions_taken: array
recovery_time: string            # Duration in seconds
error_message: string            # Present if recovery failed
```

---

## Workflow Orchestration

All workflows follow these principles:

1. **Sequential Execution**: Steps execute in order, each depending on previous success
2. **Validation Gates**: Each step validates outputs before proceeding
3. **Audit Trail**: All AI interactions logged with timestamps and artifacts
4. **Failure Handling**: Failures trigger diagnostic workflows or rollbacks
5. **Human Oversight**: Critical failures escalate to human intervention

## Testing Workflows

Each workflow should be tested with:
- Happy path (all steps succeed)
- Failure scenarios (each step fails independently)
- Edge cases (resource limits, timeouts, concurrent operations)
- Recovery scenarios (automated recovery succeeds/fails)

Test results documented in deployment log for workflow improvement.
