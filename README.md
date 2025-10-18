# Harlie Audio-Visual ChatGPT 5 Companion

Dieses Projekt stellt ein lokales Grundgerüst für einen deutschsprachigen, audio-visuellen Chat-Assistenten bereit. Audio-Eingabe wird in Text transkribiert, mit dem OpenAI-API-Modell beantwortet und anschließend als Videoantwort über D-ID mit einer ElevenLabs-Stimme visualisiert.

## Architektur im Überblick

```
Browser (WebRTC Audio) → FastAPI Backend → OpenAI (Speech-to-Text & Chat) → D-ID (Avatar + ElevenLabs Stimme)
```

- **Frontend**: Einfache Weboberfläche zum Aufnehmen des Mikrofons oder Eingabe von Text sowie zur Anzeige der Videoantwort.
- **Backend**: FastAPI-Server mit Endpunkt `/api/chat` für Audio/Text → Antwort inkl. D-ID Talk.
- **Speicher**: Konversationszustand wird im Arbeitsspeicher gehalten und pro Session-ID fortgeführt.

## Voraussetzungen

1. Python 3.10+
2. Abhängigkeiten aus `requirements.txt`
3. API-Schlüssel für:
   - OpenAI
   - ElevenLabs (Voice-ID erforderlich)
   - D-ID (HTTP Basic Token)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Trage anschließend die API-Schlüssel und ggf. das gewünschte OpenAI-Modell in die `.env` ein. Der Avatar wird standardmäßig aus `Avatar_1.jpg` im Projektverzeichnis geladen. Alternativ kann über `AVATAR_IMAGE_PATH` eine andere Bilddatei hinterlegt werden.

> **Hinweis zu D-ID**: Das `DID_API_KEY` Feld erwartet denselben Base64-kodierten String, den du auch in der offiziellen Dokumentation im Header `Authorization: Basic <token>` verwendest. Viele Konten arbeiten mit der Form `Base64("<key>:")`.

## Start des Servers

```bash
uvicorn app.main:app --reload --port 8000
```

Rufe anschließend `http://localhost:8000` im Browser auf.

## Ablauf einer Anfrage

1. **Aufnahme**: Die Web-App zeichnet Audio (`webm`) über den Browser auf.
2. **Transkription**: Das Backend nutzt `gpt-4o-mini-transcribe`, um Text zu erzeugen.
3. **Chat-Antwort**: Die Konversation wird an das ausgewählte OpenAI-Modell gesendet.
4. **Video-Rendering**: Die Antwort wird an D-ID weitergeleitet, das mithilfe der hinterlegten ElevenLabs-Stimme ein Video rendert.
5. **Ausgabe**: Sobald D-ID den Status `done` meldet, wird das Video im Frontend angezeigt.

## Anpassungen & Erweiterungen

- **Persistenz**: Für produktive Szenarien sollte der Conversation-Store (siehe `app/conversation.py`) durch eine Datenbank ersetzt werden.
- **Sicherheit**: Das Beispiel erlaubt CORS von allen Ursprüngen. Für den Einsatz im Internet sollten die erlaubten Domains eingeschränkt werden.
- **Streaming**: D-ID bietet Streaming-APIs. Das Polling in `app/did_client.py` kann durch WebRTC ersetzt werden, um Latenzzeiten zu verringern.
- **ElevenLabs Audio**: Falls du das Audio separat im Frontend ausgeben möchtest, kannst du neben dem D-ID Video eine weitere Anforderung an die ElevenLabs API stellen und den Audio-Stream direkt zurückgeben.

## Tests

Derzeit sind keine automatisierten Tests enthalten. Du kannst aber die Lauffähigkeit des Codes mit folgendem Befehl prüfen:

```bash
python -m compileall app
```
