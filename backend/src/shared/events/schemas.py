"""
Event schemas for Event-Driven Todo Chatbot.

Defines Pydantic models for all event types.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    """Standard event envelope structure."""
    eventId: str = Field(..., description="Unique event identifier")
    eventType: str = Field(..., description="Event type (e.g., task.created)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    correlationId: str = Field(..., description="Correlation ID for tracing")
    sourceService: str = Field(..., description="Service that published event")
    userId: str = Field(..., description="User who triggered event")
    payload: Dict[str, Any] = Field(..., description="Event-specific data")


class TaskCreatedEvent(BaseModel):
    """Event published when task is created."""
    task: Dict[str, Any]


class TaskUpdatedEvent(BaseModel):
    """Event published when task is updated."""
    task: Dict[str, Any]
    changes: Dict[str, Dict[str, Any]]


class TaskCompletedEvent(BaseModel):
    """Event published when task is completed."""
    task: Dict[str, Any]


class TaskDeletedEvent(BaseModel):
    """Event published when task is deleted."""
    taskId: str
    taskSnapshot: Dict[str, Any]


class ReminderDueEvent(BaseModel):
    """Event published when reminder is due."""
    notificationId: str
    taskId: str
    reminderType: str
    scheduledTime: str


class SyncTaskEvent(BaseModel):
    """Event published for real-time sync."""
    task: Optional[Dict[str, Any]] = None
    taskId: Optional[str] = None
    sequenceNumber: int
    completedAt: Optional[str] = None
