from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ApplyLeaveRequest(BaseModel):
    leaveType: Literal["CASUAL", "SICK", "EARNED"] = Field(...)
    startDate: date
    endDate: date
    leaveDays: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=1000)
