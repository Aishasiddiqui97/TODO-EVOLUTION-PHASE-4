"""
Reminder Due Event Handler for Notification Service.

Listens for reminder.scheduled events and sends notifications
when task reminders are due.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..services.inapp_notifier import InAppNotifier
from ..services.email_notifier import EmailNotifier
from ..services.consolidator import NotificationConsolidator
from ...shared.dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)

router = APIRouter()


class CloudEvent(BaseModel):
    """Cloud Event format from Dapr PubSub."""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: Dict[str, Any]


@router.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "task-pubsub",
            "topic": "reminder-events",
            "route": "/events/reminder-due"
        }
    ]


@router.post("/events/reminder-due")
async def handle_reminder_due(request: Request):
    """
    Handle reminder.scheduled events.

    When a reminder is due, this handler:
    1. Retrieves user preferences for notification channels
    2. Consolidates multiple simultaneous notifications
    3. Sends notifications via configured channels (in-app, email)
    4. Implements retry logic for failed deliveries

    Args:
        request: FastAPI request containing CloudEvent

    Returns:
        Success response
    """
    try:
        # Parse CloudEvent
        event_data = await request.json()
        logger.info(f"Received event: {event_data.get('type')}")

        # Extract event type and payload
        event_type = event_data.get("type", "")
        data = event_data.get("data", {})

        # Only process reminder.scheduled events
        if event_type != "reminder.scheduled":
            logger.debug(f"Ignoring event type: {event_type}")
            return {"status": "ignored", "reason": "not a reminder.scheduled event"}

        # Extract reminder details
        task_id = data.get("taskId")
        user_id = data.get("userId")
        reminder_type = data.get("reminderType")
        task_title = data.get("taskTitle")
        reminder_time = data.get("reminderTime")

        if not all([task_id, user_id, reminder_type, task_title]):
            logger.warning("Missing required fields in reminder event")
            return {"status": "error", "reason": "missing required fields"}

        # Get user preferences for notification channels
        dapr_client = DaprClientWrapper()
        preferences_key = f"chat-api.preferences.user.{user_id}"
        preferences_data = await dapr_client.get_state(preferences_key)

        notification_channels = ["in-app", "email"]  # Default
        if preferences_data:
            notification_channels = preferences_data.get("notificationChannels", ["in-app", "email"])

        # Check for consolidation (multiple reminders at same time)
        consolidator = NotificationConsolidator()
        should_consolidate, consolidated_tasks = await consolidator.check_consolidation(
            user_id=user_id,
            task_id=task_id,
            reminder_time=reminder_time
        )

        # Prepare notification content
        if should_consolidate and len(consolidated_tasks) > 1:
            notification_title = f"{len(consolidated_tasks)} Task Reminders"
            notification_body = f"You have {len(consolidated_tasks)} tasks due soon:\n"
            for task in consolidated_tasks:
                notification_body += f"- {task['title']}\n"
        else:
            if reminder_type == "advance":
                advance_hours = data.get("advanceHours", 24)
                notification_title = f"Upcoming Task: {task_title}"
                notification_body = f"Reminder: '{task_title}' is due in {advance_hours} hours"
            else:  # due
                notification_title = f"Task Due: {task_title}"
                notification_body = f"'{task_title}' is due now"

        # Send notifications via configured channels
        results = []

        # In-app notification
        if "in-app" in notification_channels:
            try:
                inapp_notifier = InAppNotifier()
                inapp_result = await inapp_notifier.send_notification(
                    user_id=user_id,
                    title=notification_title,
                    body=notification_body,
                    task_id=task_id,
                    reminder_type=reminder_type
                )
                results.append({"channel": "in-app", "success": inapp_result["success"]})
                logger.info(f"In-app notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending in-app notification: {e}", exc_info=True)
                results.append({"channel": "in-app", "success": False, "error": str(e)})

        # Email notification
        if "email" in notification_channels:
            try:
                email_notifier = EmailNotifier()
                email_result = await email_notifier.send_notification(
                    user_id=user_id,
                    title=notification_title,
                    body=notification_body,
                    task_id=task_id,
                    reminder_type=reminder_type
                )
                results.append({"channel": "email", "success": email_result["success"]})
                logger.info(f"Email notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending email notification: {e}", exc_info=True)
                results.append({"channel": "email", "success": False, "error": str(e)})

        # Check if all notifications succeeded
        all_success = all(r.get("success", False) for r in results)

        if all_success:
            logger.info(f"All notifications sent successfully for task {task_id}")
            return {
                "status": "success",
                "channels": results,
                "message": "Notifications sent successfully"
            }
        else:
            logger.warning(f"Some notifications failed for task {task_id}")
            return {
                "status": "partial_success",
                "channels": results,
                "message": "Some notifications failed"
            }

    except Exception as e:
        logger.error(f"Error handling reminder.due event: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }
