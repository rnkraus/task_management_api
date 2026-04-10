from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskPut, TaskDetailResponse
from app.services.task_service import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    patch_task
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
def create_task_endpoint(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(db, task, current_user.id)


@router.get("", response_model=list[TaskResponse])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_tasks(db, current_user.id)


@router.get("/{task_id}", response_model=TaskDetailResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_by_id(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task_endpoint(
    task_id: int,
    task: TaskPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_task = update_task(db, task_id, task, current_user.id)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task_endpoint(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated_task = patch_task(db, task_id, task, current_user.id)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_task = delete_task(db, task_id, current_user.id)
    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return deleted_task