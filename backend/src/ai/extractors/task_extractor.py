"""
Task detail extractor for Phase III User Story 1.
Extracts task details (title, description, due date, priority) from natural language.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..date_parser import extract_date_from_text

logger = logging.getLogger(__name__)


class TaskExtractor:
    """
    Extracts structured task details from natural language input.

    Works in conjunction with the AI agent to parse user messages
    and extract task-relevant information.
    """

    @staticmethod
    def extract_task_details(text: str) -> Dict[str, Any]:
        """
        Extract task details from natural language text.

        Args:
            text: User's message

        Returns:
            Dictionary with extracted details:
            - title: Task title
            - description: Optional description
            - due_date: Optional due date
            - priority: Optional priority
        """
        details = {
            "title": TaskExtractor._extract_title(text),
            "description": None,
            "due_date": None,
            "priority": None
        }

        # Extract due date
        due_date = extract_date_from_text(text)
        if due_date:
            details["due_date"] = due_date.isoformat()

        # Extract priority
        priority = TaskExtractor._extract_priority(text)
        if priority:
            details["priority"] = priority

        logger.info(f"Extracted task details from: {text[:50]}...")
        return details

    @staticmethod
    def _extract_title(text: str) -> str:
        """
        Extract task title from text.

        Args:
            text: User's message

        Returns:
            Extracted title
        """
        # Remove common task-related prefixes
        prefixes = [
            "add ", "create ", "new task ", "remind me to ",
            "don't forget to ", "i need to ", "todo: ",
            "task: ", "remember to "
        ]

        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                title = text[len(prefix):].strip()
                # Remove date-related suffixes for cleaner title
                title = TaskExtractor._clean_title(title)
                return title

        # If no prefix, use the whole text
        return TaskExtractor._clean_title(text)

    @staticmethod
    def _clean_title(title: str) -> str:
        """
        Clean up title by removing date references.

        Args:
            title: Raw title text

        Returns:
            Cleaned title
        """
        # Remove common date phrases from end of title
        date_phrases = [
            " tomorrow", " today", " tonight",
            " by friday", " by monday", " by tuesday", " by wednesday",
            " by thursday", " by saturday", " by sunday",
            " next week", " next month",
            " at ", " by "
        ]

        title_lower = title.lower()
        for phrase in date_phrases:
            if phrase in title_lower:
                # Find the phrase and truncate
                idx = title_lower.find(phrase)
                if idx > 0:  # Don't truncate if phrase is at start
                    title = title[:idx].strip()
                    break

        return title

    @staticmethod
    def _extract_priority(text: str) -> Optional[str]:
        """
        Extract priority level from text.

        Args:
            text: User's message

        Returns:
            Priority level ("low", "medium", "high") or None
        """
        text_lower = text.lower()

        # High priority indicators
        if any(word in text_lower for word in [
            "urgent", "important", "critical", "asap",
            "high priority", "immediately", "right away"
        ]):
            return "high"

        # Medium priority indicators
        if any(word in text_lower for word in [
            "medium priority", "normal", "regular"
        ]):
            return "medium"

        # Low priority indicators
        if any(word in text_lower for word in [
            "low priority", "whenever", "someday", "eventually",
            "not urgent", "no rush"
        ]):
            return "low"

        return None

    @staticmethod
    def validate_task_details(details: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate extracted task details.

        Args:
            details: Extracted task details

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not details.get("title"):
            return False, "Task title is required"

        # Validate title length
        title = details["title"]
        if len(title) > 500:
            return False, "Task title is too long (max 500 characters)"

        # Validate priority if provided
        priority = details.get("priority")
        if priority and priority not in ["low", "medium", "high"]:
            return False, f"Invalid priority: {priority}"

        return True, None
