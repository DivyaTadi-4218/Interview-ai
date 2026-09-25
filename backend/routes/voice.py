"""
Voice endpoints. By default STT/TTS run entirely client-side in the
browser via the Web Speech API (SpeechRecognition + SpeechSynthesis) —
no server round trip, lowest latency, zero API key needed. These
endpoints exist so a real server-side provider (Whisper, Deepgram,
ElevenLabs, Azure Speech, etc.) can be dropped in later without any
frontend contract change: the frontend already POSTs here first and
only falls back to the Web Speech API if this returns 501.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    # Plug a real STT provider in here (e.g. send `audio` bytes to
    # Whisper/Deepgram) and return {"transcript": "..."}.
    raise HTTPException(
        status_code=501,
        detail="Server-side STT not configured — using client-side Web Speech API.",
    )


@router.post("/speak")
async def speak(text: str):
    # Plug a real TTS provider in here (e.g. ElevenLabs/Azure) and
    # return an audio stream. Until then the frontend uses
    # window.speechSynthesis directly.
    raise HTTPException(
        status_code=501,
        detail="Server-side TTS not configured — using client-side Web Speech API.",
    )
