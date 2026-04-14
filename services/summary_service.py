from services.extractive_summarizer import LENGTH_PROFILES, summarize_extractive
from services.openai_summarizer import summarize_with_openai
from services.text_utils import normalize_whitespace, split_sentences, word_count


def _allowed_ratio(length: str) -> float:
    profile = LENGTH_PROFILES.get(length, LENGTH_PROFILES["medium"])
    return min(profile["ratio"] + 0.12, 0.7)


def _sanitize_summary(summary: str) -> str:
    cleaned = normalize_whitespace(summary)
    if cleaned.endswith(":"):
        cleaned = cleaned[:-1].strip()
    return cleaned


def summary_is_meaningfully_shorter(original: str, summary: str, length: str) -> bool:
    original_words = word_count(original)
    summary_words = word_count(summary)

    if original_words == 0 or summary_words == 0:
        return False
    if summary_words >= original_words:
        return False
    if summary_words > max(20, int(original_words * _allowed_ratio(length))):
        return False

    original_sentences = split_sentences(original)
    summary_sentences = split_sentences(summary)
    if len(summary_sentences) > len(original_sentences):
        return False

    return True


def generate_summary(text: str, length: str) -> dict:
    cleaned_text = normalize_whitespace(text)
    summary = summarize_with_openai(cleaned_text, length)
    provider = "openai"

    if not summary or not summary_is_meaningfully_shorter(cleaned_text, summary, length):
        summary = summarize_extractive(cleaned_text, length)
        provider = "extractive-fallback"

    summary = _sanitize_summary(summary)
    if not summary_is_meaningfully_shorter(cleaned_text, summary, length):
        fallback_sentences = split_sentences(summary)
        summary = " ".join(fallback_sentences[: max(1, len(fallback_sentences) - 1)]) or summary
        summary = _sanitize_summary(summary)

    return {
        "summary": summary,
        "provider": provider,
        "input_word_count": word_count(cleaned_text),
        "output_word_count": word_count(summary),
        "compression_ratio": round(word_count(summary) / max(word_count(cleaned_text), 1), 2),
    }
