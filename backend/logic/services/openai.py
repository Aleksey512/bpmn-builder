import json
import logging
from dataclasses import dataclass
from typing import TypedDict

from openai import AsyncOpenAI

from logic.services.base import BpmnService, GenerateResponse, Suggestion, Xml
from settings.config import Config

logger = logging.getLogger(__name__)


class GenerateRequestMessage(TypedDict):
    role: str
    content: str


class GenerateRequest(TypedDict):
    model: str
    messages: list[GenerateRequestMessage]
    temperature: float  # 0-1
    top_p: float  # 0-1
    top_k: int  # 1-100


@dataclass
class OpenAIService(BpmnService):
    config: Config

    @property
    def client(self) -> AsyncOpenAI:
        """
        Instantiates and returns an AsyncOpenAI client.

        :return: An instance of AsyncOpenAI configured with the provided API token
                 and base URL.
        """
        return AsyncOpenAI(
            api_key=self.config.openai_api_token, base_url=self.config.openai_url
        )

    def __post_init__(self) -> None:
        """
        Post-initialization to validate configuration.

        :raises ValueError: If the OpenAI API URL is not provided in the config.
        """
        if not self.config.openai_url:
            raise ValueError("Cannot provide OPENAPI_URL")

    @property
    def headers(self) -> dict[str, str]:
        """
        Builds and returns HTTP headers required for API requests.

        :return: Dictionary of headers including Content-Type and Accept.
        """
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.openai_api_token}",
        }

    async def create_model(self) -> None:
        return

    async def model_ready(self) -> bool:
        """
        Checks whether the OpenAI model is ready to receive requests.

        Currently returns True unconditionally, assuming service readiness.

        :return: True if the model is ready (always in this implementation).
        """
        return True

    async def generate_bpmn(self, prompt: str) -> GenerateResponse[Xml]:
        """
        Generates BPMN XML output from a given prompt.

        :param prompt: Input prompt string.
        :return: A GenerateResponse object containing the generated BPMN XML.
        """
        return await self._generate_bpmn(prompt)

    async def get_suggestions(self, prompt: str) -> GenerateResponse[list[Suggestion]]:
        """
        Generates suggestions (errors and corrections) from a BPMN diagram prompt.

        :param prompt: Input BPMN XML string or natural language.
        :return: A GenerateResponse containing a list of suggestions.
        """
        return await self._get_suggestions(prompt)

    async def _generate_bpmn(self, prompt: str) -> GenerateResponse[Xml]:
        result = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": self.config.generate_bpmn_agent},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "xml_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "xml": {"type": "string"},
                        },
                        "required": ["xml"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        logger.debug(result)
        generated_text = result.choices[0].message.content or "{'xml': ''}"
        xml_data = json.loads(generated_text)["xml"]
        return GenerateResponse[Xml](
            model=self.config.openai_model, response={"xml": xml_data}
        )

    async def _get_suggestions(self, prompt: str) -> GenerateResponse[list[Suggestion]]:
        result = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": self.config.suggestions_agent},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "xml_response",
                    "strict": True,
                    "schema": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "correction": {"type": "string"},
                            },
                            "required": ["error", "correction"],
                            "additionalProperties": False,
                        },
                    },
                },
            },
        )
        generated_text = result.choices[0].message.content or "[]"
        suggestions: list[Suggestion] = json.loads(generated_text)
        logger.debug(result)
        return GenerateResponse[list[Suggestion]](
            model=self.config.openai_model, response=suggestions
        )
