import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_employee, require_admin
from app.schemas.leave import ApplyLeaveRequest
from app.services import leave_service

logger = logging.getLogger("app.routes.leaves")

VALID_LEAVE_STATUSES = ("pending", "approved", "rejected")

router = APIRouter(
    prefix="/api/leave",
    tags=["Leaves"]
)


@router.post("")
def apply_leave(
    request: ApplyLeaveRequest,
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        leave, error = leave_service.apply_leave(
            db=db,
            user_id=current_user["user_id"],
            leave_type=request.leaveType,
            start_date=request.startDate,
            end_date=request.endDate,
            days=request.leaveDays,
            reason=request.reason,
        )
    except SQLAlchemyError:
        logger.error("Database error applying leave", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process leave request"
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Leave request submitted successfully",
        "leave": leave_service.serialize_leave(leave),
    }


@router.get("/my")
def my_leaves(
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        leaves = leave_service.get_my_leaves(
            db=db,
            user_id=current_user["user_id"],
        )
    except SQLAlchemyError:
        logger.error("Database error fetching my leaves", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaves"
        )

    return {"leaves": leaves}


@router.get("/all")
def all_leaves(
    status: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if status is not None and status not in VALID_LEAVE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter. Use: {', '.join(VALID_LEAVE_STATUSES)}"
        )

    try:
        leaves = leave_service.get_all_leaves(
            db=db,
            status_filter=status,
        )
    except SQLAlchemyError:
        logger.error("Database error fetching all leaves", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaves"
        )

    return {"leaves": leaves}


@router.put("/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        leave, error = leave_service.decide_leave(
            db=db,
            leave_id=leave_id,
            decision="approved",
        )
    except SQLAlchemyError:
        logger.error("Database error approving leave %d", leave_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve leave"
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Leave request approved",
        "leave": leave_service.serialize_leave(leave),
    }


@router.put("/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        leave, error = leave_service.decide_leave(
            db=db,
            leave_id=leave_id,
            decision="rejected",
        )
    except SQLAlchemyError:
        logger.error("Database error rejecting leave %d", leave_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject leave"
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Leave request rejected",
        "leave": leave_service.serialize_leave(leave),
    }


@router.delete("/{leave_id}")
def delete_leave(
    leave_id: int,
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        error = leave_service.delete_leave(
            db=db,
            leave_id=leave_id,
            user_id=current_user["user_id"],
        )
    except SQLAlchemyError:
        logger.error("Database error deleting leave %d", leave_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete leave"
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {"message": "Leave request deleted successfully"}
