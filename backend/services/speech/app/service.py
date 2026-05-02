"""Speech service — ASR (speech-to-text) + TTS (text-to-speech).

Provider abstraction; defaults to stubs that return deterministic payloads
so consumers and CI can round-trip the contract. Plug in real providers
(AI4Bharat IndicWhisper, ElevenLabs, Coqui) by setting ``SPEECH_ASR_PROVIDER``
and ``SPEECH_TTS_PROVIDER`` and wiring the adapter.
"""
from __future__ import annotations

import base64
import hashlib
import os

from backend.shared import ValidationError


SUPPORTED_LANGS = ["hi", "en", "mr", "ta", "te", "bn", "gu", "kn", "ml", "pa"]


def transcribe(audio_b64: str, lang: str) -> dict:
    if lang not in SUPPORTED_LANGS:
        raise ValidationError(f"unsupported lang: {lang}", hint=f"supported: {','.join(SUPPORTED_LANGS)}")
    try:
        raw = base64.b64decode(audio_b64, validate=True)
    except Exception:
        raise ValidationError("audio must be valid base64")
    if not raw:
        raise ValidationError("empty audio")

    provider = os.environ.get("SPEECH_ASR_PROVIDER", "stub")
    # Deterministic stub output — lets callers verify plumbing without real ASR.
    digest = hashlib.sha256(raw).hexdigest()[:16]
    return {
        "provider": provider,
        "lang": lang,
        "bytes": len(raw),
        "transcript": f"[stub:{digest}]",
        "confidence": 0.0 if provider == "stub" else None,
    }


def synthesize(text: str, lang: str, voice: str = "default") -> dict:
    if lang not in SUPPORTED_LANGS:
        raise ValidationError(f"unsupported lang: {lang}")
    if not text or len(text) > 5000:
        raise ValidationError("text must be 1..5000 chars")

    provider = os.environ.get("SPEECH_TTS_PROVIDER", "stub")
    # Stub produces a short deterministic "audio" payload. Clients can
    # verify wiring; real providers will return proper MP3/WAV bytes.
    fake = f"KAILASH-TTS|{lang}|{voice}|{hashlib.sha256(text.encode()).hexdigest()[:16]}".encode()
    return {
        "provider": provider,
        "lang": lang,
        "voice": voice,
        "audio_b64": base64.b64encode(fake).decode(),
        "format": "stub",
    }
