from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str
    role: str = "technician"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserPasswordReset(BaseModel):
    token: str
    new_password: str


class UserInDB(UserBase):
    id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDB):
    pass
