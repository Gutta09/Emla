import httpx
from app.config import settings

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"


def _fallback(signs: list[str]) -> str:
    return " ".join(s.replace("_", " ").lower().capitalize() for s in signs) + "."


async def signs_to_sentence(signs: list[str]) -> str:
    """Convert a sequence of ASL sign labels to natural English via Gemini."""
    if not signs:
        return ""

    if not settings.gemini_api_key:
        return _fallback(signs)

    prompt = (
        f"Convert these ASL signs to natural English: {' '.join(signs)}\n\n"
        "Rules:\n"
        "- Output ONLY the final sentence, nothing else\n"
        "- Fill in articles (a, the), prepositions, and verb conjugations naturally\n"
        "- Keep the meaning faithful to the signs\n"
        "- Capitalize properly and end with a period"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                GEMINI_URL,
                params={"key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return _fallback(signs)
