"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Your session is invalid or has expired. Please log in again.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    if not token:
        raise CREDENTIALS_ERROR
    subject = decode_access_token(token)
    if not subject:
        raise CREDENTIALS_ERROR
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise CREDENTIALS_ERROR
    user = db.get(User, user_id)
    if user is None:
        raise CREDENTIALS_ERROR
    return user
