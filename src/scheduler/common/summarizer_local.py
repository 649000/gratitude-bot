import logging
from collections import Counter
from datetime import date

from scheduler.common.models import GratitudeEntry, User
from scheduler.common.summarizer import DigestSummarizer

logger = logging.getLogger(__name__)

_LOCAL_STOP_WORDS = {
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
    "gratitudejar",
    "im",
    "ive",
}

_TYPE_LABELS = {
    "weekly": "this week",
    "monthly": "this month",
    "yearly": "this year",
}

_EMOJI_STATS = {
    "starred": "\u2b50",
    "entries": "\U0001f4dd",
    "people": "\U0001f465",
    "streak": "\U0001f525",
}


class LocalSummarizer(DigestSummarizer):
    async def summarize(
        self,
        user: User,
        digest_type: str,
        period_start: date,
        period_end: date,
        highlights: list[GratitudeEntry],
    ) -> dict:
        entries_data = self._build_entry_list(highlights)
        intro = self._build_intro(user, digest_type, highlights, entries_data)
        body = self._build_body(digest_type, period_start, period_end, highlights)
        return {
            "intro": intro,
            "body": body,
            "entries": entries_data,
            "entry_count": len(highlights),
        }

    def _build_intro(
        self,
        user: User,
        digest_type: str,
        highlights: list[GratitudeEntry],
        _entries_data: list[dict],
    ) -> str:
        name = user.first_name or "there"
        period = _TYPE_LABELS.get(digest_type, "recently")

        stats_parts = [f"{len(highlights)} entries"]
        starred_count = sum(1 for e in highlights if e.starred)
        if starred_count:
            stats_parts.append(f"{starred_count} starred")

        people = self._extract_people(highlights)
        if people:
            stats_parts.append(f"about {len(people)} people")

        stats = ", ".join(stats_parts)

        theme_line = self._detect_themes(highlights)
        if theme_line:
            return f"{name}, {period} you had {stats}\u2014{theme_line} \U0001f4ab"
        return f"{name}, {period} you had {stats}. Here are your highlights \U0001f4ab"

    def _detect_themes(self, highlights: list[GratitudeEntry]) -> str:
        all_words: list[str] = []
        for entry in highlights:
            tokens = [
                w.lower()
                for w in __import__("re").findall(r"[a-zA-Z]+", entry.content)
                if w.lower() not in _LOCAL_STOP_WORDS and len(w) > 3
            ]
            all_words.extend(tokens)

        if not all_words:
            return ""

        top = Counter(all_words).most_common(3)
        themes = [word.capitalize() for word, count in top if count > 1]
        if not themes:
            return ""
        if len(themes) == 1:
            return f"revolving around {themes[0]}"
        if len(themes) == 2:
            return f"revolving around {themes[0]} and {themes[1]}"
        return f"revolving around {', '.join(themes[:-1])} and {themes[-1]}"

    def _extract_people(self, highlights: list[GratitudeEntry]) -> list[str]:
        found: list[str] = []
        for entry in highlights:
            words = __import__("re").findall(r"[A-Z][a-z]+", entry.content)
            for w in words:
                if w not in _LOCAL_STOP_WORDS and w not in found:
                    found.append(w)
        return found

    def _build_entry_list(self, highlights: list[GratitudeEntry]) -> list[dict]:
        return [
            {
                "id": str(e.id),
                "content": e.content,
                "date": e.created_at.strftime("%Y-%m-%d %H:%M"),
                "starred": e.starred,
            }
            for e in highlights
        ]

    def _build_body(
        self,
        digest_type: str,
        period_start: date,
        period_end: date,
        highlights: list[GratitudeEntry],
    ) -> str:
        labels = {
            "weekly": "\U0001f4c5 Your Weekly Digest",
            "monthly": "\U0001f4c5 Your Monthly Digest",
            "yearly": "\U0001f4c5 Your Yearly Digest",
        }
        header = labels.get(digest_type, "\U0001f4c5 Your Digest")
        lines = [f"{header} ({period_start} \u2014 {period_end})"]
        for i, entry in enumerate(highlights, 1):
            lines.append(f"\n{i}\u20e3 {entry.content}")
            date_str = entry.created_at.strftime("%Y-%m-%d %H:%M")
            if entry.starred:
                date_str += " \u2b50"
            lines.append(f"   \u2014 {date_str}")
        return "\n".join(lines)
