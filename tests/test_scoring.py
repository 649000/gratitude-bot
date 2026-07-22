import uuid

from scheduler.common.models import GratitudeEntry
from scheduler.common.scoring import score_entries, select_highlights

_counter = 0


def _next_id() -> str:
    global _counter
    _counter += 1
    return f"00000000-0000-0000-0000-{_counter:012d}"


def make_entry(
    content: str,
    starred: bool = False,
    entry_id: str | None = None,
) -> GratitudeEntry:
    if entry_id is None:
        entry_id = _next_id()
    entry = GratitudeEntry(
        content=content,
        starred=starred,
    )
    entry.id = uuid.UUID(entry_id)
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

    def test_single_entry_gets_non_negative_score(self):
        entries = [make_entry("gratitude test entry")]
        scored = score_entries(entries)
        assert len(scored) == 1
        assert scored[0]["score"] >= 0

    def test_only_stop_words_gets_low_score(self):
        entries = [make_entry("the a an in on at")]
        scored = score_entries(entries)
        assert len(scored) == 1
        assert scored[0]["score"] >= 0

    def test_empty_content_handled(self):
        entries = [make_entry("")]
        scored = score_entries(entries)
        assert len(scored) == 1

    def test_unicode_content_handled(self):
        entries = [
            make_entry("I am grateful for caf\u00e9"),
            make_entry("Beautiful d\u00eda"),
        ]
        scored = score_entries(entries)
        assert len(scored) == 2
        for s in scored:
            assert s["score"] >= 0

    def test_empty_list_returns_empty(self):
        scored = score_entries([])
        assert scored == []

    def test_two_entries_same_content_scores(self):
        entries = [
            make_entry("identical content here"),
            make_entry("identical content here"),
        ]
        scored = score_entries(entries)
        assert len(scored) == 2
        assert scored[0]["score"] == scored[1]["score"]


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

    def test_top_n_equals_len_returns_all(self):
        entries = [make_entry(f"entry {i}") for i in range(3)]
        result = select_highlights(entries, top_n=3)
        assert len(result) == 3

    def test_fallback_fills_when_entries_share_bigrams(self):
        entries = [
            make_entry("interview preparation went well today"),
            make_entry("the interview was challenging but rewarding"),
            make_entry("preparing for the interview took time"),
            make_entry("I had a relaxing walk in the park"),
            make_entry("beautiful sunset at the beach today"),
        ]
        result = select_highlights(entries, top_n=3)
        assert len(result) == 3

    def test_single_entry_returns_single(self):
        entries = [make_entry("only one")]
        result = select_highlights(entries, top_n=5)
        assert len(result) == 1
        assert result[0].content == "only one"

    def test_all_entries_unique_returns_top_n(self):
        entries = [
            make_entry("apple pie baking"),
            make_entry("bicycle ride morning"),
            make_entry("coffee shop reading"),
            make_entry("dog park running"),
            make_entry("early sunrise hiking"),
        ]
        result = select_highlights(entries, top_n=3)
        assert len(result) == 3
