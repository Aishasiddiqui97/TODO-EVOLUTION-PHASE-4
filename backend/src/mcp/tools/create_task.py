"""
Create Task MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to create tasks through natural language conversation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskPriority, TaskStatus, RecurrencePattern
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key


class CreateTaskInput(BaseModel):
    """Input parameters for create_task tool."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field("medium", pattern="^(high|medium|low)$")
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrencePattern: Optional[Dict[str, Any]] = None
    userId: str


class CreateTaskOutput(BaseModel):
    """Output from create_task tool."""
    success: bool
    taskId: str
    message: str


async def create_task(input_data: CreateTaskInput) -> CreateTaskOutput:
    """
    Create a new task.

    Args:
        input_data: Task creation parameters

    Returns:
        CreateTaskOutput with task ID and success message
    """
    dapr_client = DaprClientWrapper()
    event_publisher = EventPublisher("chat-api")

    # Generate task ID
    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    # Create task object
    task_data = {
        "id": task_id,
        "userId": input_data.userId,
        "title": input_data.title,
        "description": input_data.description,
        "priority": input_data.priority or "medium",
        "dueDate": input_data.dueDate,
        "dueTime": input_data.dueTime,
        "tags": input_data.tags or [],
        "status": "pending",
        "recurrencePattern": input_data.recurrencePattern,
        "parentTaskId": None,
        "createdAt": now,
        "updatedAt": now,
        "completedAt": None
    }

    # Validate with Pydantic model
    task = Task(**task_data)

    # Save to state store
    state_key = generate_task_key(input_data.userId, task_id)
    await dapr_client.save_state(state_key, task.dict())

    # Update task index for user
    index_key = f"chat-api.task-index.user.{input_data.userId}"
    task_index = await dapr_client.get_state(index_key) or {"taskIds": []}
    if task_id not in task_index["taskIds"]:
        task_index["taskIds"].append(task_id)
        await dapr_client.save_state(index_key, task_index)

    # Publish task.created event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.created",
        user_id=input_data.userId,
        payload={"task": task.dict()}
    )

    return CreateTaskOutput(
        success=True,
        taskId=task_id,
        message=f"Task '{input_data.title}' created successfully"
    )
