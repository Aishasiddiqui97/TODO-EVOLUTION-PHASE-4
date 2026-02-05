"""
List Tasks MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to retrieve and filter tasks through natural language conversation.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

from ...shared.models.task import Task, TaskStatus, TaskPriority
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.utils.state_keys import generate_task_key
from ...shared.utils.date_filters import filter_tasks_by_date_range, is_task_overdue, DateRange
from ...shared.utils.sorter import sort_tasks, sort_by_smart_priority, SortField, SortOrder

logger = logging.getLogger(__name__)


class ListTasksInput(BaseModel):
    """Input parameters for list_tasks tool."""
    userId: str
    status: Optional[str] = Field(None, pattern="^(pending|completed)$")
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    tags: Optional[List[str]] = None
    matchAllTags: Optional[bool] = Field(False, description="If True, all tags must match; if False, any tag matches")
    dateRange: Optional[str] = Field(None, description="Predefined date range: today, tomorrow, this_week, next_week, this_month, next_month, overdue, upcoming")
    includeOverdue: Optional[bool] = Field(False, description="Include only overdue tasks")
    sortBy: Optional[str] = Field(None, description="Field to sort by: priority, dueDate, createdAt, updatedAt, title, status")
    sortOrder: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc")
    useSmartSort: Optional[bool] = Field(False, description="Use smart priority sorting (overrides sortBy)")
    limit: Optional[int] = Field(100, ge=1, le=1000)


class ListTasksOutput(BaseModel):
    """Output from list_tasks tool."""
    success: bool
    tasks: List[Dict[str, Any]]
    count: int
    message: str


async def list_tasks(input_data: ListTasksInput) -> ListTasksOutput:
    """
    List tasks with optional filtering and sorting.

    Supports:
    - Status filtering (pending, completed)
    - Priority filtering (high, medium, low)
    - Tag filtering (match any or all)
    - Date range filtering (today, this week, overdue, etc.)
    - Overdue task filtering
    - Sorting by various fields
    - Smart priority sorting
    - Result limiting

    Args:
        input_data: Task listing and filtering parameters

    Returns:
        ListTasksOutput with list of tasks
    """
    try:
        logger.info(f"Listing tasks for user {input_data.userId} with filters: status={input_data.status}, priority={input_data.priority}, tags={input_data.tags}")

        dapr_client = DaprClientWrapper()

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
        all_tasks = []
        for task_id in task_ids:
            state_key = generate_task_key(input_data.userId, task_id)
            task_data = await dapr_client.get_state(state_key)

            if task_data:
                try:
                    task = Task(**task_data)
                    all_tasks.append(task.dict())
                except Exception as e:
                    logger.warning(f"Failed to parse task {task_id}: {e}")
                    continue

        logger.info(f"Retrieved {len(all_tasks)} total tasks")

        # Apply filters
        filtered_tasks = all_tasks

        # Filter by status
        if input_data.status:
            filtered_tasks = [
                t for t in filtered_tasks
                if t.get("status") == input_data.status
            ]
            logger.info(f"After status filter: {len(filtered_tasks)} tasks")

        # Filter by priority
        if input_data.priority:
            filtered_tasks = [
                t for t in filtered_tasks
                if t.get("priority") == input_data.priority
            ]
            logger.info(f"After priority filter: {len(filtered_tasks)} tasks")

        # Filter by tags
        if input_data.tags:
            if input_data.matchAllTags:
                # All tags must be present
                filtered_tasks = [
                    t for t in filtered_tasks
                    if all(tag.lower() in [tt.lower() for tt in t.get("tags", [])] for tag in input_data.tags)
                ]
            else:
                # Any tag matches (original behavior)
                filtered_tasks = [
                    t for t in filtered_tasks
                    if any(tag.lower() in [tt.lower() for tt in t.get("tags", [])] for tag in input_data.tags)
                ]
            logger.info(f"After tag filter: {len(filtered_tasks)} tasks")

        # Filter by date range
        if input_data.dateRange:
            try:
                date_range = DateRange(input_data.dateRange)
                filtered_tasks = filter_tasks_by_date_range(
                    filtered_tasks,
                    range_type=date_range
                )
                logger.info(f"After date range filter: {len(filtered_tasks)} tasks")
            except ValueError:
                logger.warning(f"Invalid date range: {input_data.dateRange}")

        # Filter overdue tasks
        if input_data.includeOverdue:
            overdue_tasks = [t for t in filtered_tasks if is_task_overdue(t)]
            filtered_tasks = overdue_tasks
            logger.info(f"After overdue filter: {len(filtered_tasks)} tasks")

        # Sort results
        if input_data.useSmartSort:
            # Use smart priority sorting
            filtered_tasks = sort_by_smart_priority(filtered_tasks)
            logger.info("Applied smart priority sorting")
        elif input_data.sortBy:
            try:
                sort_field = SortField(input_data.sortBy)
                sort_order = SortOrder(input_data.sortOrder)
                filtered_tasks = sort_tasks(
                    filtered_tasks,
                    sort_by=sort_field,
                    order=sort_order
                )
                logger.info(f"Sorted by {input_data.sortBy} ({input_data.sortOrder})")
            except ValueError:
                logger.warning(f"Invalid sort field or order: {input_data.sortBy}, {input_data.sortOrder}")

        # Apply limit
        if input_data.limit and len(filtered_tasks) > input_data.limit:
            filtered_tasks = filtered_tasks[:input_data.limit]
            logger.info(f"Limited to {input_data.limit} tasks")

        logger.info(f"Returning {len(filtered_tasks)} tasks")

        return ListTasksOutput(
            success=True,
            tasks=filtered_tasks,
            count=len(filtered_tasks),
            message=f"Found {len(filtered_tasks)} task(s)"
        )

    except Exception as e:
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        return ListTasksOutput(
            success=False,
            tasks=[],
            count=0,
            message=f"Error listing tasks: {str(e)}"
        )
