from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskPut
from app.services.task_service import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task as update_task_service,
    delete_task as delete_task_service,
    patch_task
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse)
def create_task_endpoint(task: TaskCreate):
    return create_task(task)


@router.get("", response_model=list[TaskResponse])
def read_tasks():
    return get_all_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: int, task: TaskPut):
    updated_task = update_task_service(task_id, task)

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task


@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task_endpoint(task_id: int, task: TaskUpdate):
    updated_task = patch_task(task_id, task)

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task


@router.delete("/{task_id}", response_model=TaskResponse)
def delete_task_endpoint(task_id: int):
    deleted_task = delete_task_service(task_id)

    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return deleted_task