from typing import Optional

from pydantic import BaseModel, Field

from logic.services.base import Suggestion


class XmlFromTextRequest(BaseModel):
    description: str
    bpmn_xml: Optional[str] = Field(default=None)


class XmlResponse(BaseModel):
    bpmn_xml: str


class SuggestionsRequest(BaseModel):
    bpmn_xml: str


class SuggestionsResponse(BaseModel):
    suggestions: list[Suggestion]
