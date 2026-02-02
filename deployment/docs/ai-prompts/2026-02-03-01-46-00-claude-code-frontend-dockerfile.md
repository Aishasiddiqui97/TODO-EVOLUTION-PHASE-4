# AI Prompt: Frontend Dockerfile Generation

**Date**: 2026-02-03
**Tool**: Claude Code (Claude Sonnet 4.5)
**Task**: T007 - Generate frontend Dockerfile

## Prompt

Generate a production-ready Dockerfile for a React frontend application with the following requirements:

- Base image: node:18-alpine (build stage), nginx:alpine (runtime stage)
- Dependencies: frontend/package.json
- Build command: npm run build
- Port: 80
- Multi-stage build (Node.js for build, nginx for serving)
- Run as non-root user for security
- Optimize layer caching
- Configure nginx for SPA routing

## Generated Output

See: deployment/dockerfiles/frontend.Dockerfile

## Review Notes

- Multi-stage build implemented: builder (Node.js) + runtime (nginx)
- Non-root user configured in nginx
- Custom nginx.conf for SPA routing (fallback to index.html)
- Layer caching optimized (package.json copied first)
- Image size target: <50MB

## Commit

Committed with message: "feat(deploy): add AI-generated Dockerfiles for backend and frontend"
