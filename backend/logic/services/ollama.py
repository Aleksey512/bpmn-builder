import json
import logging
from dataclasses import dataclass
from typing import Any, NotRequired, TypedDict

import httpx

from logic.services.base import BpmnService, GenerateResponse, Suggestion, Xml
from settings.config import Config
from utils.decorators.retry import async_retry

logger = logging.getLogger(__name__)


class ModelOptions(TypedDict):
    """
    Configuration options for the model generation process.

    :key temperature: Sampling temperature (0-1).
    :key top_p: Top-p sampling value (0-1).
    :key top_k: Top-k sampling value (1-100).
    :key num_ctx: Maximum number of context tokens (1-128000).
    """

    temperature: float  # 0-1
    top_p: float  # 0-1
    top_k: int  # 1-100
    num_ctx: int  # 1-128000


class GenerateRequest(TypedDict):
    """
    Represents a request body for generating output from the model.

    :key model: Model name to use.
    :key system: System prompt or instruction.
    :key prompt: User input prompt.
    :key stream: Whether to stream the response.
    :key options: Generation options.
    :key format: Optional schema format for the expected response.
    """

    model: str
    system: str
    prompt: str
    stream: bool
    options: ModelOptions
    format: NotRequired[dict[str, Any]]


@dataclass
class OllamaService(BpmnService):
    """
    Service for interacting with the Ollama model API.

    :param config: Configuration object containing API settings.
    """

    config: Config

    @property
    def headers(self) -> dict[str, str]:
        """
        Builds and returns HTTP headers required for API requests.

        :return: Dictionary of headers including Content-Type and Accept.
        """
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    async def model_ready(self) -> bool:
        """
        Checks whether the model is available in Ollama.

        :return: True if the model exists and is ready, otherwise False.
        """
        try:
            return await self._model_ready()
        except httpx.HTTPError:
            return False

    async def create_model(self) -> None:
        """
        Pulls and creates the model from Ollama if not already available.

        :return: None
        """
        return await self._create_model()

    @async_retry(3, (httpx.HTTPStatusError, httpx.TimeoutException), 1)
    async def generate_bpmn(self, prompt: str) -> GenerateResponse[Xml]:  # type: ignore
        """
        Generates BPMN XML output from a given prompt.

        :param prompt: Input prompt string.
        :return: A GenerateResponse object containing the generated BPMN XML.
        """
        return await self._generate(prompt)

    async def get_suggestions(self, prompt: str) -> GenerateResponse[list[Suggestion]]:
        """
        Generates suggestions (errors and corrections) from a BPMN diagram prompt.

        :param prompt: Input BPMN XML string or natural language.
        :return: A GenerateResponse containing a list of suggestions.
        """
        return await self._get_suggestions_from_bpmn(prompt)

    async def _model_ready(self) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.config.ollama_url}/api/tags")
            if response.is_error:
                return False
            data = response.json()
            for model in data.get("models", []):
                if model["name"] == self.config.ollama_model:
                    return True
            return False

    async def _create_model(self) -> None:
        async with httpx.AsyncClient(timeout=None) as client:
            ollama_payload = {
                "model": self.config.ollama_model,
            }
            response = await client.post(
                f"{self.config.ollama_url}/api/pull",
                json=ollama_payload,
                headers=self.headers,
            )
            response.raise_for_status()

    async def _generate(self, prompt: str) -> GenerateResponse[Xml]:
        async with httpx.AsyncClient(
            base_url=self.config.ollama_url, timeout=None
        ) as client:
            response = await client.post(
                url="api/generate",
                json=GenerateRequest(
                    model=self.config.ollama_model,
                    system=self.config.generate_bpmn_agent,
                    prompt=prompt,
                    stream=False,
                    options=ModelOptions(
                        temperature=0.7,
                        top_p=0.9,
                        top_k=40,
                        num_ctx=16384
                    ),
                    format={
                        "type": "object",
                        "properties": {
                            "xml": {"type": "string"},
                        },
                        "required": ["xml"],
                    },
                ),
                headers=self.headers,
            )
            response.raise_for_status()
            response = response.json()
            response['response'] = json.loads(response['response'])

            result: GenerateResponse[Xml] = response
            logger.debug(result)
            return result

    async def _get_suggestions_from_bpmn(
        self, prompt: str
    ) -> GenerateResponse[list[Suggestion]]:
        async with httpx.AsyncClient(
            base_url=self.config.ollama_url, timeout=None
        ) as client:
            response = await client.post(
                url="api/generate",
                json=GenerateRequest(
                    model=self.config.ollama_model,
                    system=self.config.suggestions_agent,
                    prompt=prompt,
                    stream=False,
                    options=ModelOptions(
                        temperature=0.7,
                        top_p=0.9,
                        top_k=40,
                        num_ctx=16384
                    ),
                    format={
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "correction": {"type": "string"},
                            },
                            "required": ["error", "correction"],
                        },
                    },
                ),
                headers=self.headers,
            )
            response.raise_for_status()
            response = response.json()
            response['response'] = json.loads(response['response'])

            result: GenerateResponse[list[Suggestion]] = response
            logger.debug(result)
            return result
