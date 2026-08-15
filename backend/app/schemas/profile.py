from typing import Optional

from pydantic import BaseModel, EmailStr, Field

# Country code (1-3 digits, starting with +) followed by exactly 10 digits.
# Example: +919876543210
PHONE_NUMBER_PATTERN = r"^\+[1-9]\d{1,3}\d{10}$"


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(
        None,
        max_length=15,
        pattern=PHONE_NUMBER_PATTERN,
    )


class ResetPasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
