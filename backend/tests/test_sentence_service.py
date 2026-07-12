import asyncio

from app.services.sentence_service import _fallback, signs_to_sentence
from app import config


def test_fallback_humanizes_underscored_labels():
    assert _fallback(["HELLO", "MY", "NAME"]) == "Hello My Name."
    assert _fallback(["THANK_YOU"]) == "Thank you."


def test_empty_signs_return_empty_string():
    assert asyncio.run(signs_to_sentence([])) == ""


def test_uses_deterministic_fallback_when_no_key(monkeypatch):
    monkeypatch.setattr(config.settings, "gemini_api_key", "", raising=False)
    out = asyncio.run(signs_to_sentence(["GOOD", "MORNING"]))
    assert out == "Good Morning."
