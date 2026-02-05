"""
Sorting utility for Event-Driven Todo Chatbot.

Provides utilities to sort tasks by various criteria.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class SortField(str, Enum):
    """Fields that can be used for sorting."""
    PRIORITY = "priority"
    DUE_DATE = "dueDate"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    TITLE = "title"
    STATUS = "status"


class SortOrder(str, Enum):
    """Sort order direction."""
    ASC = "asc"
    DESC = "desc"


# Priority order for sorting (high > medium > low)
PRIORITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
    None: 0
}

# Status order for sorting (pending > completed)
STATUS_ORDER = {
    "pending": 2,
    "completed": 1,
    None: 0
}


def sort_tasks(
    tasks: List[Dict[str, Any]],
    sort_by: SortField = SortField.CREATED_AT,
    order: SortOrder = SortOrder.DESC,
    secondary_sort: Optional[SortField] = None
) -> List[Dict[str, Any]]:
    """
    Sort tasks by specified field and order.

    Args:
        tasks: List of task dictionaries
        sort_by: Field to sort by
        order: Sort order (asc or desc)
        secondary_sort: Optional secondary sort field (always ascending)

    Returns:
        Sorted list of tasks
    """
    if not tasks:
        return []

    def get_sort_key(task: Dict[str, Any]) -> tuple:
        """Generate sort key for a task."""
        primary_value = _get_field_value(task, sort_by)

        if secondary_sort:
            secondary_value = _get_field_value(task, secondary_sort)
            return (primary_value, secondary_value)

        return (primary_value,)

    # Sort tasks
    reverse = (order == SortOrder.DESC)
    sorted_tasks = sorted(tasks, key=get_sort_key, reverse=reverse)

    return sorted_tasks


def _get_field_value(task: Dict[str, Any], field: SortField) -> Any:
    """
    Get sortable value for a field.

    Args:
        task: Task dictionary
        field: Field to extract

    Returns:
        Sortable value (handles None, dates, priorities, etc.)
    """
    if field == SortField.PRIORITY:
        priority = task.get("priority")
        return PRIORITY_ORDER.get(priority, 0)

    elif field == SortField.STATUS:
        status = task.get("status")
        return STATUS_ORDER.get(status, 0)

    elif field == SortField.DUE_DATE:
        due_date_str = task.get("dueDate")
        if not due_date_str:
            # Tasks without due dates sort last
            return datetime.max

        try:
            due_date = datetime.fromisoformat(due_date_str)

            # Add time if available
            due_time_str = task.get("dueTime")
            if due_time_str:
                hour, minute = map(int, due_time_str.split(":"))
                due_date = due_date.replace(hour=hour, minute=minute)

            return due_date
        except (ValueError, AttributeError):
            return datetime.max

    elif field == SortField.CREATED_AT:
        created_at_str = task.get("createdAt")
        if not created_at_str:
            return datetime.min

        try:
            return datetime.fromisoformat(created_at_str)
        except (ValueError, AttributeError):
            return datetime.min

    elif field == SortField.UPDATED_AT:
        updated_at_str = task.get("updatedAt")
        if not updated_at_str:
            return datetime.min

        try:
            return datetime.fromisoformat(updated_at_str)
        except (ValueError, AttributeError):
            return datetime.min

    elif field == SortField.TITLE:
        title = task.get("title", "")
        return title.lower()  # Case-insensitive sort

    else:
        return ""


def sort_by_smart_priority(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort tasks by "smart priority" - a combination of priority, due date, and status.

    Smart priority logic:
    1. Overdue high-priority tasks first
    2. Overdue medium-priority tasks
    3. Overdue low-priority tasks
    4. High-priority tasks due soon
    5. Medium-priority tasks due soon
    6. Low-priority tasks due soon
    7. Other pending tasks by priority
    8. Completed tasks last

    Args:
        tasks: List of task dictionaries

    Returns:
        Sorted list of tasks
    """
    if not tasks:
        return []

    now = datetime.now()

    def smart_priority_key(task: Dict[str, Any]) -> tuple:
        """Generate smart priority sort key."""
        status = task.get("status", "pending")
        priority = task.get("priority", "medium")

        # Completed tasks always go last
        if status == "completed":
            return (999, 0, datetime.max)

        # Get priority value
        priority_value = PRIORITY_ORDER.get(priority, 2)

        # Get due date
        due_date_str = task.get("dueDate")
        if not due_date_str:
            # No due date - sort by priority only
            return (100 + (3 - priority_value), 0, datetime.max)

        try:
            due_date = datetime.fromisoformat(due_date_str)
            due_time_str = task.get("dueTime")
            if due_time_str:
                hour, minute = map(int, due_time_str.split(":"))
                due_date = due_date.replace(hour=hour, minute=minute)
            else:
                due_date = due_date.replace(hour=23, minute=59, second=59)

            # Calculate days until due
            time_until_due = (due_date - now).total_seconds()

            if time_until_due < 0:
                # Overdue - highest priority (0-2 based on priority)
                return (3 - priority_value, 0, due_date)
            elif time_until_due < 86400:  # Less than 1 day
                # Due today - very high priority (10-12)
                return (10 + (3 - priority_value), 0, due_date)
            elif time_until_due < 604800:  # Less than 7 days
                # Due this week - high priority (20-22)
                return (20 + (3 - priority_value), 0, due_date)
            else:
                # Due later - medium priority (30-32)
                return (30 + (3 - priority_value), 0, due_date)

        except (ValueError, AttributeError):
            # Invalid date - sort by priority only
            return (100 + (3 - priority_value), 0, datetime.max)

    sorted_tasks = sorted(tasks, key=smart_priority_key)
    return sorted_tasks


def sort_by_multiple_fields(
    tasks: List[Dict[str, Any]],
    sort_criteria: List[tuple[SortField, SortOrder]]
) -> List[Dict[str, Any]]:
    """
    Sort tasks by multiple fields in order of priority.

    Args:
        tasks: List of task dictionaries
        sort_criteria: List of (field, order) tuples in priority order

    Returns:
        Sorted list of tasks

    Example:
        sort_by_multiple_fields(tasks, [
            (SortField.PRIORITY, SortOrder.DESC),
            (SortField.DUE_DATE, SortOrder.ASC)
        ])
    """
    if not tasks or not sort_criteria:
        return tasks

    def multi_field_key(task: Dict[str, Any]) -> tuple:
        """Generate multi-field sort key."""
        key_parts = []
        for field, order in sort_criteria:
            value = _get_field_value(task, field)

            # Invert value for descending order
            if order == SortOrder.DESC:
                if isinstance(value, (int, float)):
                    value = -value
                elif isinstance(value, datetime):
                    # Use negative timestamp for datetime
                    value = -value.timestamp() if value != datetime.max and value != datetime.min else value
                elif isinstance(value, str):
                    # String inversion is tricky, use reverse comparison
                    # We'll handle this differently
                    pass

            key_parts.append(value)

        return tuple(key_parts)

    sorted_tasks = sorted(tasks, key=multi_field_key)
    return sorted_tasks
