"""
MCP Server for Event-Driven Todo Chatbot.

Provides tool registration and execution for AI agent integration.
"""

import logging
from typing import Dict, Any, List, Callable

from .tools.create_task import create_task, CreateTaskInput
from .tools.update_task import update_task, UpdateTaskInput
from .tools.complete_task import complete_task, CompleteTaskInput
from .tools.delete_task import delete_task, DeleteTaskInput
from .tools.list_tasks import list_tasks, ListTasksInput

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP (Model Context Protocol) Server for tool registration and execution.

    Manages the registry of available tools and provides schemas for AI agent.
    """

    def __init__(self):
        """Initialize the MCP server with tool registry."""
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available MCP tools."""
        # Register create_task tool
        self.tools["create_task"] = {
            "function": create_task,
            "input_model": CreateTaskInput,
            "schema": {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task with title, description, priority, due date, and tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required, 1-500 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional, max 5000 characters)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Task priority (default: medium)"
                            },
                            "dueDate": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format (optional)"
                            },
                            "dueTime": {
                                "type": "string",
                                "description": "Due time in HH:MM format (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags (optional)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            }
        }

        # Register list_tasks tool
        self.tools["list_tasks"] = {
            "function": list_tasks,
            "input_model": ListTasksInput,
            "schema": {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List and filter tasks by status, priority, or tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed"],
                                "description": "Filter by task status (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "Filter by priority (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of tasks to return (default: 100, max: 1000)"
                            }
                        },
                        "required": []
                    }
                }
            }
        }

        # Register update_task tool
        self.tools["update_task"] = {
            "function": update_task,
            "input_model": UpdateTaskInput,
            "schema": {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task's properties",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "taskId": {
                                "type": "string",
                                "description": "Task ID to update (required)"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                                "description": "New priority (optional)"
                            },
                            "dueDate": {
                                "type": "string",
                                "description": "New due date in YYYY-MM-DD format (optional)"
                            },
                            "dueTime": {
                                "type": "string",
                                "description": "New due time in HH:MM format (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New list of tags (optional)"
                            }
                        },
                        "required": ["taskId"]
                    }
                }
            }
        }

        # Register complete_task tool
        self.tools["complete_task"] = {
            "function": complete_task,
            "input_model": CompleteTaskInput,
            "schema": {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "taskId": {
                                "type": "string",
                                "description": "Task ID to complete (required)"
                            }
                        },
                        "required": ["taskId"]
                    }
                }
            }
        }

        # Register delete_task tool
        self.tools["delete_task"] = {
            "function": delete_task,
            "input_model": DeleteTaskInput,
            "schema": {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "taskId": {
                                "type": "string",
                                "description": "Task ID to delete (required)"
                            }
                        },
                        "required": ["taskId"]
                    }
                }
            }
        }

        logger.info(f"Registered {len(self.tools)} MCP tools")

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function schemas for all registered tools.

        Returns:
            List of tool schemas in OpenAI function format
        """
        return [tool["schema"] for tool in self.tools.values()]

    async def execute_tool(
        self,
        tool_name: str,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a registered tool with given parameters.

        Args:
            tool_name: Name of the tool to execute
            user_id: User ID for the operation
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {
                "success": False,
                "error": "tool_not_found",
                "message": f"Tool '{tool_name}' is not registered"
            }

        try:
            tool = self.tools[tool_name]
            function = tool["function"]
            input_model = tool["input_model"]

            # Add userId to kwargs
            kwargs["userId"] = user_id

            # Validate and create input model
            input_data = input_model(**kwargs)

            # Execute tool
            result = await function(input_data)

            # Convert result to dict
            if hasattr(result, "dict"):
                return result.dict()
            else:
                return result

        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "execution_failed",
                "message": str(e)
            }


# Global MCP server instance
mcp_server = MCPServer()
