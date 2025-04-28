import base64
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from taskiq import AsyncBroker
from taskiq_pipelines import Pipeline

from application.api.pipeline.schemas import (PipelineResponse,
                                              TextPipelineRequest)
from logic import TypedContainer, init_container
from logic.tasks.base import PipelineValue
from logic.tasks.bpmn_create import pipeline_bpmn_step
from logic.tasks.bpmn_suggestions import pipeline_bpmn_suggestions_step
from logic.tasks.stt import pipeline_stt_step
from logic.tasks.webm_convert import pipeline_webm_covert_step

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/from_file", response_model=PipelineResponse)
async def start_pipeline_from_file(
    user_id: Annotated[str, Query(..., description="User id")],
    file: Annotated[UploadFile, File(description="*.webm speach file")],
    container: TypedContainer = Depends(init_container),
) -> PipelineResponse:
    broker = container.resolve(AsyncBroker)
    if file.content_type != "audio/webm":
        raise HTTPException(400, "Invalid file format")

    content = await file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    pipe = (
        Pipeline(broker, pipeline_webm_covert_step)
        .call_next(pipeline_stt_step)
        .call_next(pipeline_bpmn_step)
        .call_next(pipeline_bpmn_suggestions_step)
    )

    pipeline_id = str(uuid.uuid4())
    await pipe.kiq(
        PipelineValue(value=encoded, user_id=user_id, pipeline_id=pipeline_id)
    )
    return PipelineResponse(pipeline_id=pipeline_id)


@router.post("/from_text", response_model=PipelineResponse)
async def start_pipeline_from_text(
    data: TextPipelineRequest,
    container: TypedContainer = Depends(init_container),
) -> PipelineResponse:
    broker = container.resolve(AsyncBroker)
    pipeline_id = str(uuid.uuid4())

    pipe = Pipeline(broker, pipeline_bpmn_step).call_next(
        pipeline_bpmn_suggestions_step
    )
    await pipe.kiq(
        PipelineValue(value=data.text, user_id=data.user_id, pipeline_id=pipeline_id),
        data.bpmn_xml,
    )
    return PipelineResponse(pipeline_id=pipeline_id)
