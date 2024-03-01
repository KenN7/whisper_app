from motor.motor_asyncio import AsyncIOMotorClient
from config import config
from users.models import User, UserCreate
from typing import Optional
from pydantic import SecretStr
from utils import hash_password, verify_password
from bson.objectid import ObjectId
from fastapi import HTTPException, status, Security
import secrets
from fastapi.security.api_key import APIKeyHeader

client = AsyncIOMotorClient(config["mongodburl"])
db = client.whisper
collection = db.users


async def authenticate_user(user: str, password: SecretStr) -> Optional[User]:
    user_obj = await collection.find_one({"username": user})
    if user_obj and verify_password(
        user_obj["hashed_password"], password.get_secret_value()
    ):
        user_obj["hashed_password"] = ""
        return User(**user_obj)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate api key",
    )


async def create_user(user: UserCreate):
    user_exists = await collection.find_one({"username": user.username})
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user_dict = user.model_dump(exclude={"password"})  # Data for User object
    user_dict["hashed_password"] = hash_password(user.password)  # Hash the password
    user_obj = User(**user_dict)
    await collection.insert_one(user_dict)
    return user_obj


def generate_api_key():
    return secrets.token_urlsafe(32)
    # Generates a 32-byte (256-bit) random URL-safe key


async def add_token_to_user(user: User, token_name: str):
    """Adds a new token with a name to the user's tokens dictionary."""
    api_key = generate_api_key()
    user.tokens[api_key] = token_name  # API key as the key, token name as the value

    result = await collection.update_one(
        {"_id": ObjectId(user.id)},  # Convert string ID to ObjectId
        {"$set": {"tokens": user.tokens}},
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return api_key


async def remove_token_from_user(user: User, token_name: str):
    """Removes a token by its name from the user's tokens dictionary."""

    # Find the corresponding api_key based on the token_name
    for api_key, name in user.tokens.items():
        if name == token_name:
            del user.tokens[api_key]
            result = await collection.update_one(
                {"_id": ObjectId(user.id)},  # Convert string ID to ObjectId
                {"$set": {"tokens": user.tokens}},
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User or token not found",
                )
            return  # Token removed successfully

    # If we reach here, the token was not found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Token not found for this user"
    )


api_key_header = APIKeyHeader(name="api_key", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header:
        # Verify the API key (e.g., check if it exists in your database)
        user = await collection.find_one(
            {"tokens." + api_key_header: {"$exists": True}}
        )
        if user:
            user["hashed_password"] = ""
            return User(**user)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate api key",
    )
