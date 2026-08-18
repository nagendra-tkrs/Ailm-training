import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_employee
from app.schemas.leave_crud import (
    CreateLeaveRequest,
    UpdateLeaveRequest,
)
from app.services import leave_service

logger = logging.getLogger("app.routes.leaves_crud")

router = APIRouter(
    prefix="/api/leaves",
    tags=["Leaves CRUD"]
)


def _raise_error(error: dict):
    raise HTTPException(
        status_code=error["status_code"],
        detail=error["detail"],
    )


@router.post("")
def create_leave(
    request: CreateLeaveRequest,
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        leave, error = leave_service.create_leave(
            db=db,
            user_id=current_user["user_id"],
            leave_type=request.leave_type,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason,
        )
    except SQLAlchemyError:
        logger.error("Database error creating leave", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create leave request"
        )

    if error:
        _raise_error(error)

    return leave_service.serialize_leave_spec(leave)


@router.get("")
def list_leaves(
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        leaves = leave_service.list_employee_leaves(
            db=db,
            user_id=current_user["user_id"],
        )
    except SQLAlchemyError:
        logger.error("Database error listing leaves", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaves"
        )

    return [
        leave_service.serialize_leave_spec(leave)
        for leave in leaves
    ]


@router.put("/{leave_id}")
def update_leave(
    leave_id: int,
    request: UpdateLeaveRequest,
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        leave, error = leave_service.update_leave(
            db=db,
            user_id=current_user["user_id"],
            leave_id=leave_id,
            leave_type=request.leave_type,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason,
        )
    except SQLAlchemyError:
        logger.error("Database error updating leave %d", leave_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update leave request"
        )

    if error:
        _raise_error(error)

    return leave_service.serialize_leave_spec(leave)


@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        error = leave_service.delete_employee_leave(
            db=db,
            user_id=current_user["user_id"],
            leave_id=leave_id,
        )
    except SQLAlchemyError:
        logger.error("Database error deleting leave %d", leave_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete leave request"
        )

    if error:
        _raise_error(error)

    return {"message": "Leave request deleted successfully"}
