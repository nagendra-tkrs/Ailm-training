from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.services import leave_service


router = APIRouter(
    prefix="/api/employee",
    tags=["Employee Dashboard"]
)


@router.get("/dashboard")
def employee_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns leave balance + pending/approved leaves for the logged-in user."""
    data = leave_service.get_dashboard_data(
        db=db,
        user_id=current_user["user_id"],
    )

    return data
