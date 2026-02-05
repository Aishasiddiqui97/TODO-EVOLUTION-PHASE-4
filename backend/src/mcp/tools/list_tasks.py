"""
List Tasks MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to retrieve and filter tasks through natural language conversation.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskStatus, TaskPriority
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.utils.state_keys import generate_task_key


class ListTasksInput(BaseModel):
    """Input parameters for list_tasks tool."""
    userId: str
    status: Optional[str] = Field(None, pattern="^(pending|completed)$")
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    tags: Optional[List[str]] = None
    limit: Optional[int] = Field(100, ge=1, le=1000)


class ListTasksOutput(BaseModel):
    """Output from list_tasks tool."""
    success: bool
    tasks: List[Dict[str, Any]]
    count: int
    message: str


async def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """
    List tasks with optional filtering.

    Args:
        input_data: Task listing and filtering parameters

    Returns:
        ListTasksOutput with list of tasks
    """
    dapr_client = DaprClientWrapper()

    # Query tasks from state store
    # Note: Dapr State API doesn't support complex queries natively.
    # For MVP, we'll use a simple approach with metadata query.
    # In production, consider using Dapr Query API or a dedicated query service.

    # For now, we'll use a prefix query to get all tasks for the user
    # This is a simplified implementation for MVP
    prefix = f"chat-api.task.user.{input_data.userId}"

    # Since Dapr doesn't have a native prefix query in the basic State API,
    # we'll need to maintain a task list index or use Query API
    # For MVP, we'll implement a simple approach using a task index

    # Get task index for user
    index_key = f"chat-api.task-index.user.{input_data.userId}"
    task_index = await dapr_client.get_state(index_key)

    if not task_index:
        return ListTasksOutput(
            success=True,
            tasks=[],
            count=0,
            message="No tasks found"
        )

    # Retrieve all task IDs from index
    task_ids = task_index.get("taskIds", [])

    # Fetch all tasks
    tasks = []
    for task_id in task_ids:
        state_key = generate_task_key(input_data.userId, task_id)
        task_data = await dapr_client.get_state(state_key)

        if task_data:
            try:
                task = Task(**task_data)

                # Apply filters
                if input_data.status and task.status.value != input_data.status:
                    continue
                if input_data.priority and task.priority.value != input_data.priority:
                    continue
                if input_data.tags:
                    # Check if any of the requested tags are in the task's tags
                    if not any(tag in task.tags for tag in input_data.tags):
                        continue

                tasks.append(task.dict())

                # Apply limit
                if len(tasks) >= input_data.limit:
                    break

            except Exception as e:
                # Skip invalid tasks
                continue

    return ListTasksOutput(
        success=True,
        tasks=tasks,
        count=len(tasks),
        message=f"Found {len(tasks)} task(s)"
    )
