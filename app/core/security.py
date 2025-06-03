from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.db.database import get_db
from app.db.models import User
from app.schemas.token import TokenData

"""Security and authentication utilities.

This module provides:
- Password hashing and verification
- JWT token creation and validation
- User authentication and authorization
- Role-based permission checks
- Audit logging functionality
"""

# Load environment variables
load_dotenv()

# Get security settings from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def verify_password(plain_password, hashed_password):
    """Verify if a plain text password matches the hashed version.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The stored hashed password

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generate a secure hash of a password.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user with username and password.

    Args:
        db: Database session
        username: User's username
        password: User's plain text password

    Returns:
        User: The authenticated user object if successful
        bool: False if authentication fails

    Side Effects:
        Updates failed_attempts counter and last_login timestamp
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        # Increment failed login attempts
        user.failed_attempts += 1
        db.commit()
        return False
    # Check if user is active
    if not user.is_active:
        return False
    ##Reset failed attempts and update last login
    user.failed_attempts = 0
    user.last_login = datetime.utcnow()
    db.commit()
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token with expiration.

    Args:
        data: Dictionary containing token claims (must include 'sub')
        expires_delta: Optional timedelta for token expiration

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieve and validate the current user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: 401 if invalid credentials or inactive user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Verify and return the current active user.

    Args:
        current_user: User object from get_current_user

    Returns:
        User: The active user

    Raises:
        HTTPException: 400 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def is_admin(current_user: User = Depends(get_current_user)):
    """Check if current user has admin role.

    Args:
        current_user: User object from get_current_user

    Returns:
        User: The admin user

    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


def is_manager_or_admin(current_user: User = Depends(get_current_user)):
    """Check if current user has manager or admin role.

    Args:
        current_user: User object from get_current_user

    Returns:
        User: The authorized user

    Raises:
        HTTPException: 403 if user lacks required role
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


def create_audit_log(db: Session, user_id: str, action: str, entity_type: str, 
                    entity_id: str, details: dict = None, ip_address: str = None, 
                    user_agent: str = None):
    """Create an audit log entry for security tracking.

    Args:
        db: Database session
        user_id: ID of user performing the action
        action: Type of action performed
        entity_type: Type of entity affected
        entity_id: ID of entity affected
        details: Optional additional details as dict
        ip_address: Optional IP address of requester
        user_agent: Optional user agent string

    Returns:
        AuditLog: The created audit log entry
    """
    from app.db.models import AuditLog
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    return audit_log
