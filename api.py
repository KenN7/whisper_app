from fastapi import (
    FastAPI,
    Depends,
)
from typing import Annotated, List

from contextlib import asynccontextmanager
from config import config
from db.utils import get_api_key
from users.router import router as user_router
from users.models import User


@asynccontextmanager
async def startup(app: FastAPI):
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

    yield
    # Dynamic Output Selection
    # for output in config["outputs"]:
    #    if output == "notion":
    #        from output_modules import notion


app = FastAPI(lifespan=startup)
# include the user router
app.include_router(user_router)


@app.get("/ping")
async def ping():
    return {"data": "pong"}


@app.get("/protected_ping")
async def protected_data(user: User = Depends(get_api_key)):
    # Only accessible if authentication is successful
    return {
        "secret_data": "This is only for authorized users",
        "user": user,
    }
