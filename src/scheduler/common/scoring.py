import re
from typing import TypedDict

from scheduler.common.models import GratitudeEntry


class ScoredEntry(TypedDict):
    entry: GratitudeEntry
    score: float


_STOP_WORDS: set[str] = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "can",
    "shall",
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "she",
    "it",
    "they",
    "them",
    "this",
    "that",
    "these",
    "those",
    "am",
    "its",
    "very",
    "really",
    "just",
    "so",
    "not",
    "no",
    "yes",
    "today",
    "day",
    "grateful",
    "thankful",
    "thanks",
    "thank",
    "gratitude",
    "feel",
    "feeling",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOP_WORDS}


def score_entries(entries: list[GratitudeEntry]) -> list[ScoredEntry]:
    all_tokens: dict[str, set[str]] = {}
    for entry in entries:
        all_tokens[str(entry.id)] = _tokenize(entry.content)

    all_words: set[str] = set()
    for tokens in all_tokens.values():
        all_words.update(tokens)

    scored: list[ScoredEntry] = []
    for entry in entries:
        score = 0.0
        if entry.starred:
            score += 3.0
        if len(entry.content) > 50:
            score += 1.0

        entry_tokens = all_tokens.get(str(entry.id), set())
        others_tokens = all_words - entry_tokens
        unique_words = entry_tokens - others_tokens
        ratio = len(unique_words) / max(len(entry_tokens), 1)
        score += ratio * 0.5

        scored.append({"entry": entry, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _significant_bigrams(entry: GratitudeEntry) -> set[str]:
    tokens = re.findall(r"[a-z]+", entry.content.lower())
    significant = [t for t in tokens if t not in _STOP_WORDS]
    bigrams: set[str] = set()
    for i in range(len(significant) - 1):
        bigrams.add(f"{significant[i]}:{significant[i + 1]}")
    return bigrams | {t for t in significant if len(t) > 3}


def select_highlights(
    entries: list[GratitudeEntry],
    top_n: int,
) -> list[GratitudeEntry]:
    if top_n <= 0 or not entries:
        return []
    if len(entries) <= top_n:
        return entries

    scored = score_entries(entries)

    selected: list[GratitudeEntry] = []
    used_bigrams: set[str] = set()

    for item in scored:
        entry = item["entry"]
        bigrams = _significant_bigrams(entry)

        if not bigrams & used_bigrams:
            selected.append(entry)
            used_bigrams.update(bigrams)
            if len(selected) >= top_n:
                break

    if len(selected) < top_n:
        for item in scored:
            entry = item["entry"]
            if entry not in selected:
                selected.append(entry)
                if len(selected) >= top_n:
                    break

    return selected
