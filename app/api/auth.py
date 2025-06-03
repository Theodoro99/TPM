from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.database import get_db
from app.db.models import User
from app.schemas.token import Token
from app.schemas.user import User as UserSchema

"""Authentication routes for the API.

This module provides endpoints for user authentication and token management.
Includes functionality for obtaining access tokens and retrieving current user information.
"""

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and generate an access token.

    This endpoint validates user credentials and returns a JWT access token
    for authenticating subsequent requests.

    Args:
        form_data: OAuth2 password request form containing username and password.
        db: SQLAlchemy database session.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: 401 Unauthorized if authentication fails.
    """

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Retrieve information about the currently authenticated user.

    This endpoint returns details of the user associated with the provided
    JWT token in the Authorization header.

    Args:
        current_user: The authenticated user (automatically retrieved from the JWT token).

    Returns:
        User: The user object containing user details.
    """

    return current_user
