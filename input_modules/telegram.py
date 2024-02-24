from typing import Dict, List, Annotated, Union
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Query, Header  # Add Query
from pydantic import Json
from fastapi import HTTPException
import telegram
from telegram import Update
from config import config
from transcribe.fasterwhisper import transcribe_file_fast


class TelegramBot:
    def __init__(self) -> None:
        self.token = f"{config['inputs']['telegram']['token']}"
        self.bot = telegram.Bot(self.token)
        self.router = APIRouter(prefix="/telegram")  # Add router with a prefix
        self.router.add_api_route("/webhook/{token}/", self.handle_telegram_update, methods=["POST"])

    async def init(self) -> None:
        await self.bot.initialize()
        await self.bot.set_webhook(f"{config['baseurl']}/telegram/webhook/{self.token}/")

    async def __del__(self) -> None:
        await self.bot.shutdown()

    async def handle_telegram_update(
        self,
        background_tasks: BackgroundTasks,
        updates: List[Dict],
        token: str,
    ):
        if token != self.token:
            raise HTTPException(status_code=401, detail="Unauthorized")
        try:
            updates = Update.de_list(updates, self.bot)
            for update in updates:
                file_location = f"temp/{update.message.voice.file_unique_id}"
                f = await update.message.voice.get_file()
                await f.download_to_drive(file_location)
                text = transcribe_file_fast(file_location)
                await update.message.reply_text(text)
            return text
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Failed to process Telegram data")
