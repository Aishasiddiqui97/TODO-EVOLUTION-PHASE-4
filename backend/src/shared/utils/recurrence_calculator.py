"""
Next occurrence calculator for recurring tasks.

Calculates when the next instance of a recurring task should be created
based on the recurrence pattern and current completion time.
"""

from datetime import datetime, timedelta, time
from typing import Optional
import pytz
from ..models.recurrence import RecurrencePattern, RecurrenceType, EndConditionType


class RecurrenceCalculatorError(Exception):
    """Exception raised when next occurrence cannot be calculated."""
    pass


def calculate_next_occurrence(
    current_due_date: datetime,
    pattern: RecurrencePattern,
    completion_time: Optional[datetime] = None
) -> Optional[datetime]:
    """
    Calculate the next occurrence date for a recurring task.

    Args:
        current_due_date: Due date of the current task instance
        pattern: Recurrence pattern defining the schedule
        completion_time: When the task was completed (defaults to now)

    Returns:
        Next occurrence datetime, or None if recurrence should end

    Raises:
        RecurrenceCalculatorError: If calculation fails
    """
    if not pattern:
        raise RecurrenceCalculatorError("Recurrence pattern is required")

    if completion_time is None:
        completion_time = datetime.utcnow()

    # Get timezone
    try:
        tz = pytz.timezone(pattern.timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.UTC

    # Ensure dates are timezone-aware
    if current_due_date.tzinfo is None:
        current_due_date = tz.localize(current_due_date)
    if completion_time.tzinfo is None:
        completion_time = tz.localize(completion_time)

    # Calculate next occurrence based on pattern type
    if pattern.type == RecurrenceType.DAILY:
        next_date = _calculate_next_daily(current_due_date, pattern)
    elif pattern.type == RecurrenceType.WEEKLY:
        next_date = _calculate_next_weekly(current_due_date, pattern)
    else:
        raise RecurrenceCalculatorError(f"Unsupported recurrence type: {pattern.type}")

    # Check end conditions
    if pattern.endCondition:
        if pattern.endCondition.type == EndConditionType.END_DATE:
            if pattern.endCondition.endDate:
                end_date = datetime.fromisoformat(pattern.endCondition.endDate)
                if end_date.tzinfo is None:
                    end_date = tz.localize(end_date)
                if next_date > end_date:
                    return None  # Recurrence has ended

        elif pattern.endCondition.type == EndConditionType.MAX_OCCURRENCES:
            # Note: This check requires tracking occurrence count externally
            # The caller should maintain a count and stop creating instances
            # when maxOccurrences is reached
            pass

    return next_date


def _calculate_next_daily(
    current_due_date: datetime,
    pattern: RecurrencePattern
) -> datetime:
    """
    Calculate next occurrence for daily recurrence pattern.

    Args:
        current_due_date: Current task due date
        pattern: Recurrence pattern with interval

    Returns:
        Next occurrence datetime
    """
    # Add interval days to current due date
    next_date = current_due_date + timedelta(days=pattern.interval)
    return next_date


def _calculate_next_weekly(
    current_due_date: datetime,
    pattern: RecurrencePattern
) -> datetime:
    """
    Calculate next occurrence for weekly recurrence pattern.

    Args:
        current_due_date: Current task due date
        pattern: Recurrence pattern with interval and optional days of week

    Returns:
        Next occurrence datetime
    """
    if not pattern.daysOfWeek:
        # Simple weekly recurrence (every N weeks on same day)
        next_date = current_due_date + timedelta(weeks=pattern.interval)
        return next_date

    # Complex weekly recurrence with specific days
    # Find the next occurrence on one of the specified days
    day_name_to_number = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    # Convert day names to weekday numbers
    target_weekdays = []
    for day_name in pattern.daysOfWeek:
        day_num = day_name_to_number.get(day_name.lower())
        if day_num is not None:
            target_weekdays.append(day_num)

    if not target_weekdays:
        raise RecurrenceCalculatorError("No valid days of week specified")

    target_weekdays.sort()

    # Start from the day after current due date
    next_date = current_due_date + timedelta(days=1)
    current_weekday = next_date.weekday()

    # Find the next target weekday
    days_ahead = None
    for target_day in target_weekdays:
        if target_day >= current_weekday:
            days_ahead = target_day - current_weekday
            break

    # If no target day found in current week, go to first target day of next week
    if days_ahead is None:
        days_ahead = (7 - current_weekday) + target_weekdays[0]

    next_date = next_date + timedelta(days=days_ahead)

    # Preserve the time from original due date
    next_date = next_date.replace(
        hour=current_due_date.hour,
        minute=current_due_date.minute,
        second=current_due_date.second,
        microsecond=current_due_date.microsecond
    )

    return next_date


def should_create_next_instance(
    pattern: RecurrencePattern,
    occurrence_count: int
) -> bool:
    """
    Check if next instance should be created based on end conditions.

    Args:
        pattern: Recurrence pattern with end conditions
        occurrence_count: Number of instances created so far

    Returns:
        True if next instance should be created, False otherwise
    """
    if not pattern.endCondition:
        return True  # No end condition, continue indefinitely

    if pattern.endCondition.type == EndConditionType.MAX_OCCURRENCES:
        if pattern.endCondition.maxOccurrences:
            return occurrence_count < pattern.endCondition.maxOccurrences

    return True


def format_next_occurrence_message(
    next_date: datetime,
    pattern: RecurrencePattern
) -> str:
    """
    Format a human-readable message about the next occurrence.

    Args:
        next_date: Next occurrence datetime
        pattern: Recurrence pattern

    Returns:
        Human-readable message
    """
    # Get timezone
    try:
        tz = pytz.timezone(pattern.timezone)
        next_date_local = next_date.astimezone(tz)
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        next_date_local = next_date

    date_str = next_date_local.strftime("%Y-%m-%d %H:%M %Z")

    if pattern.type == RecurrenceType.DAILY:
        if pattern.interval == 1:
            pattern_str = "daily"
        else:
            pattern_str = f"every {pattern.interval} days"
    elif pattern.type == RecurrenceType.WEEKLY:
        if pattern.daysOfWeek:
            days_str = ", ".join(pattern.daysOfWeek)
            pattern_str = f"every {days_str}"
        elif pattern.interval == 1:
            pattern_str = "weekly"
        else:
            pattern_str = f"every {pattern.interval} weeks"
    else:
        pattern_str = "recurring"

    return f"Next occurrence ({pattern_str}): {date_str}"


def get_recurrence_summary(pattern: RecurrencePattern) -> str:
    """
    Get a human-readable summary of the recurrence pattern.

    Args:
        pattern: Recurrence pattern

    Returns:
        Human-readable summary
    """
    if pattern.type == RecurrenceType.DAILY:
        if pattern.interval == 1:
            summary = "Repeats daily"
        else:
            summary = f"Repeats every {pattern.interval} days"
    elif pattern.type == RecurrenceType.WEEKLY:
        if pattern.daysOfWeek:
            days_str = ", ".join(d.capitalize() for d in pattern.daysOfWeek)
            summary = f"Repeats every {days_str}"
        elif pattern.interval == 1:
            summary = "Repeats weekly"
        else:
            summary = f"Repeats every {pattern.interval} weeks"
    else:
        summary = "Recurring task"

    # Add end condition info
    if pattern.endCondition:
        if pattern.endCondition.type == EndConditionType.END_DATE and pattern.endCondition.endDate:
            end_date = datetime.fromisoformat(pattern.endCondition.endDate)
            summary += f" until {end_date.strftime('%Y-%m-%d')}"
        elif pattern.endCondition.type == EndConditionType.MAX_OCCURRENCES and pattern.endCondition.maxOccurrences:
            summary += f" for {pattern.endCondition.maxOccurrences} occurrences"

    return summary
