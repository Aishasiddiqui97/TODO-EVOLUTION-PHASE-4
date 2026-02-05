"""
Notification Consolidation Service.

Consolidates multiple simultaneous notifications into a single message
to avoid overwhelming users with multiple alerts.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from ...shared.dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)


class NotificationConsolidator:
    """
    Service for consolidating multiple notifications.

    Groups notifications that occur within a short time window
    to send a single consolidated message instead of multiple alerts.
    """

    def __init__(self, consolidation_window_seconds: int = 60):
        """
        Initialize notification consolidator.

        Args:
            consolidation_window_seconds: Time window for consolidation (default 60 seconds)
        """
        self.dapr_client = DaprClientWrapper()
        self.consolidation_window = timedelta(seconds=consolidation_window_seconds)

    async def check_consolidation(
        self,
        user_id: str,
        task_id: str,
        reminder_time: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if notification should be consolidated with others.

        Args:
            user_id: ID of the user
            task_id: ID of the task
            reminder_time: When the reminder is due (ISO format)

        Returns:
            Tuple of (should_consolidate, list_of_tasks_to_consolidate)
        """
        try:
            # Parse reminder time
            reminder_dt = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))

            # Get pending notifications for user
            pending_key = f"notification.pending.{user_id}"
            pending_notifications = await self.dapr_client.get_state(pending_key) or {"notifications": []}

            # Add current notification to pending list
            current_notification = {
                "taskId": task_id,
                "reminderTime": reminder_time,
                "addedAt": datetime.utcnow().isoformat() + "Z"
            }

            # Filter notifications within consolidation window
            consolidated_tasks = []
            now = datetime.utcnow()

            for notif in pending_notifications.get("notifications", []):
                notif_time = datetime.fromisoformat(notif["reminderTime"].replace("Z", "+00:00"))

                # Check if within consolidation window
                if abs((notif_time - reminder_dt).total_seconds()) <= self.consolidation_window.total_seconds():
                    # Get task details
                    task = await self._get_task_details(user_id, notif["taskId"])
                    if task:
                        consolidated_tasks.append(task)

            # Add current task
            current_task = await self._get_task_details(user_id, task_id)
            if current_task:
                consolidated_tasks.append(current_task)

            # Update pending notifications
            pending_notifications["notifications"].append(current_notification)

            # Clean up old notifications (older than consolidation window)
            pending_notifications["notifications"] = [
                n for n in pending_notifications["notifications"]
                if (now - datetime.fromisoformat(n["addedAt"].replace("Z", "+00:00"))).total_seconds() <= self.consolidation_window.total_seconds() * 2
            ]

            await self.dapr_client.save_state(pending_key, pending_notifications)

            # Determine if consolidation should occur
            should_consolidate = len(consolidated_tasks) > 1

            logger.info(
                f"Consolidation check for user {user_id}: "
                f"{len(consolidated_tasks)} tasks, consolidate={should_consolidate}"
            )

            return should_consolidate, consolidated_tasks

        except Exception as e:
            logger.error(f"Error checking consolidation: {e}", exc_info=True)
            # On error, don't consolidate
            return False, []

    async def mark_as_sent(
        self,
        user_id: str,
        task_ids: List[str]
    ) -> None:
        """
        Mark notifications as sent and remove from pending list.

        Args:
            user_id: ID of the user
            task_ids: List of task IDs that were sent
        """
        try:
            pending_key = f"notification.pending.{user_id}"
            pending_notifications = await self.dapr_client.get_state(pending_key) or {"notifications": []}

            # Remove sent notifications
            pending_notifications["notifications"] = [
                n for n in pending_notifications.get("notifications", [])
                if n["taskId"] not in task_ids
            ]

            await self.dapr_client.save_state(pending_key, pending_notifications)

            logger.info(f"Marked {len(task_ids)} notifications as sent for user {user_id}")

        except Exception as e:
            logger.error(f"Error marking notifications as sent: {e}", exc_info=True)

    async def _get_task_details(
        self,
        user_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Get task details from state store.

        Args:
            user_id: ID of the user
            task_id: ID of the task

        Returns:
            Task details dict or None
        """
        try:
            task_key = f"chat-api.task.user.{user_id}.{task_id}"
            task_data = await self.dapr_client.get_state(task_key)

            if task_data:
                return {
                    "id": task_data.get("id"),
                    "title": task_data.get("title"),
                    "priority": task_data.get("priority"),
                    "dueDate": task_data.get("dueDate"),
                    "dueTime": task_data.get("dueTime")
                }

            return None

        except Exception as e:
            logger.warning(f"Error getting task details: {e}")
            return None

    def get_consolidation_summary(
        self,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a summary message for consolidated notifications.

        Args:
            tasks: List of task details

        Returns:
            Summary message string
        """
        if not tasks:
            return ""

        if len(tasks) == 1:
            return f"Task: {tasks[0]['title']}"

        # Group by priority
        high_priority = [t for t in tasks if t.get("priority") == "high"]
        medium_priority = [t for t in tasks if t.get("priority") == "medium"]
        low_priority = [t for t in tasks if t.get("priority") == "low"]

        summary = f"You have {len(tasks)} tasks due:\n"

        if high_priority:
            summary += f"\nHigh Priority ({len(high_priority)}):\n"
            for task in high_priority[:3]:  # Show max 3
                summary += f"  • {task['title']}\n"
            if len(high_priority) > 3:
                summary += f"  • ...and {len(high_priority) - 3} more\n"

        if medium_priority:
            summary += f"\nMedium Priority ({len(medium_priority)}):\n"
            for task in medium_priority[:3]:
                summary += f"  • {task['title']}\n"
            if len(medium_priority) > 3:
                summary += f"  • ...and {len(medium_priority) - 3} more\n"

        if low_priority:
            summary += f"\nLow Priority ({len(low_priority)}):\n"
            for task in low_priority[:3]:
                summary += f"  • {task['title']}\n"
            if len(low_priority) > 3:
                summary += f"  • ...and {len(low_priority) - 3} more\n"

        return summary
