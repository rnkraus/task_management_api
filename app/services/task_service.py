from sqlalchemy.orm import Session
from app.models.task import Task as TaskModel
from app.schemas.task import TaskCreate, TaskPut, TaskUpdate


def create_task(db:Session, task_data: TaskCreate) -> TaskModel:
    new_task = TaskModel(
        title=task_data.title,
        completed=task_data.completed,
        description=task_data.description,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_all_tasks(db:Session) -> list[TaskModel]:
        return db.query(TaskModel).all()


def get_task_by_id(db: Session, task_id: int) -> TaskModel | None:
    return db.query(TaskModel).filter(TaskModel.id == task_id).first()


def update_task(db: Session,task_id: int, task_data: TaskPut) -> TaskModel | None:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task is None:
            return None

        task.title = task_data.title
        task.completed = task_data.completed
        task.description = task_data.description

        db.commit()
        db.refresh(task)
        return task


def patch_task(db: Session, task_id: int, task_data: TaskUpdate) -> TaskModel | None:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task is None:
            return None

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.completed is not None:
            task.completed = task_data.completed
        if task_data.description is not None:
            task.description = task_data.description

        db.commit()
        db.refresh(task)
        return task


def delete_task(db: Session, task_id: int) -> TaskModel | None:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task is None:
            return None

        db.delete(task)
        db.commit()
        return task