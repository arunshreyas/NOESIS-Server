# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def _password_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 4096:
            raise ValueError("Password too long (max 4096 bytes)")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def _password_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 4096:
            raise ValueError("Password too long (max 4096 bytes)")
        return v

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
