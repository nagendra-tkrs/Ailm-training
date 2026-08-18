from typing import Literal, Optional

from pydantic import BaseModel, Field


class ApplyLeaveRequest(BaseModel):
    leaveType: Literal["CASUAL", "SICK", "EARNED"] = Field(...)
    startDate: str = Field(..., min_length=1)
    endDate: str = Field(..., min_length=1)
    leaveDays: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=1000)
