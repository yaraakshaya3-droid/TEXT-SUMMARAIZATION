import math
from collections import Counter

from services.text_utils import normalize_whitespace, split_sentences, tokenize, word_count


STOP_WORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}

LENGTH_PROFILES = {
    "short": {"ratio": 0.18, "min_sentences": 2, "max_sentences": 3, "target_words": 70},
    "medium": {"ratio": 0.3, "min_sentences": 3, "max_sentences": 5, "target_words": 120},
    "long": {"ratio": 0.45, "min_sentences": 4, "max_sentences": 7, "target_words": 180},
}


def _profile(length: str) -> dict:
    return LENGTH_PROFILES.get(length, LENGTH_PROFILES["medium"])


def _best_sentence_count(total_sentences: int, length: str) -> int:
    profile = _profile(length)
    ratio_count = max(1, math.ceil(total_sentences * profile["ratio"]))
    return max(profile["min_sentences"], min(profile["max_sentences"], ratio_count))


def _compress_to_budget(summary: str, length: str) -> str:
    profile = _profile(length)
    budget = profile["target_words"]
    summary_sentences = split_sentences(summary)

    if word_count(summary) <= budget or len(summary_sentences) <= 1:
        return normalize_whitespace(summary)

    kept_sentences = []
    running_total = 0

    for sentence in summary_sentences:
        sentence_words = word_count(sentence)
        if kept_sentences and running_total + sentence_words > budget:
            break
        kept_sentences.append(sentence)
        running_total += sentence_words

    if not kept_sentences:
        kept_sentences.append(summary_sentences[0])

    return normalize_whitespace(" ".join(kept_sentences))


def summarize_extractive(text: str, length: str) -> str:
    cleaned = normalize_whitespace(text)
    sentences = split_sentences(cleaned)
    if len(sentences) <= 2:
        return cleaned

    words = [word for word in tokenize(cleaned) if word not in STOP_WORDS and len(word) > 2]
    if not words:
        return _compress_to_budget(" ".join(sentences[: _best_sentence_count(len(sentences), length)]), length)

    frequencies = Counter(words)
    max_frequency = max(frequencies.values())
    normalized = {word: count / max_frequency for word, count in frequencies.items()}

    scored = []
    for index, sentence in enumerate(sentences):
        sentence_words = tokenize(sentence)
        meaningful_words = [word for word in sentence_words if word in normalized]
        if not meaningful_words:
            continue

        score = sum(normalized[word] for word in meaningful_words)
        position_bonus = 1.2 if index == 0 else 1.0
        density_bonus = 1 + (len(set(meaningful_words)) / max(len(meaningful_words), 1))
        scored.append(
            {
                "index": index,
                "sentence": sentence,
                "score": score * position_bonus * density_bonus,
            }
        )

    if not scored:
        return _compress_to_budget(" ".join(sentences[: _best_sentence_count(len(sentences), length)]), length)

    summary_count = _best_sentence_count(len(sentences), length)
    selected = sorted(scored, key=lambda item: item["score"], reverse=True)[:summary_count]
    ordered = sorted(selected, key=lambda item: item["index"])
    return _compress_to_budget(" ".join(item["sentence"] for item in ordered), length)
