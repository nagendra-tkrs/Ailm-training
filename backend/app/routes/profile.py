from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.profile import UpdateProfileRequest, ResetPasswordRequest
from app.services import profile_service


router = APIRouter(
    prefix="/api/profile",
    tags=["Employee Profile"]
)


def _raise_error(error: dict):
    raise HTTPException(
        status_code=error["status_code"],
        detail=error["detail"],
    )


@router.get("")
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile, error = profile_service.get_profile(
        db=db,
        user_id=current_user["user_id"],
    )

    if error:
        _raise_error(error)

    return profile


@router.put("")
def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile, error = profile_service.update_profile(
        db=db,
        user_id=current_user["user_id"],
        name=request.name,
        email=request.email,
        address=request.address,
        phone_number=request.phone_number,
    )

    if error:
        _raise_error(error)

    return profile


@router.put("/password")
def reset_password(
    request: ResetPasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    error = profile_service.reset_password(
        db=db,
        user_id=current_user["user_id"],
        current_password=request.current_password,
        new_password=request.new_password,
    )

    if error:
        _raise_error(error)

    return {"message": "Password updated successfully"}
