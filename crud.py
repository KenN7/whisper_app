from motor.motor_asyncio import AsyncIOMotorClient
from models import UserCreate, User, hash_password
from config import config
from typing import Optional 
from bson.objectid import ObjectId 

client = AsyncIOMotorClient(config['mongodburl'])
db = client.whisper
collection = db.users

async def create_user(user: UserCreate):
    user_dict = user.dict(exclude={"password"})  # Data for User object
    user_dict["hashed_password"] = hash_password(user.password)  # Hash the password
    user_obj = User(**user_dict)
    await collection.insert_one(user_obj.dict())
    return user_obj

async def get_user(username: str) -> Optional[User]:
    """
    Fetches a user from the database based on their username.

    Args:
        username: The username of the user to retrieve.

    Returns:
        A User object if the user is found, otherwise None.
    """
    user = await collection.find_one({"username": username})
    if user:
        return User(**user)
    else:
        return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Fetches a user from the database based on their MongoDB _id.

    Args: 
        user_id: The MongoDB _id of the user to retrieve.

    Returns:
        A User object if the user is found, otherwise None.
    """
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(**user)
        else:
            return None 
    except:  # Catch potential errors with ObjectId conversion
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
