"""
Retry Handler with Exponential Backoff for Notification Service.

Implements retry logic for failed notification deliveries with
exponential backoff and maximum retry attempts.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional

from ...shared.dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)


class RetryHandler:
    """
    Service for handling notification delivery retries.

    Implements exponential backoff strategy:
    - 1st retry: 1 minute
    - 2nd retry: 2 minutes
    - 3rd retry: 4 minutes
    - 4th retry: 8 minutes
    - 5th retry: 16 minutes
    """

    def __init__(
        self,
        max_retries: int = 5,
        initial_delay_seconds: int = 60,
        max_delay_seconds: int = 3600
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay_seconds: Initial delay before first retry
            max_delay_seconds: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay_seconds
        self.max_delay = max_delay_seconds
        self.dapr_client = DaprClientWrapper()

    async def retry_with_backoff(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute operation with exponential backoff retry.

        Args:
            operation: Async function to execute
            operation_name: Name of the operation for logging
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Dict with success status and result
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Execute operation
                result = await operation(*args, **kwargs)

                if result.get("success"):
                    if attempt > 0:
                        logger.info(
                            f"{operation_name} succeeded on attempt {attempt + 1}"
                        )
                    return result

                # Operation returned failure
                last_error = result.get("message", "Unknown error")

                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {delay} seconds: {last_error}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"{operation_name} failed after {self.max_retries + 1} attempts: {last_error}"
                    )

            except Exception as e:
                last_error = str(e)

                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"{operation_name} raised exception (attempt {attempt + 1}/{self.max_retries + 1}), "
                        f"retrying in {delay} seconds: {e}",
                        exc_info=True
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"{operation_name} raised exception after {self.max_retries + 1} attempts: {e}",
                        exc_info=True
                    )

        # All retries exhausted
        return {
            "success": False,
            "message": f"Failed after {self.max_retries + 1} attempts: {last_error}",
            "attempts": self.max_retries + 1
        }

    def _calculate_delay(self, attempt: int) -> int:
        """
        Calculate delay for exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: initial_delay * 2^attempt
        delay = self.initial_delay * (2 ** attempt)

        # Cap at max_delay
        return min(delay, self.max_delay)

    async def schedule_retry(
        self,
        notification_id: str,
        user_id: str,
        notification_data: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """
        Schedule a notification retry.

        Args:
            notification_id: ID of the notification
            user_id: ID of the user
            notification_data: Notification data to retry
            attempt: Current attempt number

        Returns:
            Dict with success status
        """
        try:
            if attempt >= self.max_retries:
                logger.warning(
                    f"Max retries reached for notification {notification_id}, "
                    f"moving to dead letter queue"
                )
                await self._move_to_dead_letter_queue(
                    notification_id,
                    user_id,
                    notification_data,
                    reason="max_retries_exceeded"
                )
                return {
                    "success": False,
                    "message": "Max retries exceeded"
                }

            # Calculate next retry time
            delay = self._calculate_delay(attempt)
            retry_time = datetime.utcnow() + timedelta(seconds=delay)

            # Store retry information
            retry_key = f"notification.retry.{notification_id}"
            retry_data = {
                "notificationId": notification_id,
                "userId": user_id,
                "notificationData": notification_data,
                "attempt": attempt + 1,
                "scheduledFor": retry_time.isoformat() + "Z",
                "createdAt": datetime.utcnow().isoformat() + "Z"
            }

            await self.dapr_client.save_state(retry_key, retry_data)

            logger.info(
                f"Scheduled retry {attempt + 1} for notification {notification_id} "
                f"at {retry_time.isoformat()}"
            )

            return {
                "success": True,
                "retryTime": retry_time.isoformat(),
                "attempt": attempt + 1
            }

        except Exception as e:
            logger.error(f"Error scheduling retry: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to schedule retry: {str(e)}"
            }

    async def _move_to_dead_letter_queue(
        self,
        notification_id: str,
        user_id: str,
        notification_data: Dict[str, Any],
        reason: str
    ) -> None:
        """
        Move failed notification to dead letter queue.

        Args:
            notification_id: ID of the notification
            user_id: ID of the user
            notification_data: Notification data
            reason: Reason for failure
        """
        try:
            dlq_key = f"notification.dlq.{notification_id}"
            dlq_entry = {
                "notificationId": notification_id,
                "userId": user_id,
                "notificationData": notification_data,
                "reason": reason,
                "failedAt": datetime.utcnow().isoformat() + "Z"
            }

            await self.dapr_client.save_state(dlq_key, dlq_entry)

            # Add to DLQ index
            dlq_index_key = "notification.dlq.index"
            dlq_index = await self.dapr_client.get_state(dlq_index_key) or {"entries": []}

            dlq_index["entries"].append({
                "notificationId": notification_id,
                "userId": user_id,
                "failedAt": datetime.utcnow().isoformat() + "Z"
            })

            # Keep only last 1000 entries
            dlq_index["entries"] = dlq_index["entries"][-1000:]

            await self.dapr_client.save_state(dlq_index_key, dlq_index)

            logger.info(f"Moved notification {notification_id} to dead letter queue")

        except Exception as e:
            logger.error(f"Error moving to dead letter queue: {e}", exc_info=True)

    async def get_retry_status(
        self,
        notification_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get retry status for a notification.

        Args:
            notification_id: ID of the notification

        Returns:
            Retry status dict or None
        """
        try:
            retry_key = f"notification.retry.{notification_id}"
            retry_data = await self.dapr_client.get_state(retry_key)

            return retry_data

        except Exception as e:
            logger.warning(f"Error getting retry status: {e}")
            return None

    async def cancel_retry(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a scheduled retry.

        Args:
            notification_id: ID of the notification

        Returns:
            Dict with success status
        """
        try:
            retry_key = f"notification.retry.{notification_id}"

            # Delete retry data
            await self.dapr_client.delete_state(retry_key)

            logger.info(f"Cancelled retry for notification {notification_id}")

            return {
                "success": True,
                "message": "Retry cancelled"
            }

        except Exception as e:
            logger.error(f"Error cancelling retry: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to cancel retry: {str(e)}"
            }
