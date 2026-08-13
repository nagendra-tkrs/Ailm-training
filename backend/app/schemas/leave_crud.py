from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateLeaveRequest(BaseModel):
    leave_type: Literal["CASUAL", "SICK", "EARNED"]
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1, max_length=1000)


class UpdateLeaveRequest(BaseModel):
    leave_type: Literal["CASUAL", "SICK", "EARNED"]
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1, max_length=1000)


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    leave_days: int
    reason: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
