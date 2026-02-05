"""
Task Management REST API Routes for Event-Driven Todo Chatbot.

Provides CRUD operations for tasks using Dapr State API and event publishing.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ...shared.models.task import Task, TaskPriority, TaskStatus
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key
from ...mcp.tools.create_task import create_task, CreateTaskInput
from ...mcp.tools.update_task import update_task, UpdateTaskInput
from ...mcp.tools.complete_task import complete_task, CompleteTaskInput
from ...mcp.tools.delete_task import delete_task, DeleteTaskInput
from ...mcp.tools.list_tasks import list_tasks, ListTasksInput

import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1")


# Request/Response Models
class TaskCreateRequest(BaseModel):
    """Request model for creating a task."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field("medium", pattern="^(high|medium|low)$")
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Response model for task operations."""
    id: str
    userId: str
    title: str
    description: Optional[str]
    priority: str
    dueDate: Optional[str]
    dueTime: Optional[str]
    tags: List[str]
    status: str
    createdAt: str
    updatedAt: str
    completedAt: Optional[str]


# Temporary: Hardcoded user ID for MVP
# TODO: Replace with proper authentication in production
TEMP_USER_ID = "user-001"


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(task_request: TaskCreateRequest):
    """
    Create a new task.

    Args:
        task_request: Task creation data

    Returns:
        Created task details
    """
    try:
        # Call MCP tool
        input_data = CreateTaskInput(
            title=task_request.title,
            description=task_request.description,
            priority=task_request.priority,
            dueDate=task_request.dueDate,
            dueTime=task_request.dueTime,
            tags=task_request.tags,
            userId=TEMP_USER_ID
        )

        result = await create_task(input_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        # Retrieve created task
        dapr_client = DaprClientWrapper()
        state_key = generate_task_key(TEMP_USER_ID, result.taskId)
        task_data = await dapr_client.get_state(state_key)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task created but could not be retrieved"
            )

        return TaskResponse(**task_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks_endpoint(
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(pending|completed)$"),
    priority: Optional[str] = Query(None, pattern="^(high|medium|low)$"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    List tasks with optional filtering.

    Args:
        status_filter: Filter by task status (pending/completed)
        priority: Filter by priority (high/medium/low)
        tags: Filter by tags (comma-separated)
        limit: Maximum number of tasks to return

    Returns:
        List of tasks
    """
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None

        # Call MCP tool
        input_data = ListTasksInput(
            userId=TEMP_USER_ID,
            status=status_filter,
            priority=priority,
            tags=tag_list,
            limit=limit
        )

        result = await list_tasks(input_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        return [TaskResponse(**task) for task in result.tasks]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: str):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID

    Returns:
        Task details
    """
    try:
        dapr_client = DaprClientWrapper()
        state_key = generate_task_key(TEMP_USER_ID, task_id)
        task_data = await dapr_client.get_state(state_key)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID '{task_id}' not found"
            )

        return TaskResponse(**task_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(task_id: str, task_request: TaskUpdateRequest):
    """
    Update a task.

    Args:
        task_id: Task ID
        task_request: Task update data

    Returns:
        Updated task details
    """
    try:
        # Call MCP tool
        input_data = UpdateTaskInput(
            taskId=task_id,
            userId=TEMP_USER_ID,
            title=task_request.title,
            description=task_request.description,
            priority=task_request.priority,
            dueDate=task_request.dueDate,
            dueTime=task_request.dueTime,
            tags=task_request.tags
        )

        result = await update_task(input_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result.message.lower() else status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        # Retrieve updated task
        dapr_client = DaprClientWrapper()
        state_key = generate_task_key(TEMP_USER_ID, task_id)
        task_data = await dapr_client.get_state(state_key)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task updated but could not be retrieved"
            )

        return TaskResponse(**task_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task_endpoint(task_id: str):
    """
    Mark a task as completed.

    Args:
        task_id: Task ID

    Returns:
        Updated task details
    """
    try:
        # Call MCP tool
        input_data = CompleteTaskInput(
            taskId=task_id,
            userId=TEMP_USER_ID
        )

        result = await complete_task(input_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result.message.lower() else status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        # Retrieve updated task
        dapr_client = DaprClientWrapper()
        state_key = generate_task_key(TEMP_USER_ID, task_id)
        task_data = await dapr_client.get_state(state_key)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Task completed but could not be retrieved"
            )

        return TaskResponse(**task_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(task_id: str):
    """
    Delete a task.

    Args:
        task_id: Task ID

    Returns:
        No content
    """
    try:
        # Call MCP tool
        input_data = DeleteTaskInput(
            taskId=task_id,
            userId=TEMP_USER_ID
        )

        result = await delete_task(input_data)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if "not found" in result.message.lower() else status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )
