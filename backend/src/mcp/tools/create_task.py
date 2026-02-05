"""
Create Task MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to create tasks through natural language conversation.
Supports recurring tasks with natural language pattern parsing.
Automatically schedules reminders for tasks with due dates.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskPriority, TaskStatus, RecurrencePattern
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key
from ...shared.utils.recurrence_parser import parse_recurrence_pattern, validate_recurrence_pattern, RecurrenceParserError
from ...shared.utils.recurrence_calculator import get_recurrence_summary
from ...services.chat_api.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)


class CreateTaskInput(BaseModel):
    """Input parameters for create_task tool."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field("medium", pattern="^(high|medium|low)$")
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    recurrencePattern: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description="Recurrence pattern as natural language (e.g., 'daily', 'every monday') or structured dict"
    )
    userId: str


class CreateTaskOutput(BaseModel):
    """Output from create_task tool."""
    success: bool
    taskId: str
    message: str


async def create_task(input_data: CreateTaskInput) -> CreateTaskOutput:
    """
    Create a new task with optional recurrence pattern.

    Supports natural language recurrence patterns like:
    - "daily" / "every day"
    - "weekly" / "every week"
    - "every N days" (e.g., "every 3 days")
    - "weekdays"
    - "every monday" / "every monday and wednesday"

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

    # Parse recurrence pattern if provided
    parsed_recurrence = None
    recurrence_summary = None

    if input_data.recurrencePattern:
        try:
            if isinstance(input_data.recurrencePattern, str):
                # Parse natural language pattern
                parsed_pattern = parse_recurrence_pattern(input_data.recurrencePattern)
                validate_recurrence_pattern(parsed_pattern)
                parsed_recurrence = parsed_pattern.dict()
                recurrence_summary = get_recurrence_summary(parsed_pattern)
            elif isinstance(input_data.recurrencePattern, dict):
                # Validate structured pattern
                pattern_obj = RecurrencePattern(**input_data.recurrencePattern)
                validate_recurrence_pattern(pattern_obj)
                parsed_recurrence = pattern_obj.dict()
                recurrence_summary = get_recurrence_summary(pattern_obj)
        except RecurrenceParserError as e:
            return CreateTaskOutput(
                success=False,
                taskId="",
                message=f"Invalid recurrence pattern: {str(e)}"
            )
        except Exception as e:
            return CreateTaskOutput(
                success=False,
                taskId="",
                message=f"Error parsing recurrence pattern: {str(e)}"
            )

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
        "recurrencePattern": parsed_recurrence,
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

    # Initialize occurrence count for recurring tasks
    if parsed_recurrence:
        occurrence_key = f"chat-api.recurrence.{task_id}.count"
        await dapr_client.save_state(occurrence_key, {"count": 1})

    # Publish task.created event
    await event_publisher.publish(
        topic="task-events",
        event_type="task.created",
        user_id=input_data.userId,
        payload={"task": task.dict()}
    )

    # Schedule reminders if task has due date (T077)
    if input_data.dueDate:
        try:
            reminder_service = ReminderService()
            due_datetime = reminder_service.parse_due_datetime(
                input_data.dueDate,
                input_data.dueTime or "09:00"
            )

            if due_datetime:
                reminder_result = await reminder_service.schedule_reminder(
                    task_id=task_id,
                    user_id=input_data.userId,
                    due_datetime=due_datetime,
                    task_title=input_data.title
                )

                if reminder_result["success"]:
                    logger.info(f"Scheduled reminders for task {task_id}")
                else:
                    logger.warning(f"Failed to schedule reminders: {reminder_result['message']}")
        except Exception as e:
            # Don't fail task creation if reminder scheduling fails
            logger.error(f"Error scheduling reminders: {e}", exc_info=True)

    # Build success message
    if recurrence_summary:
        message = f"Recurring task '{input_data.title}' created successfully. {recurrence_summary}"
    else:
        message = f"Task '{input_data.title}' created successfully"

    return CreateTaskOutput(
        success=True,
        taskId=task_id,
        message=message
    )
