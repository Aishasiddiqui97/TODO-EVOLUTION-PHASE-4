from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Generator, AsyncGenerator
import os

# Get database URL from environment
# For Neon Serverless PostgreSQL, use asyncpg driver
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/todo_db"
)

# Convert to async URL if using postgresql://
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create synchronous engine (for migrations and simple operations)
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Create async engine for Phase III (stateless, async operations)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a synchronous database session (Phase II compatibility).
    Used for migrations and simple operations.
    """
    with Session(engine) as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session for Phase III stateless operations.
    Each request gets a fresh session from the pool.
    """
    async with async_session_maker() as session:
        yield session
