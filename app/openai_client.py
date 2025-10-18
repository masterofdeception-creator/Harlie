from __future__ import annotations

import io
from typing import Iterable, List

from openai import AsyncOpenAI

from .config import get_settings


class OpenAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def transcribe(self, *, filename: str, data: bytes, mime_type: str) -> str:
        file_obj = (filename, io.BytesIO(data), mime_type)
        response = await self.client.audio.transcriptions.create(
            model=self.settings.openai_transcription_model,
            file=file_obj,
        )
        return response.text

    async def generate_response(self, messages: List[dict]) -> str:
        response = await self.client.responses.create(
            model=self.settings.openai_model,
            input=[{"role": message["role"], "content": message["content"]} for message in messages],
        )
        return response.output_text


def get_openai_client() -> OpenAIClient:
    return OpenAIClient()
