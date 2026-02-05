"""
Conversation model for Event-Driven Todo Chatbot.

Represents chat conversation history for AI context (Phase III compatibility).
"""

from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Single message in conversation."""
    role: MessageRole
    content: str = Field(..., max_length=10000)
    timestamp: str  # ISO 8601 timestamp

    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """Conversation history entity."""
    userId: str
    messages: List[Message] = Field(default_factory=list, max_items=100)
    updatedAt: str
