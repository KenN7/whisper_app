from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from config import config
from models import User
from crud import get_user
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

async def authenticate_user(username: str, password: str):
    user = await get_user(username=username)
    if not user or not user.verify_password(password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config['secretkey'], algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Decodes the JWT token, verifies the user exists, and returns the current user.

    Args:
        token: The JWT token dependency.

    Returns:
        The User object of the authenticated user, or None if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config['secretkey'], algorithms='HS256')
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await get_user(username=username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception 
