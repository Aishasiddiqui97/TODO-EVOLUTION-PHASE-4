from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid


class Conversation(SQLModel, table=True):
    """
    Conversation model for Phase III AI Chatbot.
    Represents a chat session between user and AI assistant.
    """
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="UUID for the conversation"
    )
    user_id: str = Field(
        foreign_key="users.id",
        index=True,
        description="ID of the user who owns this conversation"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Auto-generated title from first message"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the conversation was last updated"
    )
    last_message_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Timestamp of the last message in this conversation"
    )

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
