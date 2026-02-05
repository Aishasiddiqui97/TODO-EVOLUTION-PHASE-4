"""
TaskEvent model for Event-Driven Todo Chatbot.

Represents an audit log entry for task lifecycle events.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class TaskEvent(BaseModel):
    """Audit log entry for task events."""
    eventId: str
    eventType: str  # task.created, task.updated, task.completed, task.deleted
    timestamp: str  # ISO 8601 timestamp
    correlationId: str
    sourceService: str
    userId: str
    taskSnapshot: Dict[str, Any]
    changes: Optional[Dict[str, Dict[str, Any]]] = None
