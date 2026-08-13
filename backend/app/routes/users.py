from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.services import user_service
from app.schemas.user import UserOut


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("", response_model=list[UserOut])
def list_users(
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return user_service.list_users(db=db)


@router.get("/profile")
def my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = user_service.get_user_with_balances(
        db=db,
        user_id=current_user["user_id"],
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return profile


@router.get("/{user_id}")
def user_detail(
    user_id: int,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    profile = user_service.get_user_with_balances(
        db=db,
        user_id=user_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return profile
