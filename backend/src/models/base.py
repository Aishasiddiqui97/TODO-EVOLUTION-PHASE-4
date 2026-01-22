from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class BaseModel(SQLModel):
    """
    Base model with common fields for all database models.
    Provides created_at and updated_at timestamps.
    """
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
