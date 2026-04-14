import json
import os
import urllib.error
import urllib.request

from services.text_utils import normalize_whitespace


WORD_TARGETS = {
    "short": "45 to 70 words",
    "medium": "80 to 130 words",
    "long": "130 to 190 words",
}


def _extract_output_text(payload: dict) -> str:
    if payload.get("output_text"):
        return normalize_whitespace(payload["output_text"])

    fragments = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                fragments.append(content["text"])
    return normalize_whitespace(" ".join(fragments))


def summarize_with_openai(text: str, length: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    target = WORD_TARGETS.get(length, WORD_TARGETS["medium"])

    prompt = (
        "Summarize the following text.\n"
        f"Return a coherent summary in {target}.\n"
        "Keep the main ideas, remove repetition, and make sure the result is clearly shorter than the input.\n"
        "Use plain prose without bullets unless the source text is already list-based.\n\n"
        f"Text:\n{text}"
    )

    body = {
        "model": model,
        "input": prompt,
        "max_output_tokens": 240,
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None

    return _extract_output_text(payload) or None
