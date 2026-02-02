# Research: Kubernetes Deployment with AI Tools

**Feature**: 004-k8s-deployment
**Date**: 2026-02-03
**Purpose**: Document AI tool selection, deployment patterns, and best practices for Phase IV implementation

## Research Questions

1. How do AI tools (Docker AI, kubectl-ai, kagent) generate infrastructure code?
2. What are best practices for containerizing Python FastAPI and JavaScript frontend applications?
3. How should Kubernetes deployments be structured for local development with Minikube?
4. What Helm chart patterns support horizontal scaling and zero-downtime updates?
5. How can deployment workflows be fully auditable and traceable?

## AI Tool Workflows

### Docker AI (Gordon) - Dockerfile Generation

**Decision**: Use Docker AI (Gordon) or Claude Code to generate Dockerfiles for backend and frontend

**Rationale**:
- AI tools understand best practices for multi-stage builds
- Automatically optimize layer caching and image size
- Generate security-hardened configurations
- Produce consistent, reviewable Dockerfiles

**Usage Pattern**:
```
Prompt: "Generate a production-ready Dockerfile for a Python 3.11 FastAPI application with the following dependencies: [list]. Use multi-stage build to minimize image size. Include health check endpoint."

Output: backend.Dockerfile with:
- Multi-stage build (builder + runtime)
- Non-root user for security
- Optimized layer caching
- Health check configuration
- Environment variable support
```

**Alternatives Considered**:
- Manual Dockerfile creation: Rejected due to AI-Only Implementation principle
- Template-based generation: Rejected as less flexible than AI-driven approach

### kubectl-ai - Kubernetes Operations

**Decision**: Use kubectl-ai for all cluster operations (deploy, scale, rollback)

**Rationale**:
- Natural language interface for Kubernetes operations
- Generates correct kubectl commands with proper flags
- Reduces syntax errors and misconfigurations
- Provides explanations for generated commands

**Usage Pattern**:
```
Prompt: "Deploy the todo-chatbot Helm chart to the default namespace with 3 backend replicas"

Output: kubectl command with proper syntax and flags
Execution: Command runs automatically with confirmation
Audit: Command and output logged to deployment history
```

**Alternatives Considered**:
- Manual kubectl commands: Rejected due to AI-Only Implementation principle
- Helm CLI directly: Rejected as kubectl-ai provides better auditability

### kagent - Cluster Analysis and Troubleshooting

**Decision**: Use kagent for deployment validation, health checks, and failure diagnosis

**Rationale**:
- Analyzes cluster state and identifies issues
- Provides actionable recommendations for fixes
- Supports automated rollback decisions
- Generates deployment status reports

**Usage Pattern**:
```
Prompt: "Check if the todo-chatbot deployment is healthy and all pods are running"

Output: Cluster state analysis with:
- Pod status for each component
- Service endpoint availability
- Resource utilization
- Identified issues and recommendations
```

**Alternatives Considered**:
- Manual kubectl get/describe commands: Rejected due to AI-Only Implementation principle
- Monitoring tools (Prometheus, Grafana): Out of scope for Phase IV (local deployment only)

## Container Best Practices

### Python FastAPI Backend

**Decision**: Multi-stage Docker build with Alpine base image

**Key Practices**:
1. **Builder Stage**: Install dependencies, compile Python packages
2. **Runtime Stage**: Copy only necessary files, run as non-root user
3. **Layer Optimization**: Copy requirements.txt first for caching
4. **Health Check**: Expose /health endpoint, configure Docker HEALTHCHECK
5. **Environment Variables**: Use .env files for configuration (not baked into image)

**Image Size Target**: <200MB (Alpine base + Python + dependencies)

**Security Considerations**:
- Run as non-root user (UID 1000)
- No secrets in image layers
- Scan images for vulnerabilities (optional, not enforced in Phase IV)

### JavaScript Frontend

**Decision**: Multi-stage build with Node.js builder and nginx runtime

**Key Practices**:
1. **Builder Stage**: npm install, build static assets
2. **Runtime Stage**: nginx serving static files
3. **Layer Optimization**: Copy package.json first for caching
4. **Configuration**: nginx.conf for SPA routing
5. **Environment Variables**: Runtime configuration via window.env.js

**Image Size Target**: <50MB (nginx + static assets)

**Security Considerations**:
- nginx runs as non-root
- Remove build tools from runtime image
- Configure proper CORS headers

## Kubernetes Deployment Patterns

### Deployment Strategy

**Decision**: Rolling update strategy with readiness probes

**Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

**Rationale**:
- maxUnavailable: 0 ensures zero-downtime updates
- maxSurge: 1 allows one extra pod during updates
- Readiness probes prevent traffic to unhealthy pods

### Service Configuration

**Decision**: ClusterIP for backend, NodePort for frontend

**Rationale**:
- Backend: Internal service, accessed only by frontend
- Frontend: Exposed to host machine via NodePort (Minikube limitation)
- LoadBalancer not available in Minikube without additional setup

**Port Mapping**:
- Backend: ClusterIP on port 8000
- Frontend: NodePort on port 30080 (maps to host)

### Resource Limits

**Decision**: Set resource requests and limits for predictable behavior

**Backend**:
- Requests: 256Mi memory, 250m CPU
- Limits: 512Mi memory, 500m CPU

**Frontend**:
- Requests: 128Mi memory, 100m CPU
- Limits: 256Mi memory, 200m CPU

**Rationale**:
- Prevents resource starvation on single-node cluster
- Enables horizontal pod autoscaling (future enhancement)
- Ensures consistent performance

## Helm Chart Structure

### Chart Organization

**Decision**: Single Helm chart with separate templates for each component

**Structure**:
```
todo-chatbot/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration
└── templates/
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

**Rationale**:
- Single chart simplifies deployment (one command)
- Separate templates maintain clear component boundaries
- values.yaml centralizes configuration

### Configuration Management

**Decision**: Use values.yaml for environment-specific configuration

**Configurable Parameters**:
- Image tags (backend, frontend)
- Replica counts
- Resource limits
- Environment variables (database URL, API keys)
- Service ports

**Rationale**:
- Supports different environments (dev, staging, prod)
- Enables easy scaling via replica count
- Separates configuration from infrastructure code

### Versioning Strategy

**Decision**: Semantic versioning for Helm chart (independent of app version)

**Version Format**: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to chart structure
- MINOR: New features (new services, configuration options)
- PATCH: Bug fixes, documentation updates

**Rationale**:
- Chart version tracks infrastructure changes
- App version tracked separately in values.yaml
- Enables rollback to previous chart versions

## Local Development Workflow

### Minikube Setup

**Prerequisites**:
1. Minikube installed and running
2. kubectl configured to use minikube context
3. Docker daemon accessible to Minikube

**Initialization**:
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g
minikube addons enable ingress  # Optional for future enhancements
eval $(minikube docker-env)     # Use Minikube's Docker daemon
```

**Rationale**:
- 4 CPUs, 8GB RAM sufficient for 2 services + overhead
- Using Minikube's Docker daemon avoids image registry setup
- Ingress addon prepared for future enhancements

### Build and Deploy Workflow

**Step 1: Generate Dockerfiles** (via AI)
```
Prompt Docker AI: "Generate Dockerfile for [component]"
Review: Human reviews generated Dockerfile
Commit: Version control the Dockerfile
```

**Step 2: Build Images** (in Minikube)
```bash
docker build -t todo-backend:latest -f deployment/dockerfiles/backend.Dockerfile ./backend
docker build -t todo-frontend:latest -f deployment/dockerfiles/frontend.Dockerfile ./frontend
```

**Step 3: Generate Helm Chart** (via AI)
```
Prompt kubectl-ai: "Generate Helm chart for todo-chatbot with backend and frontend services"
Review: Human reviews generated manifests
Commit: Version control the Helm chart
```

**Step 4: Deploy** (via kubectl-ai)
```
Prompt kubectl-ai: "Install todo-chatbot Helm chart"
Validate: kagent checks deployment health
Audit: Log deployment event with timestamp
```

**Rationale**:
- Each step involves AI generation + human review
- All artifacts version controlled for auditability
- Clear separation between build and deploy phases

## Auditability and Traceability

### Prompt Recording

**Decision**: Store all AI prompts in deployment/docs/ai-prompts/ directory

**Format**:
```
YYYY-MM-DD-HH-MM-SS-[tool]-[action].md
Example: 2026-02-03-14-30-00-docker-ai-backend-dockerfile.md

Content:
- Timestamp
- Tool used
- Prompt text
- Generated output
- Review notes
- Commit hash (after version control)
```

**Rationale**:
- Complete audit trail of AI interactions
- Enables learning from successful/failed prompts
- Supports debugging and improvement

### Deployment History

**Decision**: Maintain deployment-log.md with all deployment events

**Log Format**:
```markdown
## Deployment: 2026-02-03 14:45:00

**Version**: v1.0.0
**Action**: Initial deployment
**Tool**: kubectl-ai
**Prompt**: "Install todo-chatbot Helm chart"
**Status**: Success
**Pods**: backend-xxx (3 replicas), frontend-yyy (1 replica)
**Commit**: abc123def
**Notes**: First production deployment
```

**Rationale**:
- Chronological record of all deployments
- Links deployments to Git commits
- Supports rollback decisions

### Version Control Strategy

**Decision**: Commit all AI-generated artifacts to Git

**Commit Message Format**:
```
feat(deploy): add [component] Dockerfile

Generated by: Docker AI
Prompt: [brief description]
Review: [reviewer name]

Co-Authored-By: [AI Tool] <noreply@ai-tool.com>
```

**Rationale**:
- Git history shows evolution of infrastructure
- Co-authorship credits AI tool
- Commit messages link to prompts

## Risk Mitigation

### Failure Scenarios

1. **Image Build Failure**
   - Detection: Docker build exit code
   - Response: Review Dockerfile, regenerate via AI with error context
   - Audit: Log failure and resolution

2. **Deployment Failure**
   - Detection: kagent health check fails
   - Response: Automatic rollback to previous version
   - Audit: Log failure reason and rollback action

3. **Resource Exhaustion**
   - Detection: Pods in Pending state
   - Response: Scale down or increase Minikube resources
   - Audit: Log resource constraints

4. **Configuration Error**
   - Detection: Application errors in logs
   - Response: Update values.yaml, redeploy
   - Audit: Log configuration change

**Rationale**:
- Proactive failure detection
- Automated recovery where possible
- Complete audit trail for learning

## Conclusion

This research establishes the foundation for Phase IV implementation:
- AI tools (Docker AI, kubectl-ai, kagent) provide complete infrastructure automation
- Container best practices ensure secure, optimized images
- Kubernetes patterns support scaling and zero-downtime updates
- Helm charts enable single-command deployment
- Auditability mechanisms satisfy constitution requirements

All decisions align with Phase IV constitution principles: AI-Only Implementation, Local-Only Infrastructure, and Full Auditability.

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md)
