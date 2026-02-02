"""
Delete Task MCP Tool for Phase III User Story 5.
Allows AI agent to remove tasks through natural language.

Constitutional Requirements:
- Tool is stateless (no in-memory state)
- Persists deletion to database immediately
- Returns structured result for AI agent
"""
from typing import Dict, Any, Optional
import logging

from ..tools.base import MCPTool
from ...services.task_service import TaskService
from ...db import get_async_session

logger = logging.getLogger(__name__)


class DeleteTaskTool(MCPTool):
    """
    MCP tool for deleting tasks.

    Supports matching by task ID or title.
    """

    def get_name(self) -> str:
        return "delete_task"

    def get_description(self) -> str:
        return """Delete a task permanently. Use this when the user wants to remove,
        delete, or get rid of a task. Can match by task ID or task title."""

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the user"
                },
                "task_id": {
                    "type": "string",
                    "description": "Specific task ID to delete (if known)"
                },
                "task_title": {
                    "type": "string",
                    "description": "Task title to match (if task_id not provided)"
                }
            },
            "required": ["user_id"]
        }

    async def execute(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the delete_task tool.

        Args:
            user_id: User ID (required)
            task_id: Specific task ID (optional)
            task_title: Task title to match (optional)

        Returns:
            Result dictionary with deleted task details
        """
        try:
            user_id = kwargs.get("user_id")
            task_id = kwargs.get("task_id")
            task_title = kwargs.get("task_title")

            # Validate required fields
            if not user_id:
                return self._error_response(
                    "invalid_input",
                    "User ID is required"
                )

            if not task_id and not task_title:
                return self._error_response(
                "invalid_input",
                "Either task_id or task_title is required"
            )

            task_service = TaskService(session)

            # Try to find task by ID first
            if task_id:
                task = await task_service.get_task(task_id, str(user_id))
                if not task:
                    return self._error_response(
                        "task_not_found",
                        f"I couldn't find a task with ID '{task_id}'. Could you describe it differently?"
                    )
            # Otherwise, search by title
            else:
                matching_tasks = await task_service.search_tasks(
                    user_id=str(user_id),
                    query=task_title,
                    limit=5
                )

                if not matching_tasks:
                    return self._error_response(
                        "task_not_found",
                        f"I couldn't find a task matching '{task_title}'. Could you be more specific?"
                    )

                # If multiple matches, check for exact match
                exact_matches = [
                    t for t in matching_tasks
                    if t.title.lower() == task_title.lower()
                ]

                if exact_matches:
                    task = exact_matches[0]
                elif len(matching_tasks) == 1:
                    task = matching_tasks[0]
                else:
                    # Multiple matches, ask for clarification
                    suggestions = ", ".join([f"'{t.title}'" for t in matching_tasks[:3]])
                    return self._error_response(
                        "ambiguous",
                        f"I found {len(matching_tasks)} tasks matching that. Did you mean: {suggestions}?"
                    )

            task_id = str(task.id)

            # Store task details before deletion
            task_details = {
                "task_id": task_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }

            # Delete task
            deleted = await task_service.delete_task(task_id, str(user_id))

            if not deleted:
                return self._error_response(
                    "tool_failure",
                    "Failed to delete task"
                )

            logger.info(f"Deleted task {task_id} for user {user_id}: {task_details['title']}")

            return self._success_response(
                data=task_details,
                message=f"Task '{task_details['title']}' has been deleted."
            )

        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}", exc_info=True)
            return self._error_response(
                "tool_failure",
                f"Failed to delete task: {str(e)}"
            )

