---
id: 005
title: Phase V Event-Driven Dapr Architecture
stage: constitution
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: Aisha.A.Siddiqui
command: /sp.constitution
labels: ["phase-v", "event-driven", "dapr", "kubernetes", "observability", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

# SP Constitution – Phase V (WHY)

## Purpose

This document defines the **non-negotiable principles, constraints, and standards** for Phase V. All agents and implementations must comply.

---

## Core Principles

* **Spec-Driven Development (SDD) only** – No code without approved specs.
* **Agentic Execution** – All code written by Claude Code via Spec-KitPlus MCP.
* **Event-Driven Architecture** – All inter-service communication via events.
* **Infrastructure Abstraction** – No direct Kafka/DB SDK usage in app code.
* **Environment Parity** – Same behavior on Minikube and Cloud Kubernetes.
* **Observability First** – Logging, metrics, tracing enabled by default.

---

## Mandatory Technologies

* Kubernetes (Minikube + AKS/GKE/OKE)
* Dapr (PubSub, State, Jobs, Secrets, Service Invocation)
* Kafka-compatible broker (Redpanda / Confluent / Strimzi)
* Helm charts (from Phase IV)
* GitHub Actions CI/CD

---

## Forbidden Practices

* Manual coding outside Claude Code
* Direct Kafka clients in services
* Hardcoded secrets or URLs
* Skipping Spec → Plan → Tasks lifecycle

---

## Quality Gates

* Every commit references Task ID
* Every service has Dapr sidecar
* Every feature maps to acceptance criteria

---

**Hierarchy Rule**: Constitution > Specify > Plan > Tasks > Implement

## Response snapshot

Constitution updated from v1.2.0 to v1.3.0 with Phase V governance rules.

Added comprehensive Phase V section covering:
- Purpose: Event-driven architecture using Dapr on Kubernetes with strict SDD and AI-only implementation
- Core Principles: Spec-Driven Development Only, Agentic Execution, Event-Driven Architecture, Infrastructure Abstraction, Environment Parity, Observability First
- Architectural Constraints: Kubernetes, Dapr 1.12+, Kafka-compatible brokers, Helm charts, GitHub Actions
- Behavioral Rules: Event Publishing, Event Subscription, State Management, Secrets Management
- Forbidden Practices: Manual coding, direct Kafka clients, hardcoded secrets, skipping SDD lifecycle
- Quality Gates: Task traceability, Dapr sidecars, acceptance criteria mapping, observability, event schemas
- Hierarchy Rule: Constitution > Specification > Plan > Tasks > Implementation

All principles include explicit rationales explaining the governance decisions and architectural choices.

## Outcome

- ✅ Impact: Added Phase V governance rules establishing event-driven architecture with Dapr, infrastructure abstraction, and observability-first principles
- 🧪 Tests: No tests required for constitution updates
- 📁 Files: Updated .specify/memory/constitution.md (v1.2.0 → v1.3.0)
- 🔁 Next prompts: Review and update plan-template.md, tasks-template.md, and spec-template.md for Phase V alignment (Dapr components, event-driven patterns, observability requirements); create Phase V specification
- 🧠 Reflection: MINOR version bump appropriate - added new phase-specific governance for event-driven architecture without breaking existing Phase III and Phase IV rules

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review required for governance changes
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Apply Phase V rules to create event-driven architecture specification with Dapr integration
