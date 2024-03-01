from pydantic import BaseModel, Field, BeforeValidator
from typing import Annotated, Optional, Dict
from bson import ObjectId
from bson.errors import InvalidId

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: str | None = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    tokens: Dict[str, str] = Field(default={})

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda oid: str(oid)  # Convert ObjectId instances to strings
        }
