from __future__ import annotations

import base64
import os
import pathlib
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_transcription_model: str = "gpt-4o-mini-transcribe"
    elevenlabs_voice_id: str
    did_api_key: str
    avatar_image_path: pathlib.Path = pathlib.Path("Avatar_1.jpg")
    did_poll_interval: float = 1.5
    did_poll_attempts: int = 20

    @property
    def avatar_base64(self) -> str:
        path = self.avatar_image_path
        if not path.exists():
            raise FileNotFoundError(f"Avatar image not found at {path.resolve()}")
        mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        with path.open("rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime};base64,{encoded}"


@lru_cache()
def get_settings() -> Settings:
    env_map = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", Settings.model_fields["openai_model"].default),
        "openai_transcription_model": os.getenv(
            "OPENAI_TRANSCRIPTION_MODEL", Settings.model_fields["openai_transcription_model"].default
        ),
        "elevenlabs_voice_id": os.getenv("ELEVENLABS_VOICE_ID"),
        "did_api_key": os.getenv("DID_API_KEY"),
        "avatar_image_path": pathlib.Path(os.getenv("AVATAR_IMAGE_PATH", "Avatar_1.jpg")),
        "did_poll_interval": float(os.getenv("DID_POLL_INTERVAL", Settings.model_fields["did_poll_interval"].default)),
        "did_poll_attempts": int(os.getenv("DID_POLL_ATTEMPTS", Settings.model_fields["did_poll_attempts"].default)),
    }
    missing = [key for key, value in env_map.items() if value in (None, "") and key not in {"openai_model", "openai_transcription_model", "avatar_image_path", "did_poll_interval", "did_poll_attempts"}]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return Settings(**env_map)
