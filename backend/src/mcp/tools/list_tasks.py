"""
List Tasks MCP Tool for Phase III User Story 2.
Allows AI agent to retrieve and filter tasks through natural language.

Constitutional Requirements:
- Tool is stateless (no in-memory state)
- Fetches tasks from database each time
- Returns structured result for AI agent
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from ..tools.base import MCPTool
from ...services.task_service import TaskService
from ...db import get_async_session

logger = logging.getLogger(__name__)


class ListTasksTool(MCPTool):
    """
    MCP tool for retrieving and filtering tasks.

    Supports filtering by status, due date, and search queries.
    """

    def get_name(self) -> str:
        return "list_tasks"

    def get_description(self) -> str:
        return """Retrieve and list tasks for the user. Use this when the user wants to see,
        view, list, or check their tasks. Supports filtering by status (all, pending, completed),
        due date (today, overdue), and search queries."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the user"
                },
                "filter": {
                    "type": "string",
                    "enum": ["all", "pending", "completed", "today", "overdue"],
                    "description": "Filter tasks by status or due date"
                },
                "search": {
                    "type": "string",
                    "description": "Optional search query to filter tasks by title or description"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of tasks to return (default: 50)"
                }
            },
            "required": ["user_id"]
        }

    async def execute(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the list_tasks tool.

        Args:
            session: Database session (shared from chat endpoint)
            user_id: User ID (required)
            filter: Filter type (optional)
            search: Search query (optional)
            limit: Maximum results (optional)

        Returns:
            Result dictionary with task list
        """
        try:
            user_id = kwargs.get("user_id")
            filter_type = kwargs.get("filter", "all")
            search_query = kwargs.get("search")
            limit = kwargs.get("limit", 50)

            # Validate required fields
            if not user_id:
                return self._error_response(
                    "invalid_input",
                    "User ID is required"
                )

            task_service = TaskService(session)

            # Handle search query first
            if search_query:
                tasks = await task_service.search_tasks(
                    user_id=str(user_id),
                    query=search_query,
                    limit=limit
                )
            # Handle filter types
            elif filter_type == "pending":
                tasks = await task_service.get_user_tasks(
                    user_id=str(user_id),
                    completed=False,
                    limit=limit
                )
            elif filter_type == "completed":
                tasks = await task_service.get_user_tasks(
                    user_id=str(user_id),
                    completed=True,
                    limit=limit
                )
            elif filter_type == "today":
                # Get all pending tasks and filter by due date
                all_tasks = await task_service.get_user_tasks(
                    user_id=str(user_id),
                    completed=False,
                    limit=limit
                )
                today = datetime.now().date()
                tasks = [
                    task for task in all_tasks
                    if task.due_date and task.due_date.date() == today
                ]
            elif filter_type == "overdue":
                # Get all pending tasks and filter by overdue
                all_tasks = await task_service.get_user_tasks(
                    user_id=str(user_id),
                    completed=False,
                    limit=limit
                )
                now = datetime.now()
                tasks = [
                    task for task in all_tasks
                    if task.due_date and task.due_date < now
                ]
            else:  # "all" or default
                tasks = await task_service.get_user_tasks(
                    user_id=str(user_id),
                    limit=limit
                )

            # Format tasks for response
            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority.value if task.priority else None,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ]

            logger.info(f"Listed {len(task_list)} tasks for user {user_id} (filter: {filter_type})")

            # Generate appropriate message
            if len(task_list) == 0:
                message = "You don't have any tasks"
                if filter_type != "all":
                    message += f" that are {filter_type}"
                message += "."
            else:
                message = f"Found {len(task_list)} task{'s' if len(task_list) != 1 else ''}"
                if filter_type != "all":
                    message += f" ({filter_type})"

            return self._success_response(
                data={
                    "tasks": task_list,
                    "count": len(task_list),
                    "filter": filter_type
                },
                message=message
            )

        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
            return self._error_response(
                "tool_failure",
                f"Failed to list tasks: {str(e)}"
            )
