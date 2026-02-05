"""
Recurrence pattern parser for Event-Driven Todo Chatbot.

Parses natural language recurrence patterns into structured RecurrencePattern objects.
Supports daily, weekly, and custom patterns.
"""

import re
from typing import Optional, List
from datetime import datetime, time
from ..models.recurrence import RecurrencePattern, RecurrenceType


class RecurrenceParserError(Exception):
    """Exception raised when recurrence pattern cannot be parsed."""
    pass


def parse_recurrence_pattern(pattern_text: str) -> RecurrencePattern:
    """
    Parse natural language recurrence pattern into structured format.

    Supported patterns:
    - "daily" / "every day"
    - "weekly" / "every week"
    - "every N days" (e.g., "every 3 days")
    - "every N weeks" (e.g., "every 2 weeks")
    - "every weekday" / "weekdays"
    - "every monday" / "every tuesday" etc.
    - "every monday and wednesday"

    Args:
        pattern_text: Natural language recurrence pattern

    Returns:
        RecurrencePattern object

    Raises:
        RecurrenceParserError: If pattern cannot be parsed
    """
    if not pattern_text or not pattern_text.strip():
        raise RecurrenceParserError("Recurrence pattern cannot be empty")

    pattern_text = pattern_text.lower().strip()

    # Daily patterns
    if pattern_text in ["daily", "every day", "everyday"]:
        return RecurrencePattern(
            type=RecurrenceType.DAILY,
            interval=1
        )

    # Weekday pattern
    if pattern_text in ["weekdays", "every weekday", "weekday"]:
        return RecurrencePattern(
            type=RecurrenceType.WEEKLY,
            interval=1,
            daysOfWeek=["monday", "tuesday", "wednesday", "thursday", "friday"]
        )

    # Weekly patterns
    if pattern_text in ["weekly", "every week"]:
        return RecurrencePattern(
            type=RecurrenceType.WEEKLY,
            interval=1
        )

    # Every N days
    match = re.match(r"every (\d+) days?", pattern_text)
    if match:
        interval = int(match.group(1))
        if interval <= 0:
            raise RecurrenceParserError("Interval must be greater than 0")
        return RecurrencePattern(
            type=RecurrenceType.DAILY,
            interval=interval
        )

    # Every N weeks
    match = re.match(r"every (\d+) weeks?", pattern_text)
    if match:
        interval = int(match.group(1))
        if interval <= 0:
            raise RecurrenceParserError("Interval must be greater than 0")
        return RecurrencePattern(
            type=RecurrenceType.WEEKLY,
            interval=interval
        )

    # Specific days of week
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # Single day: "every monday"
    for day in days_of_week:
        if pattern_text in [f"every {day}", day]:
            return RecurrencePattern(
                type=RecurrenceType.WEEKLY,
                interval=1,
                daysOfWeek=[day]
            )

    # Multiple days: "every monday and wednesday"
    if " and " in pattern_text or "," in pattern_text:
        # Extract day names from pattern
        found_days = []
        for day in days_of_week:
            if day in pattern_text:
                found_days.append(day)

        if found_days:
            return RecurrencePattern(
                type=RecurrenceType.WEEKLY,
                interval=1,
                daysOfWeek=found_days
            )

    # If no pattern matched, raise error
    raise RecurrenceParserError(
        f"Could not parse recurrence pattern: '{pattern_text}'. "
        f"Supported patterns: daily, weekly, every N days, every N weeks, "
        f"weekdays, specific days (e.g., 'every monday')"
    )


def parse_time_from_text(time_text: str) -> Optional[time]:
    """
    Parse time from natural language text.

    Supported formats:
    - "9am" / "9 am"
    - "9:30am" / "9:30 am"
    - "14:00" / "2:00pm"

    Args:
        time_text: Natural language time text

    Returns:
        time object or None if cannot parse
    """
    if not time_text or not time_text.strip():
        return None

    time_text = time_text.lower().strip()

    # Try parsing "9am" or "9:30am" format
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        meridiem = match.group(3)

        # Convert to 24-hour format if am/pm specified
        if meridiem:
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0

        # Validate time
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour=hour, minute=minute)

    return None


def validate_recurrence_pattern(pattern: RecurrencePattern) -> bool:
    """
    Validate that a recurrence pattern is valid.

    Args:
        pattern: RecurrencePattern to validate

    Returns:
        True if valid

    Raises:
        RecurrenceParserError: If pattern is invalid
    """
    if pattern.interval <= 0:
        raise RecurrenceParserError("Interval must be greater than 0")

    if pattern.type == RecurrenceType.WEEKLY and pattern.daysOfWeek:
        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in pattern.daysOfWeek:
            if day.lower() not in valid_days:
                raise RecurrenceParserError(f"Invalid day of week: {day}")

    if pattern.endDate and pattern.endDate < datetime.utcnow():
        raise RecurrenceParserError("End date cannot be in the past")

    return True
