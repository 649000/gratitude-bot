from scheduler.common.models import GratitudeEntry
from scheduler.common.scoring import score_entries, select_highlights


def make_entry(
    content: str,
    starred: bool = False,
    entry_id: str = "00000000-0000-0000-0000-000000000001",
) -> GratitudeEntry:
    entry = GratitudeEntry(
        content=content,
        starred=starred,
    )
    from uuid import UUID

    entry.id = UUID(entry_id)
    return entry


class TestScoreEntries:
    def test_starred_entry_gets_boost(self):
        entries = [
            make_entry("short", starred=True),
            make_entry("also short"),
        ]
        scored = score_entries(entries)
        assert scored[0]["entry"].starred is True
        assert scored[0]["score"] > scored[1]["score"]

    def test_long_entry_gets_length_boost(self):
        long_text = (
            "this is a very long entry with many words to surpass fifty characters yes indeed"
        )
        short_text = "short"
        entries = [
            make_entry(short_text),
            make_entry(long_text),
        ]
        scored = score_entries(entries)
        long_entry = next(s for s in scored if s["entry"].content == long_text)
        short_entry = next(s for s in scored if s["entry"].content == short_text)
        assert long_entry["score"] > short_entry["score"]

    def test_scoring_returns_sorted_by_score_descending(self):
        entries = [
            make_entry("a", starred=True),
            make_entry("b"),
            make_entry("z" * 60, starred=True),
        ]
        scored = score_entries(entries)
        scores = [s["score"] for s in scored]
        assert scores == sorted(scores, reverse=True)


class TestSelectHighlights:
    def test_returns_all_when_fewer_than_top_n(self):
        entries = [
            make_entry("entry one"),
            make_entry("entry two"),
        ]
        result = select_highlights(entries, top_n=5)
        assert len(result) == 2

    def test_returns_top_n_when_more_entries(self):
        entries = [make_entry(f"entry {i}") for i in range(10)]
        result = select_highlights(entries, top_n=3)
        assert len(result) == 3

    def test_starred_entry_included(self):
        entries = [
            make_entry("normal entry", starred=False),
            make_entry("starred entry", starred=True),
        ] + [make_entry(f"filler {i}") for i in range(8)]
        result = select_highlights(entries, top_n=3)
        starred_in_result = any(e.starred for e in result)
        assert starred_in_result

    def test_entity_clustering_removes_duplicates(self):
        entries = [
            make_entry("I am grateful for Sarah helping me", starred=True),
            make_entry("Sarah was so kind to me today"),
            make_entry("Sarah really made my day special"),
            make_entry("I had a great walk in the park"),
            make_entry("The sunshine today was beautiful"),
            make_entry("Good coffee at the new cafe"),
        ]
        result = select_highlights(entries, top_n=4)
        sarah_count = sum(1 for e in result if "sarah" in e.content.lower())
        assert sarah_count == 1, f"Expected 1 Sarah entry, got {sarah_count}"

    def test_top_n_zero_returns_empty(self):
        entries = [make_entry("test")]
        result = select_highlights(entries, top_n=0)
        assert result == []

    def test_empty_entries_returns_empty(self):
        result = select_highlights([], top_n=5)
        assert result == []
