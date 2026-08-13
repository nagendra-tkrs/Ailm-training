from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.schemas.leave import ApplyLeaveRequest
from app.services import leave_service


router = APIRouter(
    prefix="/api/leave",
    tags=["Leaves"]
)


@router.post("")
def apply_leave(
    request: ApplyLeaveRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.apply_leave(
        db=db,
        user_id=current_user["user_id"],
        leave_type=request.leaveType,
        start_date=request.startDate,
        end_date=request.endDate,
        days=request.leaveDays,
        reason=request.reason,
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leaves = leave_service.get_my_leaves(
        db=db,
        user_id=current_user["user_id"],
    )

    return {"leaves": leaves}


@router.get("/all")
def all_leaves(
    status: Optional[str] = None,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    leaves = leave_service.get_all_leaves(
        db=db,
        status_filter=status,
    )

    return {"leaves": leaves}


@router.put("/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.decide_leave(
        db=db,
        leave_id=leave_id,
        decision="approved",
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
    current_user: dict = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    leave, error = leave_service.decide_leave(
        db=db,
        leave_id=leave_id,
        decision="rejected",
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    error = leave_service.delete_leave(
        db=db,
        leave_id=leave_id,
        user_id=current_user["user_id"],
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {"message": "Leave request deleted successfully"}
