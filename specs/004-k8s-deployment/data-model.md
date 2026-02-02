# Data Model: Kubernetes Deployment Entities

**Feature**: 004-k8s-deployment
**Date**: 2026-02-03
**Purpose**: Define deployment-related entities and their relationships

## Overview

This data model describes the entities involved in the Kubernetes deployment workflow. Unlike application data models (users, tasks), these entities represent infrastructure state and deployment metadata.

## Core Entities

### Container Image

Represents a built Docker image ready for deployment.

**Attributes**:
- `name`: String - Image name (e.g., "todo-backend", "todo-frontend")
- `tag`: String - Image version tag (e.g., "v1.0.0", "latest")
- `digest`: String - SHA256 hash of image content (immutable identifier)
- `size`: Integer - Image size in bytes
- `build_time`: Timestamp - When the image was built
- `dockerfile_path`: String - Path to source Dockerfile
- `base_image`: String - Base image used (e.g., "python:3.11-alpine")
- `layers`: Integer - Number of image layers

**Relationships**:
- One Container Image can be used in multiple Deployments
- One Container Image is generated from one Dockerfile

**State Transitions**:
```
[Not Built] → [Building] → [Built] → [Pushed to Registry] → [Deployed]
                    ↓
                [Build Failed]
```

**Validation Rules**:
- Tag must follow semantic versioning or be "latest"
- Digest must be valid SHA256 hash
- Size must be positive integer
- Build time cannot be in the future

---

### Deployment

Represents a Kubernetes deployment instance of the application.

**Attributes**:
- `id`: String - Unique deployment identifier (UUID)
- `version`: String - Application version being deployed (e.g., "v1.0.0")
- `chart_version`: String - Helm chart version used
- `timestamp`: Timestamp - When deployment was initiated
- `status`: Enum - Current deployment status
  - `pending`: Deployment initiated, not yet applied
  - `in_progress`: Kubernetes resources being created
  - `healthy`: All pods running and passing health checks
  - `degraded`: Some pods failing or not ready
  - `failed`: Deployment failed validation
  - `rolled_back`: Deployment was rolled back
- `replicas`: Object - Replica counts per component
  - `backend`: Integer - Number of backend pods
  - `frontend`: Integer - Number of frontend pods
- `images`: Object - Image references per component
  - `backend`: String - Backend image with tag
  - `frontend`: String - Frontend image with tag
- `namespace`: String - Kubernetes namespace (default: "default")
- `initiated_by`: String - User or system that initiated deployment
- `ai_tool`: String - AI tool used for deployment (e.g., "kubectl-ai")
- `prompt_reference`: String - Path to AI prompt file

**Relationships**:
- One Deployment uses multiple Container Images
- One Deployment generates multiple Deployment Events
- One Deployment creates multiple Service Endpoints

**State Transitions**:
```
[pending] → [in_progress] → [healthy]
                ↓               ↓
            [failed]      [degraded] → [healthy] (auto-heal)
                ↓               ↓
          [rolled_back]   [rolled_back]
```

**Validation Rules**:
- Version must follow semantic versioning
- Replicas must be positive integers (1-10 for local deployment)
- Namespace must be valid Kubernetes namespace name
- Status transitions must follow defined flow

---

### Service Endpoint

Represents a network access point for deployed services.

**Attributes**:
- `name`: String - Service name (e.g., "todo-backend", "todo-frontend")
- `type`: Enum - Kubernetes service type
  - `ClusterIP`: Internal cluster access only
  - `NodePort`: Exposed on node port
  - `LoadBalancer`: External load balancer (not used in Phase IV)
- `cluster_ip`: String - Internal cluster IP address
- `port`: Integer - Service port
- `target_port`: Integer - Container port
- `node_port`: Integer - External port (if type is NodePort)
- `url`: String - Accessible URL (e.g., "http://192.168.49.2:30080")
- `deployment_id`: String - Associated deployment ID
- `health_check_path`: String - Path for health checks (e.g., "/health")
- `status`: Enum - Endpoint status
  - `creating`: Service being created
  - `active`: Service accepting traffic
  - `unavailable`: No healthy pods backing the service
  - `terminating`: Service being deleted

**Relationships**:
- One Service Endpoint belongs to one Deployment
- One Service Endpoint routes to multiple Pods (via selector)

**State Transitions**:
```
[creating] → [active] → [terminating]
                ↓
          [unavailable] → [active] (pods recover)
```

**Validation Rules**:
- Port must be in range 1-65535
- NodePort must be in range 30000-32767 (Kubernetes default)
- URL must be valid HTTP/HTTPS URL
- Health check path must start with "/"

---

### Helm Release

Represents a Helm chart installation instance.

**Attributes**:
- `name`: String - Release name (e.g., "todo-chatbot")
- `chart_name`: String - Chart name (e.g., "todo-chatbot")
- `chart_version`: String - Chart version (e.g., "1.0.0")
- `app_version`: String - Application version (e.g., "v1.0.0")
- `namespace`: String - Kubernetes namespace
- `revision`: Integer - Release revision number (increments on upgrade)
- `status`: Enum - Release status
  - `deployed`: Successfully deployed
  - `superseded`: Replaced by newer revision
  - `failed`: Deployment failed
  - `pending-install`: Installation in progress
  - `pending-upgrade`: Upgrade in progress
  - `pending-rollback`: Rollback in progress
- `first_deployed`: Timestamp - Initial deployment time
- `last_deployed`: Timestamp - Most recent deployment time
- `values`: Object - Configuration values used
- `notes`: String - Helm chart notes (post-install instructions)

**Relationships**:
- One Helm Release creates one Deployment
- One Helm Release has multiple revisions (history)

**State Transitions**:
```
[pending-install] → [deployed] → [pending-upgrade] → [deployed]
        ↓               ↓               ↓
    [failed]      [superseded]      [failed]
                        ↓               ↓
                  [deployed]    [pending-rollback] → [deployed]
```

**Validation Rules**:
- Chart version must follow semantic versioning
- Revision must be positive integer
- Namespace must exist in cluster
- Values must be valid YAML

---

### Deployment Event

Represents a logged deployment action for audit trail.

**Attributes**:
- `id`: String - Unique event identifier (UUID)
- `timestamp`: Timestamp - When event occurred
- `deployment_id`: String - Associated deployment ID (if applicable)
- `action`: Enum - Type of action
  - `build_image`: Container image built
  - `deploy`: Application deployed
  - `scale`: Replicas scaled
  - `upgrade`: Application upgraded
  - `rollback`: Deployment rolled back
  - `health_check`: Health check performed
  - `failure`: Deployment failure detected
- `tool`: String - AI tool used (e.g., "docker-ai", "kubectl-ai", "kagent")
- `prompt`: String - AI prompt text
- `output`: String - Tool output/response
- `status`: Enum - Event outcome
  - `success`: Action completed successfully
  - `failure`: Action failed
  - `in_progress`: Action still running
- `error_message`: String - Error details (if status is failure)
- `commit_hash`: String - Git commit associated with this event
- `user`: String - User who initiated the action

**Relationships**:
- Multiple Deployment Events belong to one Deployment
- One Deployment Event references one AI tool interaction

**Validation Rules**:
- Timestamp cannot be in the future
- Tool must be one of: docker-ai, kubectl-ai, kagent, claude-code
- Commit hash must be valid Git SHA (if provided)
- Error message required if status is failure

---

## Entity Relationships Diagram

```
Container Image ──┐
                  ├──> Deployment ──> Helm Release
Container Image ──┘        │
                           ├──> Service Endpoint
                           │
                           └──> Deployment Event (multiple)
```

## Data Storage

**Phase IV Scope**: All deployment entities are stored in:
1. **Kubernetes Cluster State**: Deployments, Services, Pods (managed by Kubernetes)
2. **Helm Release History**: Stored in Kubernetes secrets (managed by Helm)
3. **Local Files**: Deployment events logged to `deployment/docs/deployment-log.md`
4. **Git Repository**: All AI prompts and generated artifacts version controlled

**Future Enhancement**: Consider storing deployment metadata in a database for advanced querying and analytics.

## State Persistence

- **Container Images**: Stored in Minikube's Docker daemon (ephemeral, rebuilt as needed)
- **Deployments**: Kubernetes etcd database (persists across Minikube restarts)
- **Service Endpoints**: Kubernetes etcd database
- **Helm Releases**: Kubernetes secrets in release namespace
- **Deployment Events**: Markdown file in Git repository (permanent audit trail)

## Validation and Constraints

### Cross-Entity Constraints

1. **Deployment → Container Image**: All images referenced in a deployment must exist and be built
2. **Service Endpoint → Deployment**: Service endpoints can only exist for active deployments
3. **Helm Release → Deployment**: Each Helm release revision corresponds to exactly one deployment
4. **Deployment Event → Deployment**: Events must reference valid deployment IDs

### Resource Limits (Local Deployment)

- **Maximum Replicas**: 10 per component (Minikube resource constraints)
- **Maximum Concurrent Deployments**: 1 (avoid resource contention)
- **Image Size Limit**: 1GB per image (reasonable for local development)
- **Deployment History**: Keep last 10 revisions (Helm default)

## Usage Examples

### Deployment Lifecycle

1. **Build Phase**:
   - Create Container Image entities for backend and frontend
   - Record build events in Deployment Event log

2. **Deploy Phase**:
   - Create Deployment entity with status "pending"
   - Create Helm Release entity
   - Update Deployment status to "in_progress"
   - Create Service Endpoint entities
   - Update Deployment status to "healthy" (if validation passes)
   - Record deployment event

3. **Scale Phase**:
   - Update Deployment entity replicas
   - Record scale event

4. **Rollback Phase**:
   - Create new Deployment entity (previous version)
   - Update Helm Release to previous revision
   - Update old Deployment status to "rolled_back"
   - Record rollback event

This data model provides the foundation for tracking all deployment state and maintaining the audit trail required by Phase IV constitution principles.
