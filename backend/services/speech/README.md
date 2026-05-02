# services/speech

Indic ASR + TTS behind a provider abstraction.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/languages` | Supported language codes. |
| `POST` | `/asr` | `{ audio_b64, lang }` → transcript. |
| `POST` | `/tts` | `{ text, lang, voice }` → base64 audio. |

Providers: set `SPEECH_ASR_PROVIDER=ai4bharat` (IndicWhisper) and
`SPEECH_TTS_PROVIDER=elevenlabs|coqui`. Defaults to deterministic stubs
so CI and offline dev work.
