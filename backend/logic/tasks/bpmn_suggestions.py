import logging

import httpx
from fast_depends import Depends, inject
from socketio import AsyncManager

from infra.brokers.taskiq import broker
from logic import TypedContainer, init_container
from logic.services.base import BpmnService, Suggestion
from logic.tasks.base import PipelineValue

logger = logging.getLogger(__name__)


@inject
async def _bpmn_validate(
    xml: str, container: TypedContainer = Depends(init_container)
) -> list[Suggestion]:
    """Validates BPMN XML and generates improvement suggestions.

    Analyzes the provided BPMN diagram and returns a list of suggestions
    containing errors and their potential corrections.

    :param xml: BPMN diagram in XML format to analyze.
    :param container: Dependency injection container.
    :return: List of Suggestion objects containing errors and corrections.
    :raises httpx.HTTPError: If communication with Ollama service fails.
    """
    bpmn_service = container.resolve(BpmnService)
    prompt = (
        "Проанализируй BPMN диаграмму для bpmn-js в формате xml"
        "и верни ошибки error и способ эту ошибку исправить correction."
        f"BPMN XML: {xml}"
    )
    suggest_data = await bpmn_service.get_suggestions(prompt)
    suggestions_objects: list[Suggestion] = suggest_data["response"]

    return suggestions_objects


@broker.task(retry_on_error=True)
@inject
async def pipeline_bpmn_suggestions_step(
    data: PipelineValue,
    container: TypedContainer = Depends(init_container),
) -> PipelineValue:
    notification_mgr = container.resolve(AsyncManager)
    try:
        suggestions = await _bpmn_validate(data.value)
        await notification_mgr.emit(
            "pipeline",
            {
                "pipeline_id": data.pipeline_id,
                "data": {"suggestions": suggestions},
                "step": "suggestions",
            },
            namespace="/",
            room=data.user_id,
        )
        return PipelineValue(
            user_id=data.user_id, pipeline_id=data.pipeline_id, value=suggestions
        )
    except Exception as e:
        logger.error("Process suggestions error: ")
        logger.exception(e)
        await notification_mgr.emit(
            "pipeline",
            {
                "pipeline_id": data.pipeline_id,
                "step": "suggestions",
                "status": "error",
            },
            namespace="/",
            room=data.user_id,
        )
        raise


@broker.task(retry_on_error=True)
async def bpmn_get_suggestions(context: str) -> list[Suggestion]:
    """Standalone task for BPMN validation.

    Validates BPMN diagram without pipeline integration or notifications.

    :param context: BPMN diagram in XML format to validate.
    :return: List of Suggestion objects containing errors and corrections.
    """
    return await _bpmn_validate(context)
