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
    try:
        data = leave_service.get_dashboard_data(
            db=db,
            user_id=current_user["user_id"],
        )

        return data
    except Exception as error:
        # Dev-time: log full traceback to stdout so the server logs show details
        import traceback

        traceback.print_exc()

        # Return a JSON error detail to the client to aid frontend debugging
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=str(error))
