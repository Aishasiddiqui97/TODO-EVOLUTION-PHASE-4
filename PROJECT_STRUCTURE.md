# Project Structure - Phase V MVP

```
Hackaton 2(1)/
│
├── backend/                          # Backend service
│   ├── src/
│   │   ├── api/                      # REST API
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tasks.py          # Task CRUD endpoints
│   │   │   │   └── chat.py           # Chat endpoint
│   │   │   └── __init__.py
│   │   │
│   │   ├── ai/                       # AI Agent
│   │   │   ├── __init__.py
│   │   │   └── agent.py              # OpenAI integration
│   │   │
│   │   ├── mcp/                      # MCP Tools
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_task.py    # Create task tool
│   │   │   │   ├── update_task.py    # Update task tool
│   │   │   │   ├── complete_task.py  # Complete task tool
│   │   │   │   ├── delete_task.py    # Delete task tool
│   │   │   │   └── list_tasks.py     # List tasks tool
│   │   │   ├── __init__.py
│   │   │   └── server.py             # MCP server
│   │   │
│   │   ├── shared/                   # Shared code
│   │   │   ├── dapr_client/
│   │   │   │   ├── __init__.py
│   │   │   │   └── client.py         # Dapr SDK wrapper
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── publisher.py      # Event publisher
│   │   │   │   └── schemas.py        # Event schemas
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py           # Task model
│   │   │   │   ├── notification.py   # Notification model
│   │   │   │   ├── task_event.py     # TaskEvent model
│   │   │   │   ├── user_preferences.py
│   │   │   │   └── conversation.py   # Conversation model
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── state_keys.py     # State key generator
│   │   │   │   ├── idempotency.py    # Idempotency checker
│   │   │   │   └── logging.py        # Structured logging
│   │   │   └── __init__.py
│   │   │
│   │   └── main.py                   # FastAPI application
│   │
│   ├── Dockerfile                    # Container image
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment template
│
├── k8s/                              # Kubernetes manifests
│   ├── dapr/                         # Dapr components
│   │   ├── pubsub-local.yaml        # Kafka PubSub
│   │   ├── statestore-local.yaml    # PostgreSQL state
│   │   ├── secretstore-local.yaml   # Kubernetes secrets
│   │   ├── local-secrets.yaml       # Secret values
│   │   ├── jobs-config.yaml         # Scheduler config
│   │   ├── resiliency.yaml          # Retry policies
│   │   ├── tracing.yaml             # Zipkin tracing
│   │   ├── subscription-chat-api.yaml
│   │   ├── subscription-websocket-sync.yaml
│   │   ├── subscription-audit-log.yaml
│   │   ├── subscription-notification.yaml
│   │   └── subscription-recurring-task.yaml
│   │
│   ├── local/                        # Local infrastructure
│   │   ├── postgres.yaml            # PostgreSQL deployment
│   │   ├── redpanda.yaml            # Kafka deployment
│   │   └── mailhog.yaml             # Email testing
│   │
│   └── services/                     # Service deployments
│       ├── chat-api-deployment.yaml # Chat API deployment
│       └── chat-api-service.yaml    # Chat API service
│
├── specs/                            # Specifications
│   └── 001-event-driven-todo/
│       ├── spec.md                   # Feature specification
│       ├── plan.md                   # Implementation plan
│       ├── tasks.md                  # Task breakdown
│       ├── research.md               # Architecture decisions
│       ├── data-model.md             # Data models
│       ├── quickstart.md             # Developer guide
│       └── contracts/
│           ├── api/
│           │   └── rest-api.md      # REST API contracts
│           ├── events/
│           │   └── event-schemas.md # Event schemas
│           └── dapr/
│               └── dapr-components.md
│
├── history/                          # Prompt history
│   └── prompts/
│       └── 001-event-driven-todo/
│
├── .specify/                         # SpecKit configuration
│   └── memory/
│       └── constitution.md           # Project principles
│
├── docker-compose.yml                # Docker Compose config
├── deploy-local.sh                   # Linux/Mac deployment
├── deploy-local.bat                  # Windows deployment
├── test-api.sh                       # API test script
├── Makefile                          # Command shortcuts
│
├── .gitignore                        # Git ignore rules
├── CLAUDE.md                         # Agent instructions
├── README.md                         # Project overview
├── QUICKSTART.md                     # Quick start guide
├── API_EXAMPLES.md                   # API usage examples
├── TROUBLESHOOTING.md                # Common issues
├── IMPLEMENTATION_STATUS.md          # Implementation status
├── VERIFICATION_CHECKLIST.md         # Verification checklist
└── SUMMARY.md                        # Complete summary
```

## Key Directories

### `/backend/src/`
Core application code with FastAPI, MCP tools, and shared libraries.

### `/k8s/`
Kubernetes manifests for Dapr components, infrastructure, and services.

### `/specs/`
Specification-driven development artifacts (spec, plan, tasks).

### `/history/`
Prompt history records for traceability.

## Key Files

### Application
- `backend/src/main.py` - FastAPI application entry point
- `backend/src/mcp/server.py` - MCP tool registry
- `backend/src/ai/agent.py` - AI agent integration

### Deployment
- `docker-compose.yml` - Local development setup
- `deploy-local.sh` - Kubernetes deployment script
- `Makefile` - Common commands

### Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - Getting started
- `API_EXAMPLES.md` - API usage
- `TROUBLESHOOTING.md` - Problem solving

## File Count

- **Python files:** 69
- **YAML files:** 140
- **Documentation:** 8 files
- **Total files:** 200+

## Lines of Code

- **Python:** ~5,000 lines
- **YAML:** ~2,000 lines
- **Documentation:** ~3,000 lines
- **Total:** ~10,000 lines
