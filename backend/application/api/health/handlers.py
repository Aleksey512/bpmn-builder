import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from logic import TypedContainer, init_container
from logic.services.base import BpmnService
from logic.services.xinference import XinferenceService

router = APIRouter(tags=["Health"])


@router.get(
    path="/healthz",
    description="Endpoint to get a status of application",
)
async def health_check(
    container: TypedContainer = Depends(init_container),
) -> dict[str, str]:
    """
    Health check endpoint for the application.
    """
    bpmn_service = container.resolve(BpmnService)
    xinf_service = container.resolve(XinferenceService)

    bpmn_task = asyncio.create_task(bpmn_service.model_ready())
    xinf_task = asyncio.create_task(xinf_service.model_ready())

    ollama_ready, xinf_ready = await asyncio.gather(bpmn_task, xinf_task)

    if ollama_ready and xinf_ready:
        return {"status": "healthy"}

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="One or more services are not ready",
    )


@router.get(
    path="/readiness",
    description="Endpoint to get a status of application",
)
async def readiness_check() -> dict[str, str]:
    """
    Readiness check endpoint for the application.
    """
    return {"status": "ready"}
