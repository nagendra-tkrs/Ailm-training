from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import require_employee
from app.services import leave_service


router = APIRouter(
    prefix="/api/employee",
    tags=["Employee Dashboard"]
)


@router.get("/dashboard")
def employee_dashboard(
    current_user: dict = Depends(require_employee),
    db: Session = Depends(get_db)
):
    try:
        data = leave_service.get_dashboard_data(
            db=db,
            user_id=current_user["user_id"],
        )

        return data
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
