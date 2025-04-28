import base64
import logging

import httpx
from fast_depends import Depends, inject
from socketio import AsyncManager

from infra.brokers.taskiq import broker
from logic import TypedContainer, init_container
from logic.services.xinference import XinferenceService
from logic.tasks.base import PipelineValue

logger = logging.getLogger(__name__)


@inject
async def process_stt(
    b64_content: str, container: TypedContainer = Depends(init_container)
) -> str:
    """Converts base64 encoded audio to text using Xinference service.

    Decodes the base64 audio content and processes it through the
    speech-to-text model.

    :param content: Base64 encoded audio content.
    :param container: Dependency injection container.
    :return: Extracted text from the audio.
    :raises httpx.HTTPError: If communication with Xinference service fails.
    """
    raw_data = base64.b64decode(b64_content)
    xinf_sevice = container.resolve(XinferenceService)
    return await xinf_sevice.speach_to_text(raw_data)


@broker.task(retry_on_error=True)
@inject
async def pipeline_stt_step(
    data: PipelineValue,
    container: TypedContainer = Depends(init_container),
) -> PipelineValue:
    notification_mgr = container.resolve(AsyncManager)

    try:
        text = await process_stt(data.value)
        await notification_mgr.emit(
            "pipeline",
            {"pipeline_id": data.pipeline_id, "data": {"text": text}, "step": "stt"},
            namespace="/",
            room=data.user_id,
        )
        return PipelineValue(
            value=text, user_id=data.user_id, pipeline_id=data.pipeline_id
        )

    except Exception as e:
        logger.error("Process stt error: ")
        logger.exception(e)
        await notification_mgr.emit(
            "pipeline",
            {
                "pipeline_id": data.pipeline_id,
                "step": "stt",
                "status": "error",
            },
            namespace="/",
            room=data.user_id,
        )
        raise


@broker.task(retry_on_error=True)
async def stt(content: str) -> str:
    """Standalone task for speech-to-text conversion.

    Converts audio to text without pipeline integration or notifications.

    :param content: Base64 encoded audio content.
    :return: Extracted text from the audio.
    """
    text = await process_stt(content)
    return text
