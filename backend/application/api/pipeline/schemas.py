from typing import Optional

from pydantic import BaseModel, Field


class PipelineResponse(BaseModel):
    pipeline_id: str


class TextPipelineRequest(BaseModel):
    user_id: str
    text: str
    bpmn_xml: Optional[str] = Field(default=None)
