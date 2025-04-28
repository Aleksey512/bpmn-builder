import logging
from dataclasses import dataclass
from typing import cast

import httpx

from settings.config import Config
from utils.decorators.retry import async_retry

logger = logging.getLogger(__name__)


@dataclass
class XinferenceService:
    """
    Service for interacting with the Xinference audio model API.

    :param config: Configuration object that holds Xinference settings.
    """

    config: Config

    async def model_ready(self) -> bool:
        """
        Checks whether the configured audio model is available and loaded in Xinference.

        :return: True if the model is found, otherwise False.
        """
        try:
            return await self._get_model()
        except httpx.HTTPError:
            return False

    async def create_xinference_model(self) -> None:
        """
        Ensures the audio model is created and available in Xinference.
        If the model already exists, it does nothing.

        :return: None
        """
        if await self._get_model():
            return
        await self._create_model()

    @async_retry(3, httpx.TimeoutException, 1)
    async def speach_to_text(self, raw_file: bytes) -> str:
        """
        Transcribes speech from the given raw audio file using the Xinference model.

        :param raw_file: Raw bytes of the audio file.
        :return: Transcribed text from the audio.
        """
        return await self._stt(raw_file)

    async def _get_model(self) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.config.xinference_url}/v1/models",
            )
            if not response.is_success:
                return False
            data = response.json()
            for model in data.get("data", []):
                if model.get("model_name", None) == self.config.xinference_model:
                    return True
            return False

    async def _create_model(self) -> None:
        async with httpx.AsyncClient(timeout=None) as client:
            xinference_payload = {
                "model_name": self.config.xinference_model,
                "model_type": "audio",
                "replica": self.config.xinference_model_replica,
                "n_gpu": self.config.xinference_n_gpu,
            }
            response = await client.post(
                f"{self.config.xinference_url}/v1/models",
                json=xinference_payload,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

    async def _stt(self, raw_file: bytes) -> str:
        async with httpx.AsyncClient(
            base_url=self.config.xinference_url, timeout=10
        ) as client:
            response = await client.post(
                url="v1/audio/transcriptions",
                data={"model": self.config.xinference_model},
                files={"file": raw_file},
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(result)
            return cast(str, result["text"].strip())
