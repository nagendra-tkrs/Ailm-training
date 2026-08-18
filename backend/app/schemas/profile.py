from typing import Optional

from pydantic import BaseModel, Field, field_validator

PHONE_NUMBER_PATTERN = r"^\+[1-9]\d{1,3}\d{10}$"


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(
        None,
        max_length=15,
        pattern=PHONE_NUMBER_PATTERN,
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Only @gmail.com email addresses are allowed")
        return v.lower()


class ResetPasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=12)
