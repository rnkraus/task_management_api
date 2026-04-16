from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.ai import (
    GroupTasksResponse,
    TaskImproveRequest,
    TaskImproveResponse,
    TaskPlanResponse,
)
from app.services.ai_service import create_task_plan, group_tasks, improve_task
from app.services.task_service import get_all_tasks

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/improve-task", response_model=TaskImproveResponse)
def improve_task_endpoint(data: TaskImproveRequest):
    result = improve_task(data.title, data.description)
    return result


@router.get("/group-tasks", response_model=GroupTasksResponse)
def group_tasks_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = get_all_tasks(
        db=db,
        user_id=current_user.id,
        limit=100,
        offset=0,
        sort_by="id",
        order="asc",
    )

    task_data = [{"id": task.id, "title": task.title} for task in tasks]

    return group_tasks(task_data)


@router.get("/plan", response_model=TaskPlanResponse)
def create_task_plan_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = get_all_tasks(
        db=db,
        user_id=current_user.id,
        limit=100,
        offset=0,
        sort_by="id",
        order="asc",
    )

    task_data = [{"id": task.id, "title": task.title} for task in tasks]

    return create_task_plan(task_data)