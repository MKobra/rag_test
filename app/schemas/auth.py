from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str | None = Field(default=None, min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: EmailStr
