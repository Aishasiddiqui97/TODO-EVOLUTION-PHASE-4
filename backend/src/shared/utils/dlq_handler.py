"""
Dead letter queue handler for failed events.

Processes events that failed after maximum retry attempts.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DeadLetterQueueHandler:
    """
    Handles events that failed after all retry attempts.

    Stores failed events for manual inspection and reprocessing.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize DLQ handler.

        Args:
            dapr_http_port: Dapr HTTP port for state API
        """
        self.dapr_http_port = dapr_http_port
        self.dapr_base_url = f"http://localhost:{dapr_http_port}"
        self.state_store_name = "statestore"

    async def store_failed_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        error_message: str,
        retry_count: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a failed event in the dead letter queue.

        Args:
            event_type: Type of event that failed
            event_data: Original event data
            error_message: Error message from last failure
            retry_count: Number of retry attempts made
            metadata: Optional metadata

        Returns:
            Result dictionary
        """
        try:
            import aiohttp

            # Generate DLQ entry ID
            dlq_id = f"dlq-{uuid.uuid4()}"
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Create DLQ entry
            dlq_entry = {
                "id": dlq_id,
                "eventType": event_type,
                "eventData": event_data,
                "errorMessage": error_message,
                "retryCount": retry_count,
                "timestamp": timestamp,
                "status": "failed",
                "metadata": metadata or {}
            }

            # Save to state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"

            state_data = [{
                "key": dlq_id,
                "value": dlq_entry
            }]

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=state_data) as response:
                    if response.status in [200, 201, 204]:
                        logger.info(f"Stored failed event in DLQ: {dlq_id}")

                        # Update DLQ index
                        await self._update_dlq_index(dlq_id, event_type, timestamp)

                        return {
                            "success": True,
                            "dlqId": dlq_id,
                            "timestamp": timestamp
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to store DLQ entry: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }

        except Exception as e:
            logger.error(f"Error storing failed event: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_dlq_index(
        self,
        dlq_id: str,
        event_type: str,
        timestamp: str
    ) -> None:
        """
        Update DLQ index for efficient querying.

        Args:
            dlq_id: DLQ entry ID
            event_type: Event type
            timestamp: Timestamp
        """
        try:
            import aiohttp

            index_key = "dlq-index"

            # Get existing index
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{index_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        index_data = await response.json()
                    else:
                        index_data = {"entries": []}

                # Add new entry (keep last 10000)
                entries = index_data.get("entries", [])
                entries.append({
                    "id": dlq_id,
                    "eventType": event_type,
                    "timestamp": timestamp
                })

                if len(entries) > 10000:
                    entries = entries[-10000:]

                index_data["entries"] = entries

                # Save updated index
                save_url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"
                state_data = [{
                    "key": index_key,
                    "value": index_data
                }]

                async with session.post(save_url, json=state_data) as save_response:
                    if save_response.status not in [200, 201, 204]:
                        logger.warning("Failed to update DLQ index")

        except Exception as e:
            logger.error(f"Error updating DLQ index: {e}", exc_info=True)

    async def get_failed_events(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve failed events from DLQ.

        Args:
            limit: Maximum number of entries
            offset: Number of entries to skip
            event_type: Filter by event type

        Returns:
            Dictionary with failed events
        """
        try:
            import aiohttp

            # Get DLQ index
            index_key = "dlq-index"
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{index_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "success": True,
                            "events": [],
                            "count": 0,
                            "total": 0
                        }

                    index_data = await response.json()
                    entries = index_data.get("entries", [])

                # Reverse to get most recent first
                entries = list(reversed(entries))

                # Filter by event type if specified
                if event_type:
                    entries = [e for e in entries if e.get("eventType") == event_type]

                # Fetch DLQ entries
                events = []
                for entry in entries[offset:offset + limit]:
                    dlq_id = entry["id"]

                    # Fetch DLQ entry
                    entry_url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{dlq_id}"

                    async with session.get(entry_url) as entry_response:
                        if entry_response.status == 200:
                            event_data = await entry_response.json()
                            events.append(event_data)

                total = len(entries)

                logger.info(f"Retrieved {len(events)} failed events from DLQ")

                return {
                    "success": True,
                    "events": events,
                    "count": len(events),
                    "total": total
                }

        except Exception as e:
            logger.error(f"Error retrieving failed events: {e}", exc_info=True)
            return {
                "success": False,
                "events": [],
                "count": 0,
                "error": str(e)
            }

    async def reprocess_event(self, dlq_id: str) -> Dict[str, Any]:
        """
        Mark an event for reprocessing.

        Args:
            dlq_id: DLQ entry ID

        Returns:
            Result dictionary
        """
        try:
            import aiohttp

            # Get DLQ entry
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{dlq_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": "DLQ entry not found"
                        }

                    dlq_entry = await response.json()

                # Update status
                dlq_entry["status"] = "reprocessing"
                dlq_entry["reprocessedAt"] = datetime.utcnow().isoformat() + "Z"

                # Save updated entry
                save_url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"
                state_data = [{
                    "key": dlq_id,
                    "value": dlq_entry
                }]

                async with session.post(save_url, json=state_data) as save_response:
                    if save_response.status in [200, 201, 204]:
                        logger.info(f"Marked DLQ entry for reprocessing: {dlq_id}")
                        return {
                            "success": True,
                            "dlqId": dlq_id,
                            "eventData": dlq_entry["eventData"]
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to update DLQ entry"
                        }

        except Exception as e:
            logger.error(f"Error reprocessing event: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_event(self, dlq_id: str) -> Dict[str, Any]:
        """
        Delete an event from DLQ.

        Args:
            dlq_id: DLQ entry ID

        Returns:
            Result dictionary
        """
        try:
            import aiohttp

            # Delete from state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{dlq_id}"

            async with aiohttp.ClientSession() as session:
                async with session.delete(url) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Deleted DLQ entry: {dlq_id}")
                        return {
                            "success": True,
                            "dlqId": dlq_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }

        except Exception as e:
            logger.error(f"Error deleting DLQ entry: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
