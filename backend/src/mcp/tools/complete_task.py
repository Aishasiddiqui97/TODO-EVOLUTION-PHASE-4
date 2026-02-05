"""
Complete Task MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to mark tasks as completed through natural language conversation.
"""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskStatus
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key


class CompleteTaskInput(BaseModel):
    """Input parameters for complete_task tool."""
    taskId: str = Field(..., min_length=1)
    userId: str


class CompleteTaskOutput(BaseModel):
    """Output from complete_task tool."""
    success: bool
    message: str


async def complete_task(input_data: CompleteTaskInput) -> CompleteTaskOutput:
    """
    Mark a task as completed.

    Args:
        input_data: Task completion parameters

    Returns:
        CompleteTaskOutput with success message
    """
    dapr_client = DaprClientWrapper()
    event_publisher = EventPublisher("chat-api")

    # Retrieve existing task
    state_key = generate_task_key(input_data.userId, input_data.taskId)
    task_data = await dapr_client.get_state(state_key)

    if not task_data:
        return CompleteTaskOutput(
            success=False,
            message=f"Task with ID '{input_data.taskId}' not found"
        )

    # Validate existing task
    task = Task(**task_data)

    # Check if already completed
    if task.status == TaskStatus.COMPLETED:
        return CompleteTaskOutput(
            success=True,
            message=f"Task '{task.title}' is already completed"
        )

    # Update task status
    now = datetime.utcnow().isoformat() + "Z"
    task_data["status"] = TaskStatus.COMPLETED.value
    task_data["completedAt"] = now
    task_data["updatedAt"] = now

    # Validate updated task
    completed_task = Task(**task_data)

    # Save to state store
    await dapr_client.save_state(state_key, completed_task.dict())

    # Publish task.completed event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.completed",
        user_id=input_data.userId,
        payload={"task": completed_task.dict()}
    )

    return CompleteTaskOutput(
        success=True,
        message=f"Task '{completed_task.title}' marked as completed"
    )

