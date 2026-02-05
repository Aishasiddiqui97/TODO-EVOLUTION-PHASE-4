"""
Complex query parser for Event-Driven Todo Chatbot.

Parses natural language queries into structured search criteria.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from .date_filters import DateRange
from .sorter import SortField, SortOrder


class QueryCriteria(Dict[str, Any]):
    """
    Structured query criteria extracted from natural language.

    Fields:
        text_query: Full-text search query
        status: Task status filter (pending, completed)
        priority: Priority filter (high, medium, low)
        tags: List of tags to filter by
        match_all_tags: Whether all tags must match (AND) or any (OR)
        date_range: Predefined date range (today, this_week, etc.)
        start_date: Custom start date
        end_date: Custom end date
        include_overdue: Include overdue tasks
        sort_by: Field to sort by
        sort_order: Sort order (asc, desc)
        limit: Maximum number of results
    """
    pass


def parse_query(query: str) -> QueryCriteria:
    """
    Parse natural language query into structured criteria.

    Examples:
        "Show me high-priority tasks tagged with work that are due this week"
        "Find completed tasks from last month"
        "Search for tasks containing 'meeting' due today"
        "List all overdue high-priority tasks"

    Args:
        query: Natural language query string

    Returns:
        QueryCriteria with extracted filters
    """
    criteria = QueryCriteria()

    query_lower = query.lower()

    # Extract status
    criteria["status"] = _extract_status(query_lower)

    # Extract priority
    criteria["priority"] = _extract_priority(query_lower)

    # Extract tags
    criteria["tags"], criteria["match_all_tags"] = _extract_tags(query_lower)

    # Extract date range
    criteria["date_range"] = _extract_date_range(query_lower)
    criteria["include_overdue"] = _extract_overdue_flag(query_lower)

    # Extract sort preferences
    criteria["sort_by"], criteria["sort_order"] = _extract_sort(query_lower)

    # Extract limit
    criteria["limit"] = _extract_limit(query_lower)

    # Extract remaining text as full-text search query
    criteria["text_query"] = _extract_text_query(query, criteria)

    return criteria


def _extract_status(query: str) -> Optional[str]:
    """Extract status filter from query."""
    if re.search(r'\b(completed|done|finished)\b', query):
        return "completed"
    elif re.search(r'\b(pending|active|incomplete|todo|open)\b', query):
        return "pending"
    return None


def _extract_priority(query: str) -> Optional[str]:
    """Extract priority filter from query."""
    if re.search(r'\b(high|urgent|important|critical)[\s-]?priority\b', query):
        return "high"
    elif re.search(r'\bhigh[\s-]?priority\b', query):
        return "high"
    elif re.search(r'\b(medium|normal)[\s-]?priority\b', query):
        return "medium"
    elif re.search(r'\b(low|minor)[\s-]?priority\b', query):
        return "low"

    # Check for standalone priority words
    if re.search(r'\b(urgent|critical|important)\b', query):
        return "high"

    return None


def _extract_tags(query: str) -> tuple[List[str], bool]:
    """
    Extract tags from query.

    Returns:
        Tuple of (tags_list, match_all_tags)
    """
    tags = []
    match_all = False

    # Pattern: "tagged with X", "tag X", "tags X and Y"
    tag_patterns = [
        r'tagged?\s+(?:with\s+)?([a-zA-Z0-9\s,\-_]+?)(?:\s+(?:and|that|due|from|in|on|by)\b|$)',
        r'tags?\s+([a-zA-Z0-9\s,\-_]+?)(?:\s+(?:and|that|due|from|in|on|by)\b|$)',
        r'with\s+tags?\s+([a-zA-Z0-9\s,\-_]+?)(?:\s+(?:and|that|due|from|in|on|by)\b|$)',
    ]

    for pattern in tag_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            tag_text = match.group(1).strip()

            # Split on commas or "and"
            tag_parts = re.split(r'\s*,\s*|\s+and\s+', tag_text)

            for tag in tag_parts:
                tag = tag.strip()
                if tag and len(tag) <= 50:  # Validate tag length
                    tags.append(tag)

            # Check if "and" is used (implies match all)
            if ' and ' in tag_text.lower():
                match_all = True

            break

    return tags, match_all


def _extract_date_range(query: str) -> Optional[DateRange]:
    """Extract date range from query."""
    # Check for predefined ranges
    if re.search(r'\btoday\b', query):
        return DateRange.TODAY
    elif re.search(r'\btomorrow\b', query):
        return DateRange.TOMORROW
    elif re.search(r'\bthis\s+week\b', query):
        return DateRange.THIS_WEEK
    elif re.search(r'\bnext\s+week\b', query):
        return DateRange.NEXT_WEEK
    elif re.search(r'\bthis\s+month\b', query):
        return DateRange.THIS_MONTH
    elif re.search(r'\bnext\s+month\b', query):
        return DateRange.NEXT_MONTH
    elif re.search(r'\bupcoming\b', query):
        return DateRange.UPCOMING

    return None


def _extract_overdue_flag(query: str) -> bool:
    """Check if query requests overdue tasks."""
    return bool(re.search(r'\b(overdue|late|past\s+due)\b', query))


def _extract_sort(query: str) -> tuple[Optional[SortField], SortOrder]:
    """
    Extract sort preferences from query.

    Returns:
        Tuple of (sort_field, sort_order)
    """
    sort_field = None
    sort_order = SortOrder.DESC

    # Check for sort field
    if re.search(r'\bsort(?:ed)?\s+by\s+priority\b', query):
        sort_field = SortField.PRIORITY
    elif re.search(r'\bsort(?:ed)?\s+by\s+due\s+date\b', query):
        sort_field = SortField.DUE_DATE
    elif re.search(r'\bsort(?:ed)?\s+by\s+date\b', query):
        sort_field = SortField.DUE_DATE
    elif re.search(r'\bsort(?:ed)?\s+by\s+created\b', query):
        sort_field = SortField.CREATED_AT
    elif re.search(r'\bsort(?:ed)?\s+by\s+title\b', query):
        sort_field = SortField.TITLE

    # Check for sort order
    if re.search(r'\b(ascending|asc|oldest\s+first|earliest\s+first)\b', query):
        sort_order = SortOrder.ASC
    elif re.search(r'\b(descending|desc|newest\s+first|latest\s+first)\b', query):
        sort_order = SortOrder.DESC

    return sort_field, sort_order


def _extract_limit(query: str) -> Optional[int]:
    """Extract result limit from query."""
    # Pattern: "first N", "top N", "limit N"
    patterns = [
        r'\b(?:first|top)\s+(\d+)\b',
        r'\blimit\s+(\d+)\b',
        r'\b(\d+)\s+(?:tasks?|results?)\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            limit = int(match.group(1))
            # Cap at reasonable maximum
            return min(limit, 1000)

    return None


def _extract_text_query(original_query: str, criteria: QueryCriteria) -> Optional[str]:
    """
    Extract remaining text as full-text search query after removing filter keywords.

    Args:
        original_query: Original query string
        criteria: Extracted criteria

    Returns:
        Cleaned text query for full-text search
    """
    query = original_query.lower()

    # Remove common command words
    command_words = [
        r'\b(show|find|search|list|get|display|give)\s+(me\s+)?',
        r'\b(all|any)\s+',
        r'\btasks?\b',
        r'\bresults?\b',
    ]

    for pattern in command_words:
        query = re.sub(pattern, ' ', query, flags=re.IGNORECASE)

    # Remove extracted filters
    if criteria.get("status"):
        query = re.sub(r'\b(completed|done|finished|pending|active|incomplete|todo|open)\b', ' ', query)

    if criteria.get("priority"):
        query = re.sub(r'\b(high|medium|low|urgent|important|critical|normal|minor)[\s-]?priority\b', ' ', query)
        query = re.sub(r'\b(urgent|critical|important)\b', ' ', query)

    if criteria.get("tags"):
        for tag in criteria["tags"]:
            query = re.sub(re.escape(tag.lower()), ' ', query)
        query = re.sub(r'\btagged?\s+(?:with\s+)?', ' ', query)
        query = re.sub(r'\btags?\s+', ' ', query)

    if criteria.get("date_range"):
        date_keywords = [
            r'\btoday\b', r'\btomorrow\b', r'\bthis\s+week\b', r'\bnext\s+week\b',
            r'\bthis\s+month\b', r'\bnext\s+month\b', r'\bupcoming\b',
            r'\bdue\b', r'\bfrom\b', r'\bin\b', r'\bon\b', r'\bby\b'
        ]
        for pattern in date_keywords:
            query = re.sub(pattern, ' ', query)

    if criteria.get("include_overdue"):
        query = re.sub(r'\b(overdue|late|past\s+due)\b', ' ', query)

    if criteria.get("sort_by"):
        query = re.sub(r'\bsort(?:ed)?\s+by\s+\w+\b', ' ', query)

    if criteria.get("limit"):
        query = re.sub(r'\b(?:first|top|limit)\s+\d+\b', ' ', query)
        query = re.sub(r'\b\d+\s+(?:tasks?|results?)\b', ' ', query)

    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()

    # Remove common filler words
    filler_words = ['that', 'are', 'is', 'the', 'a', 'an', 'with', 'for', 'to', 'of']
    query_words = query.split()
    query_words = [w for w in query_words if w not in filler_words]
    query = ' '.join(query_words)

    return query if query else None


def build_filter_summary(criteria: QueryCriteria) -> str:
    """
    Build human-readable summary of applied filters.

    Args:
        criteria: Query criteria

    Returns:
        Summary string
    """
    parts = []

    if criteria.get("status"):
        parts.append(f"status: {criteria['status']}")

    if criteria.get("priority"):
        parts.append(f"priority: {criteria['priority']}")

    if criteria.get("tags"):
        tag_str = ", ".join(criteria["tags"])
        match_type = "all" if criteria.get("match_all_tags") else "any"
        parts.append(f"tags ({match_type}): {tag_str}")

    if criteria.get("date_range"):
        parts.append(f"due: {criteria['date_range']}")

    if criteria.get("include_overdue"):
        parts.append("including overdue")

    if criteria.get("text_query"):
        parts.append(f"containing: '{criteria['text_query']}'")

    if criteria.get("sort_by"):
        parts.append(f"sorted by: {criteria['sort_by']} ({criteria.get('sort_order', 'desc')})")

    if criteria.get("limit"):
        parts.append(f"limit: {criteria['limit']}")

    return " | ".join(parts) if parts else "no filters"
