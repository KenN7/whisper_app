from fastapi import APIRouter, Depends, HTTPException, status, Form
from pydantic import SecretStr
from .models import User, UserCreate
from db.utils import (
    create_user,
    add_token_to_user,
    get_api_key,
    remove_token_from_user,
    authenticate_user,
)

router = APIRouter(prefix="/users")


@router.post("/signup", response_model=User)
async def signup(user: UserCreate):
    return await create_user(user)


@router.post("/get_user", response_model=User)
async def get_user(user: User = Depends(get_api_key)):
    return user


@router.post("/new_token")
async def new_tokens(
    token_name: str, user: str = Form(...), password: SecretStr = Form(...)
):
    user_obj = await authenticate_user(user, password)  # Authenticate first
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return await add_token_to_user(user_obj, token_name)


@router.post("/remove_token")
async def rem_tokens(token_name: str, user: User = Depends(get_api_key)):
    return await remove_token_from_user(user, token_name)
