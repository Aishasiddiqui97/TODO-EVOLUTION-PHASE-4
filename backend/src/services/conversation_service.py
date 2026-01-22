"""
Conversation persistence service for Phase III.
Handles conversation CRUD operations with database.

Constitutional Requirements:
- Service is stateless (no in-memory state)
- All operations persist to database immediately
- Each request fetches fresh data from database
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
import logging

from ..models.conversation import Conversation
from ..models.message import Message

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service for managing conversations in the database.

    Provides stateless operations for conversation lifecycle management.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize conversation service with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def create_conversation(
        self,
        user_id: int,
        title: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: ID of the user
            title: Optional conversation title

        Returns:
            Created conversation
        """
        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring it belongs to the user.

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )

        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation:
            logger.info(f"Retrieved conversation {conversation_id} for user {user_id}")
        else:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")

        return conversation

    async def get_user_conversations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Conversation]:
        """
        Get recent conversations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of conversations to return

        Returns:
            List of conversations ordered by last_message_at (most recent first)
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.last_message_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)
        conversations = result.scalars().all()

        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
        return list(conversations)

    async def update_last_message_time(
        self,
        conversation_id: str
    ) -> None:
        """
        Update the last_message_at timestamp for a conversation.

        Args:
            conversation_id: Conversation UUID
        """
        statement = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                last_message_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        await self.session.execute(statement)
        await self.session.commit()

        logger.info(f"Updated last_message_at for conversation {conversation_id}")

    async def update_conversation_title(
        self,
        conversation_id: str,
        title: str
    ) -> None:
        """
        Update the title of a conversation.

        Args:
            conversation_id: Conversation UUID
            title: New title
        """
        statement = (
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(
                title=title,
                updated_at=datetime.utcnow()
            )
        )

        await self.session.execute(statement)
        await self.session.commit()

        logger.info(f"Updated title for conversation {conversation_id}")

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:
        """
        Delete a conversation and all its messages.

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found
        """
        # Verify ownership
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.commit()

        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return True

    async def get_conversation_with_messages(
        self,
        conversation_id: str,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get a conversation with all its messages loaded.

        Args:
            conversation_id: Conversation UUID
            user_id: User ID for ownership verification

        Returns:
            Conversation with messages or None if not found
        """
        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .options(selectinload(Conversation.messages))
        )

        result = await self.session.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation:
            logger.info(
                f"Retrieved conversation {conversation_id} with "
                f"{len(conversation.messages)} messages"
            )

        return conversation
