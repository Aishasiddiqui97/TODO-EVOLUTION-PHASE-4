"""
Add Task MCP Tool for Phase III User Story 1.
Allows AI agent to create tasks through natural language.

Constitutional Requirements:
- Tool is stateless (no in-memory state)
- Persists task to database immediately
- Returns structured result for AI agent
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..tools.base import MCPTool
from ...services.task_service import TaskService
from ...db import get_async_session

logger = logging.getLogger(__name__)


class AddTaskTool(MCPTool):
    """
    MCP tool for creating new tasks.

    Extracts task details from natural language and creates
    a task in the database.
    """

    def get_name(self) -> str:
        return "add_task"

    def get_description(self) -> str:
        return """Create a new task for the user. Use this when the user wants to add,
        create, or remember something. Extract the task title, optional description,
        due date, and priority from the user's message."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The task title (what needs to be done)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional detailed description of the task"
                },
                "due_date": {
                    "type": "string",
                    "description": "Optional due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Optional task priority level"
                },
                "user_id": {
                    "type": "integer",
                    "description": "ID of the user creating the task"
                }
            },
            "required": ["title", "user_id"]
        }

    async def execute(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the add_task tool.

        Args:
            session: Database session (shared from chat endpoint)
            title: Task title (required)
            description: Task description (optional)
            due_date: Due date string (optional)
            priority: Priority level (optional)
            user_id: User ID (required)

        Returns:
            Result dictionary with task details
        """
        try:
            title = kwargs.get("title")
            description = kwargs.get("description")
            due_date_str = kwargs.get("due_date")
            priority = kwargs.get("priority")
            user_id = kwargs.get("user_id")

            # Validate required fields
            if not title:
                return self._error_response(
                    "invalid_input",
                    "Task title is required"
                )

            if not user_id:
                return self._error_response(
                    "invalid_input",
                    "User ID is required"
                )

            # Parse due date if provided
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid due date format: {due_date_str}")
                    # Continue without due date rather than failing

            # Create task through service with shared session
            task_service = TaskService(session)
            task = await task_service.create_task(
                user_id=str(user_id),
                title=title,
                description=description,
                due_date=due_date,
                priority=priority
            )

            logger.info(f"Created task {task.id} for user {user_id}: {title}")

            return self._success_response(
                data={
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "completed": task.completed
                },
                message=f"Task '{title}' created successfully"
            )

        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            return self._error_response(
                "tool_failure",
                f"Failed to create task: {str(e)}"
            )

