"""
Date range filtering utility for Event-Driven Todo Chatbot.

Provides utilities to filter tasks by date ranges (today, this week, next week, etc.).
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum


class DateRange(str, Enum):
    """Predefined date range types."""
    TODAY = "today"
    TOMORROW = "tomorrow"
    THIS_WEEK = "this_week"
    NEXT_WEEK = "next_week"
    THIS_MONTH = "this_month"
    NEXT_MONTH = "next_month"
    OVERDUE = "overdue"
    UPCOMING = "upcoming"  # Next 7 days


def get_date_range_bounds(range_type: DateRange, reference_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """
    Get start and end datetime bounds for a predefined date range.

    Args:
        range_type: The type of date range
        reference_date: Reference date for calculations (defaults to now)

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    if reference_date is None:
        reference_date = datetime.now()

    # Normalize to start of day
    today_start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    if range_type == DateRange.TODAY:
        return today_start, today_end

    elif range_type == DateRange.TOMORROW:
        tomorrow_start = today_start + timedelta(days=1)
        tomorrow_end = today_end + timedelta(days=1)
        return tomorrow_start, tomorrow_end

    elif range_type == DateRange.THIS_WEEK:
        # Week starts on Monday (0)
        days_since_monday = today_start.weekday()
        week_start = today_start - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return week_start, week_end

    elif range_type == DateRange.NEXT_WEEK:
        days_since_monday = today_start.weekday()
        this_week_start = today_start - timedelta(days=days_since_monday)
        next_week_start = this_week_start + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return next_week_start, next_week_end

    elif range_type == DateRange.THIS_MONTH:
        month_start = today_start.replace(day=1)
        # Get last day of month
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        month_end = next_month - timedelta(seconds=1)
        return month_start, month_end

    elif range_type == DateRange.NEXT_MONTH:
        # Get first day of next month
        if today_start.month == 12:
            next_month_start = today_start.replace(year=today_start.year + 1, month=1, day=1)
        else:
            next_month_start = today_start.replace(month=today_start.month + 1, day=1)

        # Get last day of next month
        if next_month_start.month == 12:
            month_after_next = next_month_start.replace(year=next_month_start.year + 1, month=1)
        else:
            month_after_next = next_month_start.replace(month=next_month_start.month + 1)
        next_month_end = month_after_next - timedelta(seconds=1)
        return next_month_start, next_month_end

    elif range_type == DateRange.OVERDUE:
        # From beginning of time to yesterday end
        past_start = datetime.min
        yesterday_end = today_start - timedelta(seconds=1)
        return past_start, yesterday_end

    elif range_type == DateRange.UPCOMING:
        # Next 7 days from today
        upcoming_start = today_start
        upcoming_end = today_end + timedelta(days=6)
        return upcoming_start, upcoming_end

    else:
        raise ValueError(f"Unknown date range type: {range_type}")


def filter_tasks_by_date_range(
    tasks: List[Dict[str, Any]],
    range_type: Optional[DateRange] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    reference_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter tasks by date range.

    Args:
        tasks: List of task dictionaries
        range_type: Predefined date range type (e.g., "today", "this_week")
        start_date: Custom start date (overrides range_type)
        end_date: Custom end date (overrides range_type)
        reference_date: Reference date for range calculations

    Returns:
        Filtered list of tasks
    """
    if not tasks:
        return []

    # Determine date bounds
    if start_date and end_date:
        # Use custom date range
        range_start = start_date
        range_end = end_date
    elif range_type:
        # Use predefined range
        range_start, range_end = get_date_range_bounds(range_type, reference_date)
    else:
        # No filtering
        return tasks

    filtered_tasks = []

    for task in tasks:
        due_date_str = task.get("dueDate")
        if not due_date_str:
            # Tasks without due dates are not included in date filtering
            continue

        try:
            # Parse due date (ISO 8601 format: YYYY-MM-DD)
            due_date = datetime.fromisoformat(due_date_str)

            # Add time if available
            due_time_str = task.get("dueTime")
            if due_time_str:
                # Parse time (HH:MM format)
                hour, minute = map(int, due_time_str.split(":"))
                due_date = due_date.replace(hour=hour, minute=minute)
            else:
                # Default to end of day if no time specified
                due_date = due_date.replace(hour=23, minute=59, second=59)

            # Check if task falls within range
            if range_start <= due_date <= range_end:
                filtered_tasks.append(task)

        except (ValueError, AttributeError):
            # Skip tasks with invalid date formats
            continue

    return filtered_tasks


def is_task_overdue(task: Dict[str, Any], reference_date: Optional[datetime] = None) -> bool:
    """
    Check if a task is overdue.

    Args:
        task: Task dictionary
        reference_date: Reference date for comparison (defaults to now)

    Returns:
        True if task is overdue, False otherwise
    """
    if reference_date is None:
        reference_date = datetime.now()

    # Only pending tasks can be overdue
    if task.get("status") != "pending":
        return False

    due_date_str = task.get("dueDate")
    if not due_date_str:
        return False

    try:
        due_date = datetime.fromisoformat(due_date_str)

        # Add time if available
        due_time_str = task.get("dueTime")
        if due_time_str:
            hour, minute = map(int, due_time_str.split(":"))
            due_date = due_date.replace(hour=hour, minute=minute)
        else:
            # Default to end of day
            due_date = due_date.replace(hour=23, minute=59, second=59)

        return due_date < reference_date

    except (ValueError, AttributeError):
        return False
