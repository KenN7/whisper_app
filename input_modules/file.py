from typing import Dict, List, Annotated, Union
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, Query, Header, Depends 
from fastapi import HTTPException
from transcribe.fasterwhisper import transcribe_file_fast
from models import User
from auth import get_current_user

router = APIRouter(prefix="/file")


@router.post("/")
async def handle_file_upload(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile,
    model: str = "small",
    current_user: User = Depends(get_current_user),
):
    # ... access file contents from audio_file
    location = await get_audio_data(audio_file)
    try:
        text = transcribe_file_fast(location, model)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to process audio file")


async def get_audio_data(audio_file: UploadFile):
    #  Assuming simple processing when input_type is 'file'
    file_location = f"temp/{audio_file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(audio_file.file.read())
    return file_location  # Return appropriate data for transcription
