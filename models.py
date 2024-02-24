from pydantic import BaseModel, Field
import bcrypt

class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: str | None = None

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    hashed_password: str

    def verify_password(self, plain_password):
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password = self.hashed_password.encode('utf-8')
        return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)

def hash_password(plain_password):
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')


class Token(BaseModel):
    access_token: str
    token_type: str 
