from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, Field
from typing import Optional
import re

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        pwd = value

        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", pwd):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
            raise ValueError("Password must contain at least one special character")

        return value

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        pwd = value

        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", pwd):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
            raise ValueError("Password must contain at least one special character")

        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Refresh functionality will be added later.
class TokenWithRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

