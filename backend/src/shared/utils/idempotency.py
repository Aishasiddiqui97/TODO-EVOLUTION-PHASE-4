"""
Idempotency checker utility for Event-Driven Todo Chatbot.

Ensures events are processed only once using Dapr state store.
"""

import logging
from ..dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)


class IdempotencyChecker:
    """Checks and marks events as processed for idempotent event handling."""

    def __init__(self):
        self.dapr_client = DaprClientWrapper()

    async def is_processed(self, event_id: str) -> bool:
        """
        Check if event has already been processed.

        Args:
            event_id: Event ID to check

        Returns:
            True if event was already processed, False otherwise
        """
        key = f"processed-events.{event_id}"
        state = await self.dapr_client.get_state(key)
        return state is not None

    async def mark_processed(self, event_id: str) -> None:
        """
        Mark event as processed.

        Args:
            event_id: Event ID to mark as processed
        """
        key = f"processed-events.{event_id}"
        await self.dapr_client.save_state(key, {"processed": True})
        logger.info(f"Marked event as processed: {event_id}")

    async def process_once(self, event_id: str, handler_func, *args, **kwargs):
        """
        Execute handler function only if event hasn't been processed.

        Args:
            event_id: Event ID
            handler_func: Async function to execute
            *args: Arguments for handler function
            **kwargs: Keyword arguments for handler function

        Returns:
            Handler function result, or None if already processed
        """
        if await self.is_processed(event_id):
            logger.info(f"Event already processed, skipping: {event_id}")
            return None

        result = await handler_func(*args, **kwargs)
        await self.mark_processed(event_id)
        return result
