"""
UserPreferences model for Event-Driven Todo Chatbot.

Represents user settings for notifications, reminders, and defaults.
"""

from typing import List
from pydantic import BaseModel, EmailStr, Field
from .task import TaskPriority


class UserPreferences(BaseModel):
    """User preferences entity."""
    userId: str
    notificationChannels: List[str] = Field(default=["in-app", "email"])
    reminderAdvanceTime: int = Field(default=24, ge=1, le=168, description="Hours before due time")
    defaultPriority: TaskPriority = TaskPriority.MEDIUM
    timezone: str = Field(default="UTC", description="IANA timezone")
    emailAddress: EmailStr
    updatedAt: str

    class Config:
        use_enum_values = True
