from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import get_settings
from .conversation import store
from .did_client import DIDClient, get_did_client
from .openai_client import OpenAIClient, get_openai_client

FRONTEND_DIR = Path("frontend")

app = FastAPI(title="Harlie Audio Visual Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR, html=False), name="frontend")


async def _read_upload_file(file: UploadFile) -> bytes:
    data = await file.read()
    await file.close()
    return data


@app.post("/api/chat")
async def chat(
    conversation_id: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    openai_client: OpenAIClient = Depends(get_openai_client),
    did_client: DIDClient = Depends(get_did_client),
):
    if not audio and not text:
        raise HTTPException(status_code=400, detail="Either audio or text input is required.")

    user_text = text
    if audio:
        audio_bytes = await _read_upload_file(audio)
        filename = audio.filename or "audio.webm"
        mime_type = audio.content_type or "audio/webm"
        user_text = await openai_client.transcribe(filename=filename, data=audio_bytes, mime_type=mime_type)

    if not user_text:
        raise HTTPException(status_code=400, detail="Unable to extract text from the provided input.")

    conversation = store.get(conversation_id)
    if not conversation.messages:
        conversation.append("system", "You are a friendly German speaking AI assistant with knowledge about the project Harlie.")

    conversation.append("user", user_text)
    assistant_text = await openai_client.generate_response(conversation.as_openai_input())
    conversation.append("assistant", assistant_text)

    talk_result = await did_client.create_talk(assistant_text)

    response_payload = {
        "conversationId": conversation.id,
        "transcript": user_text,
        "response": assistant_text,
        "talk": talk_result,
    }
    return JSONResponse(response_payload)


@app.get("/health")
async def health():
    settings = get_settings()
    return {"status": "ok", "model": settings.openai_model}


@app.get("/")
async def index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="Frontend build missing index.html")
    return FileResponse(index_path)
