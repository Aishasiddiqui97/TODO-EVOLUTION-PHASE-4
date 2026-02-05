"""
Update Task MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to update task properties through natural language conversation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskPriority, TaskStatus
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key


class UpdateTaskInput(BaseModel):
    """Input parameters for update_task tool."""
    taskId: str = Field(..., min_length=1)
    userId: str
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = None


class UpdateTaskOutput(BaseModel):
    """Output from update_task tool."""
    success: bool
    message: str


async def update_task(input_data: UpdateTaskInput) -> UpdateTaskOutput:
    """
    Update an existing task.

    Args:
        input_data: Task update parameters

    Returns:
        UpdateTaskOutput with success message
    """
    dapr_client = DaprClientWrapper()
    event_publisher = EventPublisher("chat-api")

    # Retrieve existing task
    state_key = generate_task_key(input_data.userId, input_data.taskId)
    task_data = await dapr_client.get_state(state_key)

    if not task_data:
        return UpdateTaskOutput(
            success=False,
            message=f"Task with ID '{input_data.taskId}' not found"
        )

    # Validate existing task
    task = Task(**task_data)

    # Update only provided fields
    update_fields = {}
    if input_data.title is not None:
        update_fields["title"] = input_data.title
    if input_data.description is not None:
        update_fields["description"] = input_data.description
    if input_data.priority is not None:
        update_fields["priority"] = input_data.priority
    if input_data.dueDate is not None:
        update_fields["dueDate"] = input_data.dueDate
    if input_data.dueTime is not None:
        update_fields["dueTime"] = input_data.dueTime
    if input_data.tags is not None:
        update_fields["tags"] = input_data.tags

    # Apply updates
    updated_task_data = task.dict()
    updated_task_data.update(update_fields)
    updated_task_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"

    # Validate updated task
    updated_task = Task(**updated_task_data)

    # Save to state store
    await dapr_client.save_state(state_key, updated_task.dict())

    # Publish task.updated event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.updated",
        user_id=input_data.userId,
        payload={
            "task": updated_task.dict(),
            "updatedFields": list(update_fields.keys())
        }
    )

    return UpdateTaskOutput(
        success=True,
        message=f"Task '{updated_task.title}' updated successfully"
    )
