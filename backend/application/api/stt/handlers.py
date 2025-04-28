import base64
import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from taskiq import TaskiqResultTimeoutError

from application.api.stt.schemas import UploadAudioResponseSchema
from logic.tasks.stt import stt
from logic.tasks.webm_convert import webm_convert

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stt", tags=["Speech-To-Text"])


@router.post("/upload_audio", response_model=UploadAudioResponseSchema)
async def get_text_from_audio(
    file: Annotated[UploadFile, File(description="*.webm speach file")],
) -> UploadAudioResponseSchema:
    """
    Converts an uploaded `.webm` audio file into text.
    """
    if file.content_type != "audio/webm":
        raise HTTPException(400, "Invalid file format")

    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")

    try:
        set_webm_task = await webm_convert.kiq(encoded)
        encoded_content = await set_webm_task.wait_result(timeout=30, with_logs=True)
        set_stt_task = await stt.kiq(encoded_content.return_value)
        set_result = await set_stt_task.wait_result(timeout=60, with_logs=True)
    except TaskiqResultTimeoutError:
        logger.critical("STT task timeout error", exc_info=True)
        raise HTTPException(500, "Server error")

    if set_result.is_err:
        logger.critical(set_result.log)
        raise HTTPException(400, "Cannot convert audio to text")

    return UploadAudioResponseSchema(text=set_result.return_value)
