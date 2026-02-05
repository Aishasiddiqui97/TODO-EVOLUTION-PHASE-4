"""
Dapr client wrapper for Event-Driven Todo Chatbot.

Provides simplified interface to Dapr SDK for state management,
event publishing, and service invocation.
"""

import json
import logging
from typing import Any, Dict, Optional
from dapr.clients import DaprClient
from dapr.clients.grpc._response import StateResponse

logger = logging.getLogger(__name__)


class DaprClientWrapper:
    """Wrapper around Dapr SDK client for common operations."""

    def __init__(self, state_store: str = "statestore", pubsub_name: str = "pubsub"):
        self.state_store = state_store
        self.pubsub_name = pubsub_name

    async def save_state(
        self,
        key: str,
        value: Dict[str, Any],
        etag: Optional[str] = None
    ) -> None:
        """
        Save state to Dapr state store.

        Args:
            key: State key
            value: State value (will be JSON serialized)
            etag: Optional ETag for optimistic concurrency
        """
        async with DaprClient() as client:
            await client.save_state(
                store_name=self.state_store,
                key=key,
                value=json.dumps(value),
                etag=etag,
                state_metadata={"contentType": "application/json"}
            )
            logger.info(f"Saved state: {key}")

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get state from Dapr state store.

        Args:
            key: State key

        Returns:
            State value as dict, or None if not found
        """
        async with DaprClient() as client:
            response: StateResponse = await client.get_state(
                store_name=self.state_store,
                key=key
            )

            if response.data:
                return json.loads(response.data)
            return None

    async def delete_state(self, key: str) -> None:
        """
        Delete state from Dapr state store.

        Args:
            key: State key
        """
        async with DaprClient() as client:
            await client.delete_state(
                store_name=self.state_store,
                key=key
            )
            logger.info(f"Deleted state: {key}")

    async def publish_event(
        self,
        topic: str,
        event: Dict[str, Any]
    ) -> None:
        """
        Publish event to Dapr PubSub.

        Args:
            topic: Topic name
            event: Event data (will be JSON serialized)
        """
        async with DaprClient() as client:
            await client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(event),
                data_content_type="application/json"
            )
            logger.info(f"Published event to topic {topic}: {event.get('eventType')}")

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: Dict[str, Any],
        http_verb: str = "POST"
    ) -> Any:
        """
        Invoke another service via Dapr service invocation.

        Args:
            app_id: Target service app ID
            method_name: Method/endpoint name
            data: Request data
            http_verb: HTTP verb (GET, POST, etc.)

        Returns:
            Response data
        """
        async with DaprClient() as client:
            response = await client.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=json.dumps(data),
                http_verb=http_verb
            )
            logger.info(f"Invoked service {app_id}/{method_name}")
            return response.data
