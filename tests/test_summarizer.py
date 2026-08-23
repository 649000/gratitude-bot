import uuid
from datetime import date, datetime

import pytest

from scheduler.common.models import GratitudeEntry, User
from scheduler.common.summarizer_local import LocalSummarizer


def _entry(
    content: str,
    starred: bool = False,
    created_at: datetime | None = None,
):
    return GratitudeEntry(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        content=content,
        starred=starred,
        source="telegram",
        created_at=created_at or datetime(2025, 7, 20, 10, 30),
    )


def _user(
    first_name: str | None = "Alice",
    timezone: str = "UTC+8",
):
    return User(
        id=uuid.uuid4(),
        telegram_id=123,
        first_name=first_name,
        timezone=timezone,
    )


@pytest.fixture
def summarizer():
    return LocalSummarizer()


class TestBuildIntro:
    def test_includes_user_name(self, summarizer):
        user = _user(first_name="Alice")
        highlights = [_entry("Grateful for coffee"), _entry("Sunny day")]
        entries_data: list[dict[str, object]] = [{}, {}]

        intro = summarizer._build_intro(user, "weekly", highlights, entries_data)

        assert "Alice" in intro

    def test_falls_back_to_there_when_no_name(self, summarizer):
        user = _user(first_name=None)
        highlights = [_entry("Content")]

        intro = summarizer._build_intro(user, "weekly", highlights, [])

        assert "there" in intro

    def test_includes_starred_count(self, summarizer):
        user = _user()
        highlights = [
            _entry("A", starred=True),
            _entry("B", starred=True),
            _entry("C", starred=False),
        ]

        intro = summarizer._build_intro(user, "weekly", highlights, [])

        assert "2 starred" in intro

    def test_includes_people_count(self, summarizer):
        user = _user()
        highlights = [
            _entry("I am grateful for Sarah and her help"),
            _entry("John is a great friend"),
        ]

        intro = summarizer._build_intro(user, "weekly", highlights, [])

        assert "about 2 people" in intro

    def test_omits_people_when_none_found(self, summarizer):
        user = _user()
        highlights = [_entry("just a regular day no names")]

        intro = summarizer._build_intro(user, "weekly", highlights, [])

        assert "people" not in intro


class TestDetectThemes:
    def test_single_theme(self, summarizer):
        highlights = [
            _entry("Work was productive today"),
            _entry("Work project went well"),
            _entry("Work colleagues are great"),
        ]

        result = summarizer._detect_themes(highlights)

        assert "Work" in result

    def test_two_themes(self, summarizer):
        highlights = [
            _entry("Family dinner was lovely"),
            _entry("Family time at the park"),
            _entry("Coffee with friends"),
            _entry("Friends game night"),
        ]

        result = summarizer._detect_themes(highlights)

        assert "Family" in result
        assert "Friends" in result
        assert "and" in result or "," not in result.split("and")[0]

    def test_returns_empty_when_no_repeated_words(self, summarizer):
        highlights = [
            _entry("Unique content here"),
            _entry("Different words now"),
        ]

        result = summarizer._detect_themes(highlights)

        assert result == ""

    def test_returns_empty_for_empty_highlights(self, summarizer):
        result = summarizer._detect_themes([])

        assert result == ""

    def test_excludes_stop_words_from_themes(self, summarizer):
        highlights = [
            _entry("This is not relevant"),
            _entry("That will never count"),
        ]

        result = summarizer._detect_themes(highlights)

        assert "This" not in result
        assert "That" not in result


class TestExtractPeople:
    def test_finds_capitalized_names(self, summarizer):
        highlights = [
            _entry("Grateful for Sarah's support"),
            _entry("John and Mary helped me"),
        ]

        result = summarizer._extract_people(highlights)

        assert "Sarah" in result
        assert "John" in result
        assert "Mary" in result

    def test_excludes_stop_words(self, summarizer):
        highlights = [_entry("The I Today Grateful thing")]

        result = summarizer._extract_people(highlights)

        assert "The" in result
        assert "Grateful" in result
        assert "I" not in result

    def test_no_duplicates(self, summarizer):
        highlights = [
            _entry("Sarah was great"),
            _entry("Sarah helped again"),
            _entry("Sarah is the best"),
        ]

        result = summarizer._extract_people(highlights)

        assert result.count("Sarah") == 1


class TestBuildBody:
    def test_weekly_header(self, summarizer):
        highlights = [_entry("Test")]
        period_start = date(2025, 7, 14)
        period_end = date(2025, 7, 20)

        body = summarizer._build_body("weekly", period_start, period_end, highlights)

        assert "Weekly Digest" in body

    def test_monthly_header(self, summarizer):
        highlights = [_entry("Test")]

        body = summarizer._build_body("monthly", date(2025, 7, 1), date(2025, 7, 31), highlights)

        assert "Monthly Digest" in body

    def test_yearly_header(self, summarizer):
        highlights = [_entry("Test")]

        body = summarizer._build_body("yearly", date(2025, 1, 1), date(2025, 12, 31), highlights)

        assert "Yearly Digest" in body

    def test_starred_entry_has_star_marker(self, summarizer):
        highlights = [_entry("Starred content", starred=True)]

        body = summarizer._build_body("weekly", date(2025, 7, 14), date(2025, 7, 20), highlights)

        assert "\u2b50" in body

    def test_multiple_entries_numbered(self, summarizer):
        highlights = [_entry("A"), _entry("B"), _entry("C")]

        body = summarizer._build_body("weekly", date(2025, 7, 14), date(2025, 7, 20), highlights)

        assert "1." in body
        assert "2." in body
        assert "3." in body


class TestBuildEntryList:
    def test_returns_correct_keys(self, summarizer):
        highlights = [_entry("Content", starred=True)]

        result = summarizer._build_entry_list(highlights)

        assert len(result) == 1
        assert set(result[0].keys()) == {"id", "content", "date", "starred"}
        assert result[0]["content"] == "Content"
        assert result[0]["starred"] is True
        assert isinstance(result[0]["id"], str)


class TestSummarizeFull:
    @pytest.mark.asyncio
    async def test_returns_all_expected_keys(self, summarizer):
        highlights = [_entry("Test entry")]
        user = _user()

        result = await summarizer.summarize(
            user=user,
            digest_type="weekly",
            period_start=date(2025, 7, 14),
            period_end=date(2025, 7, 20),
            highlights=highlights,
        )

        assert set(result.keys()) == {"intro", "body", "entries", "entry_count"}
        assert result["entry_count"] == 1
        assert len(result["entries"]) == 1
        assert isinstance(result["intro"], str)
        assert isinstance(result["body"], str)
