"""
Create task intent handler for Phase III User Story 1.
Handles natural language task creation requests.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..date_parser import extract_date_from_text
from ..error_handler import handle_error, ErrorCode

logger = logging.getLogger(__name__)


class CreateTaskIntent:
    """
    Intent handler for creating tasks from natural language.

    Extracts task details and prepares arguments for add_task MCP tool.
    """

    @staticmethod
    async def handle(
        user_message: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Handle create task intent.

        Args:
            user_message: User's natural language message
            user_id: ID of the user

        Returns:
            Dictionary with tool call information
        """
        try:
            # Extract task title (basic extraction - AI agent does better)
            title = CreateTaskIntent._extract_title(user_message)

            if not title:
                return {
                    "tool": "add_task",
                    "arguments": {},
                    "needs_clarification": True,
                    "clarification": "What would you like to name this task?"
                }

            # Extract due date from message
            due_date = extract_date_from_text(user_message)

            # Prepare tool arguments
            arguments = {
                "title": title,
                "user_id": user_id
            }

            if due_date:
                arguments["due_date"] = due_date.isoformat()

            # Extract priority if mentioned
            priority = CreateTaskIntent._extract_priority(user_message)
            if priority:
                arguments["priority"] = priority

            return {
                "tool": "add_task",
                "arguments": arguments,
                "needs_clarification": False
            }

        except Exception as e:
            logger.error(f"Error handling create task intent: {str(e)}")
            return handle_error(ErrorCode.TOOL_FAILURE)

    @staticmethod
    def _extract_title(text: str) -> Optional[str]:
        """
        Extract task title from natural language text.

        Args:
            text: User's message

        Returns:
            Extracted title or None
        """
        # Remove common prefixes
        prefixes = [
            "add ", "create ", "new task ", "remind me to ",
            "don't forget to ", "i need to ", "todo: "
        ]

        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                return text[len(prefix):].strip()

        # If no prefix found, use the whole text
        return text.strip()

    @staticmethod
    def _extract_priority(text: str) -> Optional[str]:
        """
        Extract priority from text if mentioned.

        Args:
            text: User's message

        Returns:
            Priority level or None
        """
        text_lower = text.lower()

        if any(word in text_lower for word in ["urgent", "important", "high priority", "asap"]):
            return "high"
        elif any(word in text_lower for word in ["medium priority", "normal"]):
            return "medium"
        elif any(word in text_lower for word in ["low priority", "whenever", "someday"]):
            return "low"

        return None
