from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=12)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Only @gmail.com email addresses are allowed")
        return v.lower()


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=1, max_length=12)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Only @gmail.com email addresses are allowed")
        return v.lower()
