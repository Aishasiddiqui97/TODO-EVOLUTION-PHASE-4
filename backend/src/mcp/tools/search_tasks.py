"""
Search Tasks MCP Tool for Event-Driven Todo Chatbot.

Allows AI agent to search tasks using natural language queries with complex filtering.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

from ...shared.models.task import Task
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.utils.state_keys import generate_task_key
from ...shared.utils.query_parser import parse_query, build_filter_summary
from ...shared.utils.search import search_tasks_fulltext
from ...shared.utils.date_filters import filter_tasks_by_date_range, is_task_overdue, DateRange
from ...shared.utils.sorter import sort_tasks, sort_by_smart_priority, SortField, SortOrder

logger = logging.getLogger(__name__)


class SearchTasksInput(BaseModel):
    """Input parameters for search_tasks tool."""
    userId: str
    query: str = Field(..., min_length=1, max_length=500, description="Natural language search query")


class SearchTasksOutput(BaseModel):
    """Output from search_tasks tool."""
    success: bool
    tasks: List[Dict[str, Any]]
    count: int
    message: str
    filters_applied: str


async def search_tasks(input_data: SearchTasksInput) -> SearchTasksOutput:
    """
    Search tasks using natural language query with complex filtering.

    Supports:
    - Full-text search across title, description, tags
    - Status filtering (pending, completed)
    - Priority filtering (high, medium, low)
    - Tag filtering (match any or all)
    - Date range filtering (today, this week, overdue, etc.)
    - Sorting by various fields
    - Result limiting

    Examples:
        "Show me high-priority tasks tagged with work that are due this week"
        "Find completed tasks from last month"
        "Search for tasks containing 'meeting' due today"
        "List all overdue high-priority tasks"

    Args:
        input_data: Search query parameters

    Returns:
        SearchTasksOutput with matching tasks and applied filters
    """
    try:
        logger.info(f"Searching tasks for user {input_data.userId} with query: {input_data.query}")

        # Parse natural language query into structured criteria
        criteria = parse_query(input_data.query)
        logger.info(f"Parsed criteria: {criteria}")

        # Get all tasks for user
        dapr_client = DaprClientWrapper()
        index_key = f"chat-api.task-index.user.{input_data.userId}"
        task_index = await dapr_client.get_state(index_key)

        if not task_index:
            return SearchTasksOutput(
                success=True,
                tasks=[],
                count=0,
                message="No tasks found",
                filters_applied=build_filter_summary(criteria)
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
        if criteria.get("status"):
            filtered_tasks = [
                t for t in filtered_tasks
                if t.get("status") == criteria["status"]
            ]
            logger.info(f"After status filter: {len(filtered_tasks)} tasks")

        # Filter by priority
        if criteria.get("priority"):
            filtered_tasks = [
                t for t in filtered_tasks
                if t.get("priority") == criteria["priority"]
            ]
            logger.info(f"After priority filter: {len(filtered_tasks)} tasks")

        # Filter by tags
        if criteria.get("tags"):
            tags_to_match = criteria["tags"]
            match_all = criteria.get("match_all_tags", False)

            if match_all:
                # All tags must be present
                filtered_tasks = [
                    t for t in filtered_tasks
                    if all(tag.lower() in [tt.lower() for tt in t.get("tags", [])] for tag in tags_to_match)
                ]
            else:
                # Any tag matches
                filtered_tasks = [
                    t for t in filtered_tasks
                    if any(tag.lower() in [tt.lower() for tt in t.get("tags", [])] for tag in tags_to_match)
                ]
            logger.info(f"After tag filter: {len(filtered_tasks)} tasks")

        # Filter by date range
        if criteria.get("date_range"):
            filtered_tasks = filter_tasks_by_date_range(
                filtered_tasks,
                range_type=criteria["date_range"]
            )
            logger.info(f"After date range filter: {len(filtered_tasks)} tasks")

        # Filter overdue tasks
        if criteria.get("include_overdue"):
            overdue_tasks = [t for t in filtered_tasks if is_task_overdue(t)]
            filtered_tasks = overdue_tasks
            logger.info(f"After overdue filter: {len(filtered_tasks)} tasks")

        # Apply full-text search
        if criteria.get("text_query"):
            filtered_tasks = search_tasks_fulltext(
                filtered_tasks,
                criteria["text_query"],
                fields=["title", "description", "tags"],
                match_all_terms=False
            )
            logger.info(f"After full-text search: {len(filtered_tasks)} tasks")

        # Sort results
        if criteria.get("sort_by"):
            filtered_tasks = sort_tasks(
                filtered_tasks,
                sort_by=criteria["sort_by"],
                order=criteria.get("sort_order", SortOrder.DESC)
            )
        else:
            # Default: smart priority sorting
            filtered_tasks = sort_by_smart_priority(filtered_tasks)

        # Apply limit
        if criteria.get("limit"):
            filtered_tasks = filtered_tasks[:criteria["limit"]]

        # Remove internal relevance scores if present
        for task in filtered_tasks:
            task.pop("_relevance", None)

        filters_summary = build_filter_summary(criteria)
        logger.info(f"Search complete: {len(filtered_tasks)} tasks matched. Filters: {filters_summary}")

        return SearchTasksOutput(
            success=True,
            tasks=filtered_tasks,
            count=len(filtered_tasks),
            message=f"Found {len(filtered_tasks)} task(s) matching your query",
            filters_applied=filters_summary
        )

    except Exception as e:
        logger.error(f"Error searching tasks: {e}", exc_info=True)
        return SearchTasksOutput(
            success=False,
            tasks=[],
            count=0,
            message=f"Error searching tasks: {str(e)}",
            filters_applied=""
        )
