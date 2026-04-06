from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.models.task import Task as TaskModel
from app.schemas.user import UserCreate, UserUpdate, UserPut


def create_user(db: Session, user_data: UserCreate) -> UserModel:
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise ValueError("Email already exists")

    user = UserModel(
        email=user_data.email,
        name=user_data.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[UserModel]:
    return db.query(UserModel).all()


def get_user_by_id(db: Session, user_id: int) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserPut) -> UserModel | None:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        return None

    existing = (
        db.query(UserModel)
        .filter(UserModel.email == user_data.email, UserModel.id != user_id)
        .first()
    )
    if existing is not None:
        raise ValueError("Email already exists")

    user.email = user_data.email
    user.name = user_data.name

    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user_id: int, user_data: UserUpdate) -> UserModel | None:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        return None

    if user_data.email is not None:
        existing = (
            db.query(UserModel)
            .filter(UserModel.email == user_data.email, UserModel.id != user_id)
            .first()
        )
        if existing is not None:
            raise ValueError("Email already exists")
        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> UserModel | None:
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        return None

    has_tasks = db.query(TaskModel).filter(TaskModel.user_id == user_id).first()
    if has_tasks is not None:
        raise ValueError("Cannot delete user with existing tasks")

    db.delete(user)
    db.commit()
    return user