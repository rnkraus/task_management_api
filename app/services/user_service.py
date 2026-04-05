from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import UserCreate


def create_user(db: Session, user_data: UserCreate) -> UserModel:
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise ValueError("Email already exists")

    user = UserModel(email=user_data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session) -> list[UserModel]:
    return db.query(UserModel).all()


def get_user_by_id(db: Session, user_id: int) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.id == user_id).first()