from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserPut, UserUpdate, UserResponse
from app.services.user_service import (
    get_users,
    get_user_by_id,
    update_user,
    patch_user,
    delete_user,
)

router = APIRouter(prefix="/users", tags=["users"])



@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user: UserPut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_user = update_user(db, current_user.id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.patch("/me", response_model=UserResponse)
def patch_me(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_user = patch_user(db, current_user.id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/me", response_model=UserResponse)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted_user = delete_user(db, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user


@router.get("", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return get_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_admin(
    user_id: int,
    user: UserPut,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        updated_user = update_user(db, user_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user_by_admin(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        updated_user = patch_user(db, user_id, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    try:
        deleted_user = delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user