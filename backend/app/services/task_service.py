from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from app.models.task import Task as TaskModel
from app.schemas.task import TaskCreate, TaskPut, TaskUpdate


def create_task(db: Session, task_data: TaskCreate, user_id: int) -> TaskModel:
    new_task = TaskModel(
        title=task_data.title,
        completed=task_data.completed,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        user_id=user_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_all_tasks(
    db: Session,
    user_id: int,
    completed: bool | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "due_date",
    order: str = "asc",
) -> list[TaskModel]:
    query = db.query(TaskModel).filter(TaskModel.user_id == user_id)

    if completed is not None:
        query = query.filter(TaskModel.completed == completed)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                TaskModel.title.ilike(search_term),
                TaskModel.description.ilike(search_term),
            )
        )

    allowed_sort_fields = {
        "id": TaskModel.id,
        "title": TaskModel.title,
        "completed": TaskModel.completed,
        "created_at": TaskModel.created_at,
        "updated_at": TaskModel.updated_at,
        "priority": TaskModel.priority,
        "due_date": TaskModel.due_date,
    }

    sort_column = allowed_sort_fields.get(sort_by, TaskModel.due_date)

    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    return query.offset(offset).limit(limit).all()


def get_task_by_id(db: Session, task_id: int, user_id: int) -> TaskModel | None:
    return (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )


def update_task(
    db: Session,
    task_id: int,
    task_data: TaskPut,
    user_id: int,
) -> TaskModel | None:
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if task is None:
        return None

    task.title = task_data.title
    task.completed = task_data.completed
    task.description = task_data.description
    task.due_date = task_data.due_date
    task.priority = task_data.priority

    db.commit()
    db.refresh(task)
    return task


def patch_task(
    db: Session,
    task_id: int,
    task_data: TaskUpdate,
    user_id: int,
) -> TaskModel | None:
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if task is None:
        return None

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.priority is not None:
        task.priority = task_data.priority

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int) -> TaskModel | None:
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
        .first()
    )
    if task is None:
        return None

    db.delete(task)
    db.commit()
    return task