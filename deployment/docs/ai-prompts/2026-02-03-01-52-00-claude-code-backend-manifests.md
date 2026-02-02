# AI Prompt: Backend Kubernetes Manifests

**Date**: 2026-02-03
**Tool**: Claude Code (Claude Sonnet 4.5)
**Task**: T014 - Generate backend Kubernetes manifests

## Prompt

Generate Kubernetes Deployment and Service manifests for the backend component with:
- Deployment: 3 replicas, image todo-backend:v1.0.0, port 8000, health check /health
- Service: ClusterIP type, port 8000
- Resources: requests 256Mi/250m CPU, limits 512Mi/500m CPU
- Rolling update strategy: maxUnavailable 0, maxSurge 1
- Readiness and liveness probes

## Generated Output

See:
- deployment/helm/todo-chatbot/templates/backend-deployment.yaml
- deployment/helm/todo-chatbot/templates/backend-service.yaml

## Review Notes

- Helm templating with values.yaml references
- Rolling update strategy ensures zero-downtime
- Health checks configured for readiness and liveness
- Resource limits prevent resource starvation

## Commit

Will be committed with full Helm chart in T017
