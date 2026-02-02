"""
Task service for Phase III.
Handles task CRUD operations with database.

Constitutional Requirements:
- Service is stateless (no in-memory state)
- All operations persist to database immediately
- Each request fetches fresh data from database
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from datetime import datetime
import logging

from ..models.task import Task, TaskPriority

logger = logging.getLogger(__name__)


class TaskService:
    """
    Service for managing tasks in the database.

    Provides stateless operations for task lifecycle management.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize task service with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[str] = None
    ) -> Task:
        """
        Create a new task for a user.

        Args:
            user_id: ID of the user
            title: Task title
            description: Optional task description
            due_date: Optional due date
            priority: Optional priority level

        Returns:
            Created task
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=TaskPriority(priority) if priority else None,
            completed=False
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}: {title}")
        return task

    async def get_task(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Get a task by ID, ensuring it belongs to the user.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            Task if found and owned by user, None otherwise
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        result = await self.session.execute(statement)
        task = result.scalar_one_or_none()

        if task:
            logger.info(f"Retrieved task {task_id} for user {user_id}")
        else:
            logger.warning(f"Task {task_id} not found for user {user_id}")

        return task

    async def get_user_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks for a user with optional filtering.

        Args:
            user_id: User ID
            completed: Filter by completion status (None = all)
            priority: Filter by priority level
            limit: Maximum number of tasks to return

        Returns:
            List of tasks
        """
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        if priority:
            statement = statement.where(Task.priority == TaskPriority(priority))

        statement = statement.order_by(Task.created_at.desc()).limit(limit)

        result = await self.session.execute(statement)
        tasks = result.scalars().all()

        logger.info(
            f"Retrieved {len(tasks)} tasks for user {user_id} "
            f"(completed={completed}, priority={priority})"
        )
        return list(tasks)

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[str] = None,
        completed: Optional[bool] = None
    ) -> Optional[Task]:
        """
        Update a task.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            priority: New priority (optional)
            completed: New completion status (optional)

        Returns:
            Updated task or None if not found
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if priority is not None:
            task.priority = TaskPriority(priority)
        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(f"Updated task {task_id} for user {user_id}")
        return task

    async def delete_task(
        self,
        task_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            True if deleted, False if not found
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")
        return True

    async def complete_task(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            Updated task or None if not found
        """
        return await self.update_task(task_id, user_id, completed=True)

    async def search_tasks(
        self,
        user_id: str,
        query: str,
        limit: int = 50
    ) -> List[Task]:
        """
        Search tasks by title or description.

        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching tasks
        """
        statement = (
            select(Task)
            .where(
                Task.user_id == user_id,
                (Task.title.ilike(f"%{query}%")) | (Task.description.ilike(f"%{query}%"))
            )
            .order_by(Task.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(statement)
        tasks = result.scalars().all()

        logger.info(f"Found {len(tasks)} tasks matching '{query}' for user {user_id}")
        return list(tasks)
