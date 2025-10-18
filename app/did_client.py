from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx

from .config import get_settings


class DIDClient:
    BASE_URL = "https://api.d-id.com"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._auth_header = {
            "Authorization": f"Basic {self.settings.did_api_key}",
            "Content-Type": "application/json",
        }

    async def create_talk(self, text: str) -> Dict[str, Any]:
        payload = {
            "script": {
                "type": "text",
                "subtitles": False,
                "ssml": False,
                "provider": {
                    "type": "elevenlabs",
                    "voice_id": self.settings.elevenlabs_voice_id,
                },
                "input_text": text,
            },
            "source_image": self.settings.avatar_base64,
        }
        async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=60) as client:
            response = await client.post("/talks", headers=self._auth_header, json=payload)
            response.raise_for_status()
            data = response.json()
            talk_id = data.get("id")
            if not talk_id:
                return data

            for _ in range(self.settings.did_poll_attempts):
                await asyncio.sleep(self.settings.did_poll_interval)
                status_response = await client.get(f"/talks/{talk_id}", headers=self._auth_header)
                status_response.raise_for_status()
                status_data = status_response.json()
                status = status_data.get("status")
                if status in {"done", "error"}:
                    return status_data

        return {"status": "timeout", "id": talk_id}


def get_did_client() -> DIDClient:
    return DIDClient()
