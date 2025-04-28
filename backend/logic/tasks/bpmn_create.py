import logging

import httpx
from fast_depends import Depends, inject
from socketio import AsyncManager

from infra.brokers.taskiq import broker
from logic import TypedContainer, init_container
from logic.services.base import BpmnService
from logic.tasks.base import PipelineValue

logger = logging.getLogger(__name__)


def bpmn_postprocess(bpmn_xml: str) -> str:
    return bpmn_xml.replace("BMN", "BPMN")


@inject
async def _bpmn_create(
    description: str,
    bpmn_xml: str | None = None,
    container: TypedContainer = Depends(init_container),
) -> str:
    """Generates BPMN XML from description.

    Creates or updates a BPMN diagram based on the provided description.
    Can optionally modify an existing diagram if BPMN XML is provided.

    :param description: Text description of the desired BPMN diagram.
    :param bpmn_xml: Existing BPMN XML to modify (optional).
    :param container: Dependency injection container.
    :return: Generated BPMN XML as string.
    :raises httpx.HTTPError: If communication with Ollama service fails.
    """
    if bpmn_xml:
        bpmn_xml = f"Сделай на основе старой диаграммы {bpmn_xml}"
    else:
        bpmn_xml = ""

    bpmn_service = container.resolve(BpmnService)
    prompt = f"{description}.{bpmn_xml}"
    result = await bpmn_service.generate_bpmn(prompt)
    return bpmn_postprocess(result["response"]["xml"])


@broker.task(retry_on_error=True)
@inject
async def pipeline_bpmn_step(
    data: PipelineValue,
    bpmn_xml: str | None = None,
    container: TypedContainer = Depends(init_container),
) -> PipelineValue:
    notification_mgr = container.resolve(AsyncManager)
    try:
        xml = await _bpmn_create(data.value, bpmn_xml)
        await notification_mgr.emit(
            "pipeline",
            {"pipeline_id": data.pipeline_id, "data": {"xml": xml}, "step": "bpmn"},
            namespace="/",
            room=data.user_id,
        )
        return PipelineValue(
            user_id=data.user_id, pipeline_id=data.pipeline_id, value=xml
        )
    except Exception as e:
        logger.error("Process bpmn create error: ")
        logger.exception(e)
        await notification_mgr.emit(
            "pipeline",
            {
                "pipeline_id": data.pipeline_id,
                "step": "bpmn",
                "status": "error",
            },
            namespace="/",
            room=data.user_id,
        )
        raise


@broker.task(retry_on_error=True)
async def bpmn_create(description: str, bpmn_xml: str | None = None) -> str:
    """Standalone task for BPMN diagram creation.

    Creates BPMN diagram without pipeline integration or notifications.

    :param description: Text description of the desired BPMN diagram.
    :param bpmn_xml: Existing BPMN XML to modify (optional).
    :return: Generated BPMN XML as string.
    """
    xml = await _bpmn_create(description, bpmn_xml)
    return xml
