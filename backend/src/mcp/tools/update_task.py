"""
Update Task MCP Tool for Phase III User Story 4.
Allows AI agent to modify task details through natural language.

Constitutional Requirements:
- Tool is stateless (no in-memory state)
- Persists task updates to database immediately
- Returns structured result for AI agent
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..tools.base import MCPTool
from ...services.task_service import TaskService
from ...db import get_async_session

logger = logging.getLogger(__name__)


class UpdateTaskTool(MCPTool):
    """
    MCP tool for updating task details.

    Supports partial updates of title, description, due_date, and priority.
    """

    def get_name(self) -> str:
        return "update_task"

    def get_description(self) -> str:
        return """Update task details like title, description, due date, or priority.
        Use this when the user wants to change, modify, or update a task.
        Can match by task ID or task title."""

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
                    "description": "Specific task ID to update (if known)"
                },
                "task_title": {
                    "type": "string",
                    "description": "Current task title to match (if task_id not provided)"
                },
                "new_title": {
                    "type": "string",
                    "description": "New task title"
                },
                "new_description": {
                    "type": "string",
                    "description": "New task description"
                },
                "new_due_date": {
                    "type": "string",
                    "description": "New due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
                },
                "new_priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New task priority level"
                }
            },
            "required": ["user_id"]
        }

    async def execute(self, session: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the update_task tool.

        Args:
            user_id: User ID (required)
            task_id: Specific task ID (optional)
            task_title: Current task title to match (optional)
            new_title: New title (optional)
            new_description: New description (optional)
            new_due_date: New due date (optional)
            new_priority: New priority (optional)

        Returns:
            Result dictionary with updated task details
        """
        try:
            user_id = kwargs.get("user_id")
            task_id = kwargs.get("task_id")
            task_title = kwargs.get("task_title")
            new_title = kwargs.get("new_title")
            new_description = kwargs.get("new_description")
            new_due_date_str = kwargs.get("new_due_date")
            new_priority = kwargs.get("new_priority")

            # Validate required fields
            if not user_id:
                return self._error_response(
                    "invalid_input",
                    "User ID is required"
                )

            if not task_id and not task_title:
                return self._error_response(
                    "invalid_input",
                    "Either task_id or task_title is required to identify the task"
                )

            # Check if at least one field to update is provided
            if not any([new_title, new_description, new_due_date_str, new_priority]):
                return self._error_response(
                    "invalid_input",
                "At least one field to update must be provided"
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

            # Parse due date if provided
            new_due_date = None
            if new_due_date_str:
                try:
                    new_due_date = datetime.fromisoformat(new_due_date_str.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid due date format: {new_due_date_str}")
                    return self._error_response(
                        "invalid_input",
                        f"Invalid due date format: {new_due_date_str}. Please use ISO 8601 format."
                    )

            # Update task
            updated_task = await task_service.update_task(
                task_id=task_id,
                user_id=str(user_id),
                title=new_title,
                description=new_description,
                due_date=new_due_date,
                priority=new_priority
            )

            if not updated_task:
                return self._error_response(
                    "tool_failure",
                    "Failed to update task"
                )

            # Build update summary
            updates = []
            if new_title:
                updates.append(f"title to '{new_title}'")
            if new_description:
                updates.append("description")
            if new_due_date:
                updates.append(f"due date to {new_due_date.strftime('%Y-%m-%d')}")
            if new_priority:
                updates.append(f"priority to {new_priority}")

            update_summary = ", ".join(updates)

            logger.info(f"Updated task {task_id} for user {user_id}: {update_summary}")

            return self._success_response(
                data={
                    "task_id": task_id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                    "priority": updated_task.priority.value if updated_task.priority else None,
                    "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                },
                message=f"Updated task '{updated_task.title}' ({update_summary})"
            )

        except Exception as e:
            logger.error(f"Error updating task: {str(e)}", exc_info=True)
            return self._error_response(
                "tool_failure",
                f"Failed to update task: {str(e)}"
            )

