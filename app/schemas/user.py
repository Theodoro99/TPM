from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

"""User management schemas.

This module contains Pydantic models for handling user data structures,
including creation, updates, and authentication-related operations.
"""

class UserBase(BaseModel):
    """Base schema for user data containing common fields.

    Fields:
        username: Unique username identifier
        email: User's email address
        full_name: User's complete name
        department: Department affiliation (optional)
        phone_number: Contact number (optional)
        is_active: Account activation status (default: True)
    """
    username: str
    email: EmailStr
    full_name: str
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating new users (extends UserBase).

    Fields:
        password: Plain text password for authentication
        role: User's role/privilege level (default: 'technician')
    """

    password: str
    role: str = "technician"


class UserUpdate(BaseModel):
    """Schema for updating existing user information.

    Fields (all optional):
        email: New email address
        full_name: Updated full name
        department: Updated department
        phone_number: New phone number
        is_active: New activation status
        role: New role/privilege level
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Schema for password change requests.

    Fields:
        current_password: Existing password for verification
        new_password: Desired new password
    """
    current_password: str
    new_password: str


class UserPasswordReset(BaseModel):
    """Schema for password reset operations.

    Fields:
        token: Password reset verification token
        new_password: Desired new password
    """

    token: str
    new_password: str


class UserInDB(UserBase):
    """Complete user schema including database fields.

    Fields:
        id: Unique user identifier (UUID)
        role: User's role/privilege level
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Most recent login timestamp (optional)
    """

    id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDB):
    """Public-facing user schema (alias of UserInDB)."""
    pass
