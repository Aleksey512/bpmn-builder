import base64
import io
import logging

import httpx
from fast_depends import Depends, inject
from pydub import AudioSegment
from socketio import AsyncManager

from infra.brokers.taskiq import broker
from logic import TypedContainer, init_container
from logic.tasks.base import PipelineValue

logger = logging.getLogger(__name__)


def process_webm_convert(b64_content: str) -> str:
    """Converts WebM audio to base64-encoded WAV format.

    Processes the input WebM audio bytes, converts to WAV format,
    and returns as base64 encoded string.

    :param content: Raw bytes of WebM audio file.
    :return: Base64 encoded WAV audio content.
    :raises Exception: If audio conversion fails.
    """
    decoded = base64.b64decode(b64_content)
    webm_buf = io.BytesIO(decoded)
    audio = AudioSegment.from_file(webm_buf, format="webm")
    wav_buf = io.BytesIO()
    audio.export(wav_buf, format="wav")
    wav_buf.seek(0)
    encoded_content = base64.b64encode(wav_buf.getvalue()).decode("utf-8")
    return encoded_content


@broker.task(retry_on_error=True)
@inject
async def pipeline_webm_covert_step(
    data: PipelineValue,
    container: TypedContainer = Depends(init_container),
) -> PipelineValue:
    notification_mgr = container.resolve(AsyncManager)

    try:
        encoded_content = process_webm_convert(data.value)
        return PipelineValue(
            value=encoded_content, user_id=data.user_id, pipeline_id=data.pipeline_id
        )
    except Exception as e:
        logger.error("Process webm convert error: ")
        logger.exception(e)
        await notification_mgr.emit(
            "pipeline",
            {
                "pipeline_id": data.pipeline_id,
                "step": "webm_convert",
                "status": "error",
            },
            namespace="/",
            room=data.user_id,
        )
        raise


@broker.task(retry_on_error=True)
async def webm_convert(b64_content: str) -> str:
    """Standalone task for WebM audio conversion.

    Converts WebM to base64-encoded WAV without pipeline integration.

    :param content: Raw bytes of WebM audio file.
    :return: Base64 encoded WAV audio content.
    """
    encoded_content = process_webm_convert(b64_content)
    return encoded_content
