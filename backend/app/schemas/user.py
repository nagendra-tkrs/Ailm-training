from typing import Optional

from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    employee_id: Optional[int] = None
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}
