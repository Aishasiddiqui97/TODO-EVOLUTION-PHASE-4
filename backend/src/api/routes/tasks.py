from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from ...models.task import Task, TaskRead, TaskCreate, TaskUpdate
from ...db import get_session
from ...auth.dependencies import get_current_user

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_create: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create a new task with the current user's ID
    task = Task(
        description=task_create.description,
        completed=task_create.completed,
        user_id=current_user["user_id"]
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    current_user: dict = Depends(get_current_user),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    session: Session = Depends(get_session)
):
    # Build the query with user isolation
    query = select(Task).where(Task.user_id == current_user["user_id"])

    # Apply completion filter if provided
    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = session.exec(query).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Find the task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Find the task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Update the task with provided values
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Find the task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    session.delete(task)
    session.commit()
    return


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def update_task_completion(
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Find the task belonging to the current user
    statement = select(Task).where(Task.id == task_id, Task.user_id == current_user["user_id"])
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or does not belong to user"
        )

    # Update only the completion status
    if task_update.completed is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="completed field is required"
        )

    task.completed = task_update.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task