"""
Input validation utilities for MCP tools.

Provides additional validation beyond Pydantic models.
"""

from typing import Optional, List
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_user_id(user_id: str) -> None:
    """
    Validate user ID format.

    Args:
        user_id: User ID to validate

    Raises:
        ValidationError: If user ID is invalid
    """
    if not user_id or not user_id.strip():
        raise ValidationError("User ID cannot be empty")

    if len(user_id) > 100:
        raise ValidationError("User ID too long (max 100 characters)")

    # Allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\-_]+$', user_id):
        raise ValidationError("User ID contains invalid characters")


def validate_task_id(task_id: str) -> None:
    """
    Validate task ID format.

    Args:
        task_id: Task ID to validate

    Raises:
        ValidationError: If task ID is invalid
    """
    if not task_id or not task_id.strip():
        raise ValidationError("Task ID cannot be empty")

    if len(task_id) > 100:
        raise ValidationError("Task ID too long (max 100 characters)")

    # Allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9\-_]+$', task_id):
        raise ValidationError("Task ID contains invalid characters")


def validate_title(title: str) -> None:
    """
    Validate task title.

    Args:
        title: Task title to validate

    Raises:
        ValidationError: If title is invalid
    """
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    if len(title) > 500:
        raise ValidationError("Title too long (max 500 characters)")

    # Check for suspicious patterns (potential XSS)
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick='
    ]

    title_lower = title.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, title_lower):
            raise ValidationError("Title contains potentially unsafe content")


def validate_description(description: Optional[str]) -> None:
    """
    Validate task description.

    Args:
        description: Task description to validate

    Raises:
        ValidationError: If description is invalid
    """
    if description is None:
        return

    if len(description) > 5000:
        raise ValidationError("Description too long (max 5000 characters)")


def validate_priority(priority: str) -> None:
    """
    Validate task priority.

    Args:
        priority: Priority to validate

    Raises:
        ValidationError: If priority is invalid
    """
    valid_priorities = ["high", "medium", "low"]
    if priority not in valid_priorities:
        raise ValidationError(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")


def validate_status(status: str) -> None:
    """
    Validate task status.

    Args:
        status: Status to validate

    Raises:
        ValidationError: If status is invalid
    """
    valid_statuses = ["pending", "completed"]
    if status not in valid_statuses:
        raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")


def validate_date(date_str: str) -> None:
    """
    Validate date format (ISO 8601: YYYY-MM-DD).

    Args:
        date_str: Date string to validate

    Raises:
        ValidationError: If date is invalid
    """
    if not date_str:
        return

    try:
        datetime.fromisoformat(date_str)
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD")

    # Check if date is not too far in the past or future
    date = datetime.fromisoformat(date_str)
    now = datetime.now()

    # Allow dates up to 10 years in the past or future
    min_date = datetime(now.year - 10, 1, 1)
    max_date = datetime(now.year + 10, 12, 31)

    if date < min_date or date > max_date:
        raise ValidationError("Date must be within 10 years of current date")


def validate_time(time_str: str) -> None:
    """
    Validate time format (HH:MM).

    Args:
        time_str: Time string to validate

    Raises:
        ValidationError: If time is invalid
    """
    if not time_str:
        return

    if not re.match(r'^\d{2}:\d{2}$', time_str):
        raise ValidationError("Invalid time format. Use HH:MM")

    try:
        hour, minute = map(int, time_str.split(':'))
        if hour < 0 or hour > 23:
            raise ValidationError("Hour must be between 00 and 23")
        if minute < 0 or minute > 59:
            raise ValidationError("Minute must be between 00 and 59")
    except ValueError:
        raise ValidationError("Invalid time format. Use HH:MM")


def validate_tags(tags: List[str]) -> None:
    """
    Validate task tags.

    Args:
        tags: List of tags to validate

    Raises:
        ValidationError: If tags are invalid
    """
    if not tags:
        return

    if len(tags) > 100:
        raise ValidationError("Too many tags (max 100)")

    for tag in tags:
        if not tag or not tag.strip():
            raise ValidationError("Tag cannot be empty")

        if len(tag) > 50:
            raise ValidationError(f"Tag too long: '{tag}' (max 50 characters)")

        # Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
            raise ValidationError(f"Tag contains invalid characters: '{tag}'")


def validate_email(email: str) -> None:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        return

    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Invalid email address format")

    if len(email) > 254:
        raise ValidationError("Email address too long (max 254 characters)")


def sanitize_string(value: str) -> str:
    """
    Sanitize string input by removing potentially dangerous characters.

    Args:
        value: String to sanitize

    Returns:
        Sanitized string
    """
    if not value:
        return value

    # Remove null bytes
    value = value.replace('\x00', '')

    # Remove control characters except newlines and tabs
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')

    return value.strip()


def validate_limit(limit: int, max_limit: int = 1000) -> None:
    """
    Validate pagination limit.

    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit

    Raises:
        ValidationError: If limit is invalid
    """
    if limit < 1:
        raise ValidationError("Limit must be at least 1")

    if limit > max_limit:
        raise ValidationError(f"Limit too large (max {max_limit})")


def validate_offset(offset: int) -> None:
    """
    Validate pagination offset.

    Args:
        offset: Offset value to validate

    Raises:
        ValidationError: If offset is invalid
    """
    if offset < 0:
        raise ValidationError("Offset cannot be negative")
