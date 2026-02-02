"""
Complete Task MCP Tool for Phase III User Story 3.
Allows AI agent to mark tasks as complete through natural language.

Constitutional Requirements:
- Tool is stateless (no in-memory state)
- Persists task update to database immediately
- Returns structured result for AI agent
"""
from typing import Dict, Any, Optional
import logging

from ..tools.base import MCPTool
from ...services.task_service import TaskService
from ...db import get_async_session

logger = logging.getLogger(__name__)


class CompleteTaskTool(MCPTool):
    """
    MCP tool for marking tasks as complete.

    Supports matching by task ID or title.
    """

    def get_name(self) -> str:
        return "complete_task"

    def get_description(self) -> str:
        return """Mark a task as complete. Use this when the user says they finished,
        completed, or are done with a task. Can match by task ID or task title."""

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
                    "description": "Specific task ID to complete (if known)"
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
        Execute the complete_task tool.

        Args:
            user_id: User ID (required)
            task_id: Specific task ID (optional)
            task_title: Task title to match (optional)

        Returns:
            Result dictionary with updated task details
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

            # Check if already completed
            if task.completed:
                return self._success_response(
                    data={
                        "task_id": task_id,
                        "title": task.title,
                        "completed": True,
                        "already_completed": True
                    },
                    message=f"Task '{task.title}' was already marked as complete."
                )

            # Mark task as complete
            updated_task = await task_service.complete_task(task_id, str(user_id))

            if not updated_task:
                return self._error_response(
                    "tool_failure",
                    "Failed to mark task as complete"
                )

            logger.info(f"Completed task {task_id} for user {user_id}: {updated_task.title}")

            return self._success_response(
                data={
                    "task_id": task_id,
                    "title": updated_task.title,
                    "completed": True,
                    "completed_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                },
                message=f"Task '{updated_task.title}' marked as complete!"
            )

        except Exception as e:
            logger.error(f"Error completing task: {str(e)}", exc_info=True)
            return self._error_response(
                "tool_failure",
                f"Failed to complete task: {str(e)}"
            )

