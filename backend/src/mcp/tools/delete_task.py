"""
Delete Task MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to delete tasks through natural language conversation.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

from ...shared.models.task import Task
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key


class DeleteTaskInput(BaseModel):
    """Input parameters for delete_task tool."""
    taskId: str = Field(..., min_length=1)
    userId: str


class DeleteTaskOutput(BaseModel):
    """Output from delete_task tool."""
    success: bool
    message: str


async def delete_task(input_data: DeleteTaskInput) -> DeleteTaskOutput:
    """
    Delete a task.

    Args:
        input_data: Task deletion parameters

    Returns:
        DeleteTaskOutput with success message
    """
    dapr_client = DaprClientWrapper()
    event_publisher = EventPublisher("chat-api")

    # Retrieve existing task
    state_key = generate_task_key(input_data.userId, input_data.taskId)
    task_data = await dapr_client.get_state(state_key)

    if not task_data:
        return DeleteTaskOutput(
            success=False,
            message=f"Task with ID '{input_data.taskId}' not found"
        )

    # Validate existing task
    task = Task(**task_data)

    # Delete from state store
    await dapr_client.delete_state(state_key)

    # Update task index for user
    index_key = f"chat-api.task-index.user.{input_data.userId}"
    task_index = await dapr_client.get_state(index_key)
    if task_index and input_data.taskId in task_index.get("taskIds", []):
        task_index["taskIds"].remove(input_data.taskId)
        await dapr_client.save_state(index_key, task_index)

    # Publish task.deleted event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.deleted",
        user_id=input_data.userId,
        payload={
            "taskId": input_data.taskId,
            "task": task.dict()
        }
    )

    return DeleteTaskOutput(
        success=True,
        message=f"Task '{task.title}' deleted successfully"
    )

