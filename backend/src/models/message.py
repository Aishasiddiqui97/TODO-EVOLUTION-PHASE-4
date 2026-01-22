from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum for user and assistant messages"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Message model for Phase III AI Chatbot.
    Represents a single message in a conversation (user or assistant).
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing message ID"
    )
    conversation_id: str = Field(
        foreign_key="conversations.id",
        index=True,
        description="ID of the conversation this message belongs to"
    )
    role: MessageRole = Field(
        description="Role of the message sender (user or assistant)"
    )
    content: str = Field(
        description="Message content in plain text"
    )
    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="MCP tool calls made by assistant (JSON)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="When the message was created"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
