from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)


class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
