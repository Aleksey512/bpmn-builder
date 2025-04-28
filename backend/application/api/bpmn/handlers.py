import logging

from fastapi import APIRouter, HTTPException
from taskiq import TaskiqResultTimeoutError

from application.api.bpmn.schemas import (SuggestionsRequest,
                                          SuggestionsResponse,
                                          XmlFromTextRequest, XmlResponse)
from logic.tasks.bpmn_create import bpmn_create
from logic.tasks.bpmn_suggestions import bpmn_get_suggestions

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bpmn", tags=["BPMN"])


@router.post("/from_text", response_model=XmlResponse)
async def create_bpmn_from_text(data: XmlFromTextRequest) -> XmlResponse:
    """
    Create BPMN XML from a text description.
    """
    set_task = await bpmn_create.kiq(data.description, data.bpmn_xml)

    try:
        set_result = await set_task.wait_result(timeout=60, with_logs=True)
    except TaskiqResultTimeoutError:
        logger.critical("Bpmn task timeout error", exc_info=True)
        raise HTTPException(500, "Server error")

    if set_result.is_err:
        logger.critical(set_result.log)
        raise HTTPException(400, "Cannot create BPMN")

    return XmlResponse(bpmn_xml=set_result.return_value)


@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions_from_bpmn(
    data: SuggestionsRequest,
) -> SuggestionsResponse:
    """
    Retrieve suggestions for a given BPMN XML.
    """
    set_task = await bpmn_get_suggestions.kiq(data.bpmn_xml)

    try:
        set_result = await set_task.wait_result(timeout=60, with_logs=True)
    except TaskiqResultTimeoutError:
        logger.critical("Bpmn task timeout error", exc_info=True)
        raise HTTPException(500, "Server error")

    if set_result.is_err:
        logger.critical(set_result.log)
        raise HTTPException(400, "Cannot create BPMN")

    return SuggestionsResponse(suggestions=set_result.return_value)
