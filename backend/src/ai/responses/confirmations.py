"""
Task creation confirmation messages for Phase III User Story 1.
Provides friendly, conversational confirmations after task creation.

Constitutional Requirements:
- Confirmations MUST be conversational, not robotic
- Confirmations MUST clearly state what action was taken
"""
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskConfirmations:
    """
    Generates friendly confirmation messages for task operations.
    """

    @staticmethod
    def task_created(
        title: str,
        due_date: Optional[datetime] = None,
        priority: Optional[str] = None
    ) -> str:
        """
        Generate confirmation message for task creation.

        Args:
            title: Task title
            due_date: Optional due date
            priority: Optional priority level

        Returns:
            Friendly confirmation message
        """
        message = f"✓ I've added '{title}' to your list"

        # Add due date info if present
        if due_date:
            date_str = TaskConfirmations._format_due_date(due_date)
            message += f" (due {date_str})"

        # Add priority info if present
        if priority:
            message += f" with {priority} priority"

        message += "."

        logger.info(f"Generated task creation confirmation: {title}")
        return message

    @staticmethod
    def task_created_with_clarification(
        title: str,
        clarification_asked: str
    ) -> str:
        """
        Generate confirmation when clarification was needed.

        Args:
            title: Task title
            clarification_asked: What was clarified

        Returns:
            Confirmation message
        """
        return f"✓ I've added '{title}' to your list. {clarification_asked}"

    @staticmethod
    def _format_due_date(due_date: datetime) -> str:
        """
        Format due date in a human-friendly way.

        Args:
            due_date: Due date

        Returns:
            Formatted date string
        """
        now = datetime.utcnow()
        delta = due_date - now

        # Today
        if delta.days == 0:
            if due_date.hour > 0:
                return f"today at {due_date.strftime('%I:%M %p')}"
            return "today"

        # Tomorrow
        if delta.days == 1:
            if due_date.hour > 0:
                return f"tomorrow at {due_date.strftime('%I:%M %p')}"
            return "tomorrow"

        # This week
        if delta.days < 7:
            day_name = due_date.strftime('%A')
            if due_date.hour > 0:
                return f"{day_name} at {due_date.strftime('%I:%M %p')}"
            return day_name

        # Future date
        if due_date.hour > 0:
            return due_date.strftime('%B %d at %I:%M %p')
        return due_date.strftime('%B %d')

    @staticmethod
    def multiple_tasks_created(count: int) -> str:
        """
        Generate confirmation for multiple tasks created.

        Args:
            count: Number of tasks created

        Returns:
            Confirmation message
        """
        return f"✓ I've added {count} tasks to your list."

    @staticmethod
    def task_creation_failed(reason: str) -> str:
        """
        Generate error message for failed task creation.

        Args:
            reason: Reason for failure

        Returns:
            Error message
        """
        return f"I couldn't create that task. {reason}"


# Global instance
confirmations = TaskConfirmations()


def generate_task_created_confirmation(
    title: str,
    due_date: Optional[datetime] = None,
    priority: Optional[str] = None
) -> str:
    """
    Generate confirmation message for task creation.

    Args:
        title: Task title
        due_date: Optional due date
        priority: Optional priority

    Returns:
        Confirmation message
    """
    return confirmations.task_created(title, due_date, priority)
