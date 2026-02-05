"""
OpenAPI/Swagger documentation configuration.

Enhances FastAPI's automatic documentation with better descriptions and examples.
"""

from typing import Dict, Any


def get_openapi_config() -> Dict[str, Any]:
    """
    Get OpenAPI configuration for FastAPI.

    Returns:
        OpenAPI configuration dictionary
    """
    return {
        "title": "Event-Driven Todo Chatbot API",
        "description": """
# Event-Driven Todo Chatbot API

A production-ready, event-driven task management system with AI-powered natural language interface.

## Features

- **Natural Language Interface**: Interact with tasks using conversational AI
- **Event-Driven Architecture**: Built on Dapr with PubSub and State Store
- **Real-Time Sync**: WebSocket-based synchronization across devices
- **Recurring Tasks**: Flexible recurrence patterns with natural language support
- **Smart Search**: Advanced filtering and full-text search with relevance scoring
- **Notifications**: In-app and email notifications with retry logic
- **Audit Trail**: Immutable audit log for compliance and debugging

## Architecture

- **Microservices**: 5 independent services (Chat API, Recurring Task, Notification, WebSocket Sync, Audit Log)
- **Dapr Integration**: Service mesh with PubSub, State Store, and Secrets API
- **Kubernetes**: Cloud-native deployment with auto-scaling
- **CI/CD**: Automated testing and deployment with GitHub Actions

## Authentication

Currently using temporary user IDs. Production deployment should implement proper authentication.

## Rate Limiting

API endpoints are rate-limited to 100 requests per 60 seconds per client.

## Error Handling

All errors return consistent JSON responses with:
- `error`: Error message
- `status_code`: HTTP status code
- `request_id`: Unique request identifier for tracing
- `timestamp`: ISO 8601 timestamp

## Support

- GitHub: https://github.com/your-org/todo-chatbot
- Documentation: https://docs.todo-chatbot.example.com
        """,
        "version": "1.0.0",
        "contact": {
            "name": "Todo Chatbot Team",
            "email": "support@todo-chatbot.example.com",
            "url": "https://todo-chatbot.example.com"
        },
        "license_info": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "servers": [
            {
                "url": "http://localhost:8001",
                "description": "Local development"
            },
            {
                "url": "https://staging.todo-chatbot.example.com",
                "description": "Staging environment"
            },
            {
                "url": "https://api.todo-chatbot.example.com",
                "description": "Production environment"
            }
        ],
        "tags_metadata": [
            {
                "name": "tasks",
                "description": "Task management operations"
            },
            {
                "name": "chat",
                "description": "Natural language chat interface"
            },
            {
                "name": "preferences",
                "description": "User preferences management"
            },
            {
                "name": "audit",
                "description": "Audit log queries"
            },
            {
                "name": "websocket",
                "description": "Real-time synchronization"
            },
            {
                "name": "health",
                "description": "Health check endpoints"
            }
        ]
    }


def get_api_examples() -> Dict[str, Any]:
    """
    Get example requests and responses for API documentation.

    Returns:
        Dictionary of examples
    """
    return {
        "create_task": {
            "request": {
                "title": "Buy groceries",
                "description": "Get milk, eggs, and bread",
                "priority": "high",
                "dueDate": "2026-02-10",
                "dueTime": "18:00",
                "tags": ["shopping", "urgent"]
            },
            "response": {
                "success": True,
                "taskId": "task-123",
                "message": "Task 'Buy groceries' created successfully"
            }
        },
        "update_task": {
            "request": {
                "title": "Buy groceries and snacks",
                "priority": "medium"
            },
            "response": {
                "success": True,
                "message": "Task 'Buy groceries and snacks' updated successfully"
            }
        },
        "list_tasks": {
            "response": {
                "success": True,
                "tasks": [
                    {
                        "id": "task-123",
                        "userId": "user-001",
                        "title": "Buy groceries",
                        "priority": "high",
                        "status": "pending",
                        "tags": ["shopping", "urgent"],
                        "createdAt": "2026-02-06T12:00:00Z"
                    }
                ],
                "count": 1,
                "message": "Found 1 task(s)"
            }
        },
        "search_tasks": {
            "request": {
                "query": "Show me high-priority tasks tagged with work that are due this week"
            },
            "response": {
                "success": True,
                "tasks": [],
                "count": 0,
                "message": "Found 0 task(s) matching your query",
                "filters_applied": "priority: high | tags (any): work | due: this_week"
            }
        },
        "chat_message": {
            "request": {
                "message": "Add buy groceries to my list",
                "conversation_id": None
            },
            "response": {
                "response": "I've added 'Buy groceries' to your task list.",
                "conversation_id": "conv-123",
                "tool_calls": [
                    {
                        "tool": "create_task",
                        "result": {
                            "success": True,
                            "taskId": "task-123"
                        }
                    }
                ]
            }
        }
    }
