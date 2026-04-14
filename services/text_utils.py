import re


def load_env_file(path: str = ".env") -> None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                if key:
                    import os

                    os.environ.setdefault(key, value)
    except FileNotFoundError:
        return


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def split_sentences(text: str) -> list[str]:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def word_count(text: str) -> int:
    return len(tokenize(text))


def clip_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."
