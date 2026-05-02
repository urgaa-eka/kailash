import base64

from fastapi.testclient import TestClient
from app.main import app


def test_languages():
    r = TestClient(app).get("/languages")
    assert r.status_code == 200
    assert "hi" in r.json()["data"]["supported"]


def test_asr_stub():
    audio = base64.b64encode(b"fake-audio-bytes").decode()
    r = TestClient(app).post("/asr", json={"audio_b64": audio, "lang": "hi"})
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["lang"] == "hi"
    assert d["transcript"].startswith("[stub:")


def test_asr_bad_lang():
    audio = base64.b64encode(b"x").decode()
    r = TestClient(app).post("/asr", json={"audio_b64": audio, "lang": "xx"})
    assert r.status_code == 422


def test_tts_stub():
    r = TestClient(app).post("/tts", json={"text": "नमस्ते", "lang": "hi"})
    assert r.status_code == 200
    assert r.json()["data"]["format"] == "stub"
