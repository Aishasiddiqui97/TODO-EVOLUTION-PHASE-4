"""
Notification model for Event-Driven Todo Chatbot.

Represents a scheduled notification/reminder for a task.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    IN_APP = "in-app"
    EMAIL = "email"


class Notification(BaseModel):
    """Notification entity."""
    id: str
    taskId: str
    userId: str
    scheduledTime: str  # ISO 8601 timestamp
    channels: List[NotificationChannel]
    status: NotificationStatus = NotificationStatus.SCHEDULED
    sentAt: Optional[str] = None
    retryCount: int = Field(default=0, ge=0, le=3)
    lastError: Optional[str] = Field(None, max_length=1000)
    createdAt: str

    class Config:
        use_enum_values = True
