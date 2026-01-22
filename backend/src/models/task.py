from sqlmodel import SQLModel, Field, Column, DateTime
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    user_id: str = Field(index=True)  # Assuming user_id comes from JWT


class Task(TaskBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))


class TaskRead(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass