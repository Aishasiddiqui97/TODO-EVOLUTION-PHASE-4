# AI Prompt: Helm Chart Structure Generation

**Date**: 2026-02-03
**Tool**: Claude Code (Claude Sonnet 4.5)
**Task**: T013 - Generate Helm chart structure

## Prompt

Generate a Helm chart named 'todo-chatbot' with the following structure:
- Chart.yaml with metadata
- values.yaml with default configuration
- templates/ directory for Kubernetes manifests

Chart version: 1.0.0
App version: v1.0.0

## Generated Output

See: deployment/helm/todo-chatbot/

Files created:
- Chart.yaml
- values.yaml
- templates/ (manifests will be added in T014-T015)

## Review Notes

- Chart follows Helm v3 conventions
- Semantic versioning for chart and app versions
- values.yaml provides centralized configuration
- Ready for template generation

## Commit

Will be committed with Kubernetes manifests in T017
