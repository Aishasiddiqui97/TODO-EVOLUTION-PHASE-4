"""
State key generator utility for Event-Driven Todo Chatbot.

Generates consistent state keys following the pattern: {service}.{entity}.{scope}.{id}
"""


def generate_task_key(user_id: str, task_id: str) -> str:
    """
    Generate state key for a task.

    Args:
        user_id: User ID
        task_id: Task ID

    Returns:
        State key in format: chat-api.task.{user_id}.{task_id}
    """
    return f"chat-api.task.{user_id}.{task_id}"


def generate_conversation_key(user_id: str) -> str:
    """
    Generate state key for a conversation.

    Args:
        user_id: User ID

    Returns:
        State key in format: chat-api.conversation.{user_id}
    """
    return f"chat-api.conversation.{user_id}"


def generate_preferences_key(user_id: str) -> str:
    """
    Generate state key for user preferences.

    Args:
        user_id: User ID

    Returns:
        State key in format: chat-api.preferences.{user_id}
    """
    return f"chat-api.preferences.{user_id}"


def generate_notification_key(notification_id: str) -> str:
    """
    Generate state key for a notification.

    Args:
        notification_id: Notification ID

    Returns:
        State key in format: notification.reminder.{notification_id}
    """
    return f"notification.reminder.{notification_id}"


def generate_audit_event_key(event_id: str) -> str:
    """
    Generate state key for an audit event.

    Args:
        event_id: Event ID

    Returns:
        State key in format: audit-log.event.{event_id}
    """
    return f"audit-log.event.{event_id}"


def generate_processed_event_key(event_id: str) -> str:
    """
    Generate state key for tracking processed events (idempotency).

    Args:
        event_id: Event ID

    Returns:
        State key in format: processed-events.{event_id}
    """
    return f"processed-events.{event_id}"
