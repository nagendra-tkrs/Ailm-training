import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.services import user_service
from app.schemas.user import UserOut

logger = logging.getLogger("app.routes.users")

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/profile")
def my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        profile = user_service.get_user_with_balances(
            db=db,
            user_id=current_user["user_id"],
        )
    except SQLAlchemyError:
        logger.error("Database error fetching profile", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return profile


@router.get("", response_model=list[UserOut])
def list_users(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        return user_service.list_users(db=db)
    except SQLAlchemyError:
        logger.error("Database error listing users", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/{user_id}")
def user_detail(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    try:
        profile = user_service.get_user_with_balances(
            db=db,
            user_id=user_id,
        )
    except SQLAlchemyError:
        logger.error("Database error fetching user %d", user_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return profile
