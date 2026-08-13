from datetime import date

from pydantic import BaseModel, Field


class ApplyLeaveRequest(BaseModel):
    leaveType: str = Field(..., min_length=1, max_length=50)
    startDate: date
    endDate: date
    leaveDays: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=1000)
