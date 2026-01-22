"""
Message service for Phase III.
Handles message CRUD operations and conversation history.

Constitutional Requirements:
- Service is stateless (no in-memory state)
- All operations persist to database immediately
- History is fetched from database each request
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models.message import Message, MessageRole

logger = logging.getLogger(__name__)


class MessageService:
    """
    Service for managing messages in conversations.

    Provides stateless operations for message persistence and retrieval.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize message service with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation UUID
            role: Message role ("user" or "assistant")
            content: Message content
            tool_calls: Optional tool calls made by assistant

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole(role),
            content=content,
            tool_calls=tool_calls
        )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        logger.info(
            f"Added {role} message to conversation {conversation_id}, "
            f"tool_calls: {len(tool_calls) if tool_calls else 0}"
        )
        return message

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Message]:
        """
        Get conversation history (last N messages).

        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of messages to return

        Returns:
            List of messages ordered chronologically (oldest first)
        """
        # Fetch last N messages in descending order
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)
        messages = result.scalars().all()

        # Reverse to get chronological order (oldest first)
        messages_list = list(reversed(list(messages)))

        logger.info(
            f"Retrieved {len(messages_list)} messages for conversation {conversation_id}"
        )
        return messages_list

    async def get_message_by_id(
        self,
        message_id: int
    ) -> Optional[Message]:
        """
        Get a specific message by ID.

        Args:
            message_id: Message ID

        Returns:
            Message if found, None otherwise
        """
        statement = select(Message).where(Message.id == message_id)
        result = await self.session.execute(statement)
        message = result.scalar_one_or_none()

        if message:
            logger.info(f"Retrieved message {message_id}")
        else:
            logger.warning(f"Message {message_id} not found")

        return message

    async def get_messages_with_tool_calls(
        self,
        conversation_id: str
    ) -> List[Message]:
        """
        Get all messages in a conversation that have tool calls.

        Args:
            conversation_id: Conversation UUID

        Returns:
            List of messages with tool calls
        """
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.tool_calls.isnot(None)
            )
            .order_by(Message.created_at)
        )

        result = await self.session.execute(statement)
        messages = result.scalars().all()

        logger.info(
            f"Retrieved {len(messages)} messages with tool calls "
            f"for conversation {conversation_id}"
        )
        return list(messages)

    async def count_messages(
        self,
        conversation_id: str
    ) -> int:
        """
        Count total messages in a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Number of messages
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
        )

        result = await self.session.execute(statement)
        messages = result.scalars().all()
        count = len(list(messages))

        logger.info(f"Conversation {conversation_id} has {count} messages")
        return count

    async def get_first_user_message(
        self,
        conversation_id: str
    ) -> Optional[Message]:
        """
        Get the first user message in a conversation.
        Used for auto-generating conversation titles.

        Args:
            conversation_id: Conversation UUID

        Returns:
            First user message or None if no messages
        """
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.role == MessageRole.USER
            )
            .order_by(Message.created_at)
            .limit(1)
        )

        result = await self.session.execute(statement)
        message = result.scalar_one_or_none()

        if message:
            logger.info(f"Retrieved first user message for conversation {conversation_id}")

        return message

    async def delete_messages(
        self,
        conversation_id: str
    ) -> int:
        """
        Delete all messages in a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Number of messages deleted
        """
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        )

        result = await self.session.execute(statement)
        messages = result.scalars().all()
        count = len(list(messages))

        for message in messages:
            await self.session.delete(message)

        await self.session.commit()

        logger.info(f"Deleted {count} messages from conversation {conversation_id}")
        return count
