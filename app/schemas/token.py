from typing import Optional
from pydantic import BaseModel

"""Authentication token schemas.

This module contains Pydantic models for handling JWT token data structures.
"""


class Token(BaseModel):
    """Schema for JWT token response.

    Fields:
        access_token: The encoded JWT access token string
        token_type: The type of token (typically 'bearer')
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for decoded token payload data.

    Fields:
        username: The username extracted from the token (optional)
    """
    username: Optional[str] = None
