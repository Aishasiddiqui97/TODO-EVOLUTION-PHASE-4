"""
Tag validation utility for Event-Driven Todo Chatbot.

Provides validation and normalization for task tags.
"""

import re
from typing import List, Set, Optional


class TagValidationError(Exception):
    """Exception raised when tag validation fails."""
    pass


def validate_tag(tag: str) -> bool:
    """
    Validate a single tag.

    Rules:
    - Must be 1-50 characters
    - Can contain letters, numbers, hyphens, underscores
    - Cannot start or end with whitespace
    - Cannot be empty after trimming

    Args:
        tag: Tag string to validate

    Returns:
        True if valid

    Raises:
        TagValidationError: If tag is invalid
    """
    if not tag or not tag.strip():
        raise TagValidationError("Tag cannot be empty")

    tag = tag.strip()

    if len(tag) > 50:
        raise TagValidationError(f"Tag '{tag}' exceeds maximum length of 50 characters")

    if len(tag) < 1:
        raise TagValidationError("Tag must be at least 1 character")

    # Check for valid characters (letters, numbers, hyphens, underscores, spaces)
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
        raise TagValidationError(
            f"Tag '{tag}' contains invalid characters. "
            f"Only letters, numbers, spaces, hyphens, and underscores are allowed"
        )

    return True


def validate_tags(tags: List[str], max_tags: int = 100) -> bool:
    """
    Validate a list of tags.

    Args:
        tags: List of tag strings
        max_tags: Maximum number of tags allowed

    Returns:
        True if all tags are valid

    Raises:
        TagValidationError: If any tag is invalid or limits exceeded
    """
    if not tags:
        return True  # Empty list is valid

    if len(tags) > max_tags:
        raise TagValidationError(f"Too many tags. Maximum {max_tags} tags allowed")

    # Validate each tag
    for tag in tags:
        validate_tag(tag)

    # Check for duplicates (case-insensitive)
    normalized_tags = [normalize_tag(tag) for tag in tags]
    if len(normalized_tags) != len(set(normalized_tags)):
        raise TagValidationError("Duplicate tags are not allowed")

    return True


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag for consistent storage and comparison.

    Normalization:
    - Trim whitespace
    - Convert to lowercase
    - Replace multiple spaces with single space
    - Remove leading/trailing hyphens and underscores

    Args:
        tag: Tag string to normalize

    Returns:
        Normalized tag string
    """
    if not tag:
        return ""

    # Trim whitespace
    tag = tag.strip()

    # Convert to lowercase
    tag = tag.lower()

    # Replace multiple spaces with single space
    tag = re.sub(r'\s+', ' ', tag)

    # Remove leading/trailing hyphens and underscores
    tag = tag.strip('-_')

    return tag


def normalize_tags(tags: List[str]) -> List[str]:
    """
    Normalize a list of tags and remove duplicates.

    Args:
        tags: List of tag strings

    Returns:
        List of normalized, unique tags
    """
    if not tags:
        return []

    # Normalize each tag
    normalized = [normalize_tag(tag) for tag in tags if tag and tag.strip()]

    # Remove duplicates while preserving order
    seen: Set[str] = set()
    unique_tags = []
    for tag in normalized:
        if tag and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags


def filter_tasks_by_tags(
    tasks: List[dict],
    filter_tags: List[str],
    match_all: bool = False
) -> List[dict]:
    """
    Filter tasks by tags.

    Args:
        tasks: List of task dictionaries
        filter_tags: Tags to filter by
        match_all: If True, task must have all filter tags. If False, any match is sufficient.

    Returns:
        Filtered list of tasks
    """
    if not filter_tags:
        return tasks

    # Normalize filter tags
    normalized_filter_tags = [normalize_tag(tag) for tag in filter_tags]

    filtered_tasks = []
    for task in tasks:
        task_tags = task.get("tags", [])
        normalized_task_tags = [normalize_tag(tag) for tag in task_tags]

        if match_all:
            # Task must have all filter tags
            if all(filter_tag in normalized_task_tags for filter_tag in normalized_filter_tags):
                filtered_tasks.append(task)
        else:
            # Task must have at least one filter tag
            if any(filter_tag in normalized_task_tags for filter_tag in normalized_filter_tags):
                filtered_tasks.append(task)

    return filtered_tasks


def get_all_tags(tasks: List[dict]) -> List[str]:
    """
    Extract all unique tags from a list of tasks.

    Args:
        tasks: List of task dictionaries

    Returns:
        Sorted list of unique tags
    """
    all_tags: Set[str] = set()

    for task in tasks:
        task_tags = task.get("tags", [])
        for tag in task_tags:
            normalized = normalize_tag(tag)
            if normalized:
                all_tags.add(normalized)

    return sorted(list(all_tags))


def suggest_tags(partial_tag: str, existing_tags: List[str], limit: int = 10) -> List[str]:
    """
    Suggest tags based on partial input.

    Args:
        partial_tag: Partial tag string to match
        existing_tags: List of existing tags to search
        limit: Maximum number of suggestions

    Returns:
        List of suggested tags
    """
    if not partial_tag:
        return []

    partial_normalized = normalize_tag(partial_tag)
    suggestions = []

    for tag in existing_tags:
        normalized = normalize_tag(tag)
        if normalized.startswith(partial_normalized):
            suggestions.append(tag)
            if len(suggestions) >= limit:
                break

    return suggestions


def format_tags_display(tags: List[str]) -> str:
    """
    Format tags for display.

    Args:
        tags: List of tags

    Returns:
        Formatted string (e.g., "#work #urgent #review")
    """
    if not tags:
        return ""

    return " ".join(f"#{tag}" for tag in tags)
