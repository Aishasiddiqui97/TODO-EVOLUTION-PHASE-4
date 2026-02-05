"""
In-App Notification Sender for Notification Service.

Sends in-app notifications by publishing events that can be consumed
by WebSocket Sync Service or frontend applications.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ...shared.events.publisher import EventPublisher
from ...shared.dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)


class InAppNotifier:
    """
    Service for sending in-app notifications.

    Publishes notification events that can be consumed by:
    - WebSocket Sync Service (for real-time push)
    - Frontend applications (for notification display)
    """

    def __init__(self):
        """Initialize in-app notifier."""
        self.event_publisher = EventPublisher("notification")
        self.dapr_client = DaprClientWrapper()

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        task_id: str,
        reminder_type: str
    ) -> Dict[str, Any]:
        """
        Send an in-app notification.

        Args:
            user_id: ID of the user
            title: Notification title
            body: Notification body text
            task_id: ID of the related task
            reminder_type: Type of reminder (advance/due)

        Returns:
            Dict with success status
        """
        try:
            notification_id = f"notif-{task_id}-{reminder_type}"
            now = datetime.utcnow().isoformat() + "Z"

            # Create notification data
            notification = {
                "id": notification_id,
                "userId": user_id,
                "title": title,
                "body": body,
                "taskId": task_id,
                "type": "task_reminder",
                "reminderType": reminder_type,
                "read": False,
                "createdAt": now
            }

            # Save notification to state store for retrieval
            state_key = f"notification.inapp.{user_id}.{notification_id}"
            await self.dapr_client.save_state(state_key, notification)

            # Add to user's notification index
            index_key = f"notification.inapp.index.{user_id}"
            notification_index = await self.dapr_client.get_state(index_key) or {"notificationIds": []}

            if notification_id not in notification_index["notificationIds"]:
                notification_index["notificationIds"].insert(0, notification_id)  # Most recent first
                # Keep only last 100 notifications
                notification_index["notificationIds"] = notification_index["notificationIds"][:100]
                await self.dapr_client.save_state(index_key, notification_index)

            # Publish notification event for real-time delivery
            await self.event_publisher.publish(
                topic="notification-events",
                event_type="notification.created",
                user_id=user_id,
                payload={
                    "notification": notification,
                    "channel": "in-app"
                }
            )

            logger.info(f"In-app notification sent: {notification_id}")

            return {
                "success": True,
                "notificationId": notification_id,
                "message": "In-app notification sent successfully"
            }

        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to send in-app notification: {str(e)}"
            }

    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str
    ) -> Dict[str, Any]:
        """
        Mark a notification as read.

        Args:
            user_id: ID of the user
            notification_id: ID of the notification

        Returns:
            Dict with success status
        """
        try:
            state_key = f"notification.inapp.{user_id}.{notification_id}"
            notification = await self.dapr_client.get_state(state_key)

            if not notification:
                return {
                    "success": False,
                    "message": "Notification not found"
                }

            notification["read"] = True
            notification["readAt"] = datetime.utcnow().isoformat() + "Z"

            await self.dapr_client.save_state(state_key, notification)

            logger.info(f"Marked notification as read: {notification_id}")

            return {
                "success": True,
                "message": "Notification marked as read"
            }

        except Exception as e:
            logger.error(f"Error marking notification as read: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to mark notification as read: {str(e)}"
            }

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get notifications for a user.

        Args:
            user_id: ID of the user
            unread_only: If True, return only unread notifications
            limit: Maximum number of notifications to return

        Returns:
            Dict with notifications list
        """
        try:
            index_key = f"notification.inapp.index.{user_id}"
            notification_index = await self.dapr_client.get_state(index_key)

            if not notification_index:
                return {
                    "success": True,
                    "notifications": [],
                    "count": 0
                }

            notification_ids = notification_index.get("notificationIds", [])[:limit]
            notifications = []

            for notif_id in notification_ids:
                state_key = f"notification.inapp.{user_id}.{notif_id}"
                notification = await self.dapr_client.get_state(state_key)

                if notification:
                    if unread_only and notification.get("read", False):
                        continue
                    notifications.append(notification)

            return {
                "success": True,
                "notifications": notifications,
                "count": len(notifications)
            }

        except Exception as e:
            logger.error(f"Error getting user notifications: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to get notifications: {str(e)}"
            }
