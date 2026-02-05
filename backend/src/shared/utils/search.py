"""
Full-text search utility for Event-Driven Todo Chatbot.

Provides utilities to search tasks by text content across multiple fields.
"""

from typing import List, Dict, Any, Optional, Set
import re


def normalize_text(text: str) -> str:
    """
    Normalize text for searching (lowercase, remove extra whitespace).

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Trim
    text = text.strip()

    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into searchable terms.

    Args:
        text: Text to tokenize

    Returns:
        List of tokens
    """
    if not text:
        return []

    # Normalize first
    text = normalize_text(text)

    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', text)

    return tokens


def search_tasks_fulltext(
    tasks: List[Dict[str, Any]],
    query: str,
    fields: Optional[List[str]] = None,
    match_all_terms: bool = False
) -> List[Dict[str, Any]]:
    """
    Search tasks using full-text search across specified fields.

    Args:
        tasks: List of task dictionaries
        query: Search query string
        fields: Fields to search in (defaults to title, description, tags)
        match_all_terms: If True, all query terms must match; if False, any term matches

    Returns:
        List of matching tasks with relevance scores
    """
    if not tasks or not query:
        return []

    # Default fields to search
    if fields is None:
        fields = ["title", "description", "tags"]

    # Tokenize query
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Convert to set for faster lookup
    query_token_set = set(query_tokens)

    matching_tasks = []

    for task in tasks:
        # Build searchable text from specified fields
        searchable_text_parts = []

        for field in fields:
            field_value = task.get(field)

            if field_value is None:
                continue

            if isinstance(field_value, str):
                searchable_text_parts.append(field_value)
            elif isinstance(field_value, list):
                # Handle tags and other list fields
                searchable_text_parts.extend(str(item) for item in field_value)

        # Combine all searchable text
        searchable_text = " ".join(searchable_text_parts)

        # Tokenize task text
        task_tokens = tokenize(searchable_text)
        task_token_set = set(task_tokens)

        # Check for matches
        matching_tokens = query_token_set.intersection(task_token_set)

        if match_all_terms:
            # All query tokens must be present
            if len(matching_tokens) == len(query_token_set):
                # Calculate relevance score
                relevance = calculate_relevance(task, query_tokens, task_tokens, fields)
                task_with_score = task.copy()
                task_with_score["_relevance"] = relevance
                matching_tasks.append(task_with_score)
        else:
            # Any query token matches
            if matching_tokens:
                # Calculate relevance score
                relevance = calculate_relevance(task, query_tokens, task_tokens, fields)
                task_with_score = task.copy()
                task_with_score["_relevance"] = relevance
                matching_tasks.append(task_with_score)

    # Sort by relevance (highest first)
    matching_tasks.sort(key=lambda t: t.get("_relevance", 0), reverse=True)

    return matching_tasks


def calculate_relevance(
    task: Dict[str, Any],
    query_tokens: List[str],
    task_tokens: List[str],
    fields: List[str]
) -> float:
    """
    Calculate relevance score for a task based on query match.

    Scoring factors:
    - Number of matching terms
    - Field where match occurs (title > description > tags)
    - Term frequency
    - Exact phrase matches

    Args:
        task: Task dictionary
        query_tokens: Tokenized query
        task_tokens: Tokenized task text
        fields: Fields that were searched

    Returns:
        Relevance score (higher is better)
    """
    score = 0.0

    query_token_set = set(query_tokens)
    task_token_set = set(task_tokens)

    # Base score: number of matching unique terms
    matching_tokens = query_token_set.intersection(task_token_set)
    score += len(matching_tokens) * 10

    # Bonus for matching all query terms
    if len(matching_tokens) == len(query_token_set):
        score += 20

    # Field-specific scoring (title matches are more relevant)
    title = normalize_text(task.get("title", ""))
    description = normalize_text(task.get("description", ""))
    tags = [normalize_text(tag) for tag in task.get("tags", [])]

    for token in matching_tokens:
        # Title matches get highest weight
        if token in title:
            score += 15

        # Description matches get medium weight
        if token in description:
            score += 5

        # Tag matches get high weight (tags are explicit categorization)
        if any(token in tag for tag in tags):
            score += 12

    # Exact phrase match bonus
    query_normalized = normalize_text(" ".join(query_tokens))
    if query_normalized in title:
        score += 50
    elif query_normalized in description:
        score += 25

    # Term frequency bonus (how many times terms appear)
    for token in matching_tokens:
        frequency = task_tokens.count(token)
        score += frequency * 2

    return score


def search_by_prefix(
    tasks: List[Dict[str, Any]],
    prefix: str,
    field: str = "title"
) -> List[Dict[str, Any]]:
    """
    Search tasks where a field starts with the given prefix.

    Args:
        tasks: List of task dictionaries
        prefix: Prefix to search for
        field: Field to search in

    Returns:
        List of matching tasks
    """
    if not tasks or not prefix:
        return []

    prefix_normalized = normalize_text(prefix)
    matching_tasks = []

    for task in tasks:
        field_value = task.get(field)
        if not field_value:
            continue

        if isinstance(field_value, str):
            field_normalized = normalize_text(field_value)
            if field_normalized.startswith(prefix_normalized):
                matching_tasks.append(task)

    return matching_tasks


def search_by_exact_match(
    tasks: List[Dict[str, Any]],
    value: str,
    field: str
) -> List[Dict[str, Any]]:
    """
    Search tasks where a field exactly matches the given value.

    Args:
        tasks: List of task dictionaries
        value: Value to match
        field: Field to search in

    Returns:
        List of matching tasks
    """
    if not tasks:
        return []

    value_normalized = normalize_text(value)
    matching_tasks = []

    for task in tasks:
        field_value = task.get(field)
        if not field_value:
            continue

        if isinstance(field_value, str):
            field_normalized = normalize_text(field_value)
            if field_normalized == value_normalized:
                matching_tasks.append(task)
        elif isinstance(field_value, list):
            # For list fields (like tags), check if value is in list
            normalized_list = [normalize_text(str(item)) for item in field_value]
            if value_normalized in normalized_list:
                matching_tasks.append(task)

    return matching_tasks


def highlight_matches(text: str, query: str, max_length: int = 200) -> str:
    """
    Highlight matching terms in text and return a snippet.

    Args:
        text: Text to highlight
        query: Search query
        max_length: Maximum length of returned snippet

    Returns:
        Text snippet with matches highlighted (using **term** markdown)
    """
    if not text or not query:
        return text[:max_length] if text else ""

    query_tokens = tokenize(query)
    if not query_tokens:
        return text[:max_length]

    # Find first match position
    text_lower = text.lower()
    first_match_pos = len(text)

    for token in query_tokens:
        pos = text_lower.find(token.lower())
        if pos != -1 and pos < first_match_pos:
            first_match_pos = pos

    # Extract snippet around first match
    start = max(0, first_match_pos - 50)
    end = min(len(text), start + max_length)
    snippet = text[start:end]

    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    # Highlight matching terms
    for token in query_tokens:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(token), re.IGNORECASE)
        snippet = pattern.sub(f"**{token}**", snippet)

    return snippet
