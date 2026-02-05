"""
Task model for Event-Driven Todo Chatbot.

Represents a todo item with priorities, due dates, tags, and optional recurrence.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


class RecurrenceType(str, Enum):
    """Recurrence pattern types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class EndConditionType(str, Enum):
    """Recurrence end condition types."""
    NEVER = "never"
    AFTER_OCCURRENCES = "afterOccurrences"
    BY_DATE = "byDate"


class EndCondition(BaseModel):
    """Recurrence end condition."""
    type: EndConditionType
    occurrences: Optional[int] = None
    endDate: Optional[str] = None


class RecurrencePattern(BaseModel):
    """Defines how a task repeats."""
    type: RecurrenceType
    interval: int = Field(..., ge=1, description="Repeat every N days/weeks")
    daysOfWeek: Optional[List[str]] = Field(None, description="Days for weekly pattern")
    timezone: str = Field(default="UTC", description="IANA timezone")
    endCondition: Optional[EndCondition] = None


class Task(BaseModel):
    """Task entity."""
    id: str
    userId: str
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: TaskPriority = TaskPriority.MEDIUM
    dueDate: Optional[str] = None  # ISO 8601 date
    dueTime: Optional[str] = None  # HH:MM format
    tags: List[str] = Field(default_factory=list, max_items=100)
    status: TaskStatus = TaskStatus.PENDING
    recurrencePattern: Optional[RecurrencePattern] = None
    parentTaskId: Optional[str] = None
    createdAt: str
    updatedAt: str
    completedAt: Optional[str] = None

    class Config:
        use_enum_values = True
