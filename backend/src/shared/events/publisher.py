"""
Event publisher utility for Event-Driven Todo Chatbot.

Handles event publishing with consistent structure and metadata.
"""

import uuid
from datetime import datetime
from typing import Any, Dict
from ..dapr_client.client import DaprClientWrapper


class EventPublisher:
    """Publishes events with consistent envelope structure."""

    def __init__(self, source_service: str):
        self.source_service = source_service
        self.dapr_client = DaprClientWrapper()

    async def publish(
        self,
        topic: str,
        event_type: str,
        user_id: str,
        payload: Dict[str, Any],
        correlation_id: str = None
    ) -> str:
        """
        Publish event with standard envelope.

        Args:
            topic: Topic name (task-events, reminders, task-updates)
            event_type: Event type (e.g., task.created)
            user_id: User ID who triggered the event
            payload: Event-specific data
            correlation_id: Optional correlation ID for tracing

        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())

        event = {
            "eventId": event_id,
            "eventType": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlationId": correlation_id or str(uuid.uuid4()),
            "sourceService": self.source_service,
            "userId": user_id,
            "payload": payload
        }

        await self.dapr_client.publish_event(topic, event)

        return event_id
