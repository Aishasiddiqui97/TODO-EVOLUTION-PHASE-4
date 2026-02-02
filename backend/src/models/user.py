from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    hashed_password: str


class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    password: str  # Plain text password for input validation


class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None  # Plain text password for input