from fastapi import FastAPI, BackgroundTasks, File, UploadFile, Query, HTTPException, Depends, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

from config import config
from auth import authenticate_user, create_access_token, get_current_user
from crud import create_user
from models import User, UserCreate, Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Dynamic Input Selection
    for input in config["inputs"]:
        if input == "telegram":
            from input_modules import telegram

            bot = telegram.TelegramBot()
            await bot.init()
            app.include_router(bot.router)

        elif input == "file":
            from input_modules import file

            app.include_router(file.router)

    # Dynamic Output Selection
    #for output in config["outputs"]:
    #    if output == "notion":
    #        from output_modules import notion



@app.get("/ping")
async def ping():
    return {"data": "pong"}

@app.get("/protected_ping")
async def protected_data(current_user: User = Depends(get_current_user)):
    # Only accessible if authentication is successful
    return {"secret_data": "This is only for authorized users", "username": current_user.username} 

@app.post("/signup", response_model=User)
async def signup(user: UserCreate):
    return await create_user(user)

@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
