# AI Prompt: Backend Dockerfile Generation

**Date**: 2026-02-03
**Tool**: Claude Code (Claude Sonnet 4.5)
**Task**: T006 - Generate backend Dockerfile

## Prompt

Generate a production-ready Dockerfile for a Python 3.11 FastAPI backend application with the following requirements:

- Base image: python:3.11-alpine
- Dependencies: backend/requirements.txt
- Entry point: uvicorn main:app --host 0.0.0.0 --port 8000
- Port: 8000
- Health check: GET /health endpoint
- Multi-stage build to minimize image size
- Run as non-root user for security
- Optimize layer caching

## Generated Output

See: deployment/dockerfiles/backend.Dockerfile

## Review Notes

- Multi-stage build implemented: builder + runtime stages
- Non-root user (appuser, UID 1000) configured
- Health check configured with 30s interval
- Layer caching optimized (requirements.txt copied first)
- Image size target: <200MB

## Commit

Committed with message: "feat(deploy): add AI-generated Dockerfiles for backend and frontend"
