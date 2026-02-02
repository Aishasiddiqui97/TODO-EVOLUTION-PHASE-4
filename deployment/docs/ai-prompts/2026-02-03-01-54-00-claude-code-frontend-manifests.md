# AI Prompt: Frontend Kubernetes Manifests

**Date**: 2026-02-03
**Tool**: Claude Code (Claude Sonnet 4.5)
**Task**: T015 - Generate frontend Kubernetes manifests

## Prompt

Generate Kubernetes Deployment and Service manifests for the frontend component with:
- Deployment: 1 replica, image todo-frontend:v1.0.0, port 80, health check /health
- Service: NodePort type, port 80, nodePort 30080
- Resources: requests 128Mi/100m CPU, limits 256Mi/200m CPU
- Rolling update strategy: maxUnavailable 0, maxSurge 1
- Readiness and liveness probes

## Generated Output

See:
- deployment/helm/todo-chatbot/templates/frontend-deployment.yaml
- deployment/helm/todo-chatbot/templates/frontend-service.yaml

## Review Notes

- Helm templating with values.yaml references
- NodePort service exposes frontend on port 30080
- Health checks configured for readiness and liveness
- Single replica sufficient for frontend (stateless)

## Commit

Will be committed with full Helm chart in T017
