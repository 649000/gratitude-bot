import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.gratitude import GratitudeEntry
from app.models.preference import UserPreference
from app.models.prompt import Prompt
from app.models.user import User
from app.telegram.handlers import db
from app.telegram.messages import FALLBACK_PROMPT


def _make_result(
    *,
    scalar_one_or_none=None,
    scalar=None,
    scalars_all=None,
):
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_one_or_none
    result.scalar.return_value = scalar
    all_mock = MagicMock()
    all_mock.all.return_value = scalars_all or []
    result.scalars.return_value = all_mock
    return result


def _new_user(
    telegram_id=123,
    username="testuser",
    first_name="Test",
    last_name=None,
    timezone="UTC+8",
):
    return User(
        id=uuid.uuid4(),
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        timezone=timezone,
    )


def _new_pref(user_id=None):
    return UserPreference(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
    )


def _new_prompt(text="What are you grateful for today?"):
    return Prompt(
        id=uuid.uuid4(),
        text=text,
        category="general",
    )


def _new_entry(
    user_id=None,
    content="Test entry",
    starred=False,
    source="telegram",
    created_at=None,
):
    return GratitudeEntry(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        content=content,
        starred=starred,
        source=source,
        created_at=created_at or datetime(2025, 1, 15, 10, 30),
    )


class TestGetOrCreateUser:
    @pytest.mark.asyncio
    async def test_creates_new_user_when_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.get_or_create_user(
            session, telegram_id=123, username="u", first_name="F"
        )

        assert result.telegram_id == 123
        assert result.username == "u"
        assert result.first_name == "F"
        session.add.assert_called_once()
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_existing_user_when_found(self):
        session = AsyncMock()
        existing = _new_user()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=existing))

        result = await db.get_or_create_user(session, telegram_id=123)

        assert result is existing
        session.add.assert_not_called()


class TestGetOrCreatePreferences:
    @pytest.mark.asyncio
    async def test_creates_new_preferences_when_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))
        user_id = uuid.uuid4()

        result = await db.get_or_create_preferences(session, user_id)

        assert result.user_id == user_id
        session.add.assert_called_once()
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_existing_preferences_when_found(self):
        session = AsyncMock()
        pref = _new_pref()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=pref))

        result = await db.get_or_create_preferences(session, pref.user_id)

        assert result is pref
        session.add.assert_not_called()


class TestCreateEntry:
    @pytest.mark.asyncio
    async def test_creates_entry_with_defaults(self):
        session = AsyncMock()
        user_id = uuid.uuid4()

        result = await db.create_entry(session, user_id, "Grateful for sunshine")

        assert result.user_id == user_id
        assert result.content == "Grateful for sunshine"
        assert result.source == "telegram"
        session.add.assert_called_once()
        session.flush.assert_called_once()


class TestDeleteEntry:
    @pytest.mark.asyncio
    async def test_deletes_existing_entry(self):
        session = AsyncMock()
        entry = _new_entry()
        session.get = AsyncMock(return_value=entry)

        result = await db.delete_entry(session, entry.id)

        assert result is True
        session.delete.assert_called_once_with(entry)
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_entry_not_found(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        result = await db.delete_entry(session, uuid.uuid4())

        assert result is False
        session.delete.assert_not_called()


class TestStarEntry:
    @pytest.mark.asyncio
    async def test_sets_star_to_true(self):
        session = AsyncMock()
        entry = _new_entry(starred=False)
        session.get = AsyncMock(return_value=entry)

        result = await db.star_entry(session, entry.id, starred=True)

        assert result is True
        assert entry.starred is True

    @pytest.mark.asyncio
    async def test_sets_star_to_false(self):
        session = AsyncMock()
        entry = _new_entry(starred=True)
        session.get = AsyncMock(return_value=entry)

        result = await db.star_entry(session, entry.id, starred=False)

        assert result is True
        assert entry.starred is False

    @pytest.mark.asyncio
    async def test_returns_false_when_entry_not_found(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        result = await db.star_entry(session, uuid.uuid4(), starred=True)

        assert result is False


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_updates_provided_fields(self):
        session = AsyncMock()
        user = _new_user(first_name="Old", timezone="UTC")
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=user))

        result = await db.update_user(
            session,
            telegram_id=123,
            first_name="New",
            timezone="UTC+8",
        )

        assert result is user
        assert user.first_name == "New"
        assert user.timezone == "UTC+8"

    @pytest.mark.asyncio
    async def test_skips_none_values(self):
        session = AsyncMock()
        user = _new_user(first_name="Old", last_name="Last")
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=user))

        await db.update_user(
            session,
            telegram_id=123,
            first_name=None,
            last_name="Updated",
        )

        assert user.first_name == "Old"
        assert user.last_name == "Updated"

    @pytest.mark.asyncio
    async def test_returns_none_when_user_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.update_user(session, telegram_id=999, first_name="X")

        assert result is None


class TestUpdatePreference:
    @pytest.mark.asyncio
    async def test_updates_enabled_fields(self):
        session = AsyncMock()
        pref = _new_pref()
        pref.reminder_enabled = False
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=pref))

        result = await db.update_preference(
            session, pref.user_id, reminder_enabled=True, digest_weekly_enabled=False
        )

        assert result is pref
        assert pref.reminder_enabled is True
        assert pref.digest_weekly_enabled is False

    @pytest.mark.asyncio
    async def test_returns_none_when_preference_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.update_preference(session, uuid.uuid4(), reminder_enabled=True)

        assert result is None


class TestCompleteOnboarding:
    @pytest.mark.asyncio
    async def test_sets_onboarding_completed(self):
        session = AsyncMock()
        pref = _new_pref()
        pref.onboarding_completed = False
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=pref))

        result = await db.complete_onboarding(session, pref.user_id)

        assert result is pref
        assert pref.onboarding_completed is True

    @pytest.mark.asyncio
    async def test_returns_none_when_preference_not_found(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.complete_onboarding(session, uuid.uuid4())

        assert result is None


class TestGetRandomPrompt:
    @pytest.mark.asyncio
    async def test_returns_prompt_text_when_found(self):
        session = AsyncMock()
        prompt = _new_prompt("What made you smile today?")
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=prompt))

        result = await db.get_random_prompt(session)

        assert result == "What made you smile today?"

    @pytest.mark.asyncio
    async def test_returns_fallback_when_no_prompts(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.get_random_prompt(session)

        assert result == FALLBACK_PROMPT


class TestHasEntryToday:
    @pytest.mark.asyncio
    async def test_returns_true_when_entry_exists_today(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=5))
        user_id = uuid.uuid4()
        today = datetime(2025, 7, 22, 10, 0, 0)

        result = await db.has_entry_today(session, user_id, today=today)

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_entry_today(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=0))
        user_id = uuid.uuid4()
        today = datetime(2025, 7, 22, 10, 0, 0)

        result = await db.has_entry_today(session, user_id, today=today)

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_when_scalar_is_none(self):
        user_id = uuid.uuid4()
        today = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=1), spec_set=False)

        result = await db.has_entry_today(session, user_id, today=today)

        assert result is True


class TestGetEntries:
    @pytest.mark.asyncio
    async def test_returns_entries_list(self):
        session = AsyncMock()
        entries = [_new_entry(), _new_entry()]
        session.execute = AsyncMock(return_value=_make_result(scalars_all=entries))

        result = await db.get_entries(session, entries[0].user_id)

        assert result == entries

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_entries(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalars_all=[]))

        result = await db.get_entries(session, uuid.uuid4())

        assert result == []


class TestCountEntriesFiltered:
    @pytest.mark.asyncio
    async def test_returns_count(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=42))

        result = await db.count_entries_filtered(session, uuid.uuid4())

        assert result == 42

    @pytest.mark.asyncio
    async def test_returns_zero_when_scalar_is_none(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=None))

        result = await db.count_entries_filtered(session, uuid.uuid4())

        assert result == 0


class TestGetEntryCount:
    @pytest.mark.asyncio
    async def test_returns_count(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=10))

        result = await db.get_entry_count(session, uuid.uuid4())

        assert result == 10

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=None))

        result = await db.get_entry_count(session, uuid.uuid4())

        assert result == 0


class TestGetEntryCountRange:
    @pytest.mark.asyncio
    async def test_returns_count_since(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=7))

        result = await db.get_entry_count_range(
            session, uuid.uuid4(), since=datetime(2025, 7, 1)
        )

        assert result == 7

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=None))

        result = await db.get_entry_count_range(
            session, uuid.uuid4(), since=datetime(2025, 1, 1)
        )

        assert result == 0


class TestGetStarredCount:
    @pytest.mark.asyncio
    async def test_returns_starred_count(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=3))

        result = await db.get_starred_count(session, uuid.uuid4())

        assert result == 3

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=None))

        result = await db.get_starred_count(session, uuid.uuid4())

        assert result == 0


class TestGetStarredEntries:
    @pytest.mark.asyncio
    async def test_returns_starred_entries(self):
        session = AsyncMock()
        entries = [_new_entry(starred=True), _new_entry(starred=True)]
        session.execute = AsyncMock(return_value=_make_result(scalars_all=entries))

        result = await db.get_starred_entries(session, entries[0].user_id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_starred(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalars_all=[]))

        result = await db.get_starred_entries(session, uuid.uuid4())

        assert result == []


class TestGetDistinct:
    @pytest.mark.asyncio
    async def test_get_distinct_years(self):
        session = AsyncMock()
        rows = [(2025,), (2024,), (2023,)]
        mock_result = MagicMock()
        mock_result.all.return_value = rows
        session.execute = AsyncMock(return_value=mock_result)

        result = await db.get_distinct_years(session, uuid.uuid4())

        assert result == [2025, 2024, 2023]

    @pytest.mark.asyncio
    async def test_get_distinct_years_skips_none(self):
        session = AsyncMock()
        rows = [(2025,), (None,), (2023,)]
        mock_result = MagicMock()
        mock_result.all.return_value = rows
        session.execute = AsyncMock(return_value=mock_result)

        result = await db.get_distinct_years(session, uuid.uuid4())

        assert result == [2025, 2023]

    @pytest.mark.asyncio
    async def test_get_distinct_months(self):
        session = AsyncMock()
        rows = [(12,), (11,), (10,)]
        mock_result = MagicMock()
        mock_result.all.return_value = rows
        session.execute = AsyncMock(return_value=mock_result)

        result = await db.get_distinct_months(session, uuid.uuid4(), year=2025)

        assert result == [12, 11, 10]


class TestGetStreak:
    @pytest.mark.asyncio
    async def test_three_day_streak(self):
        user_id = uuid.uuid4()
        now = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[
            _make_result(scalar=1),
            _make_result(scalar=1),
            _make_result(scalar=1),
            _make_result(scalar=0),
        ])

        result = await db.get_streak(session, user_id, now=now)

        assert result == 3

    @pytest.mark.asyncio
    async def test_zero_streak_when_no_entries_at_all(self):
        user_id = uuid.uuid4()
        now = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[
            _make_result(scalar=0),
            _make_result(scalar=0),
        ])

        result = await db.get_streak(session, user_id, now=now)

        assert result == 0

    @pytest.mark.asyncio
    async def test_yesterday_only_streak(self):
        user_id = uuid.uuid4()
        now = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[
            _make_result(scalar=0),
            _make_result(scalar=1),
            _make_result(scalar=0),
        ])

        result = await db.get_streak(session, user_id, now=now)

        assert result == 1

    @pytest.mark.asyncio
    async def test_streak_with_yesterday_continuation(self):
        user_id = uuid.uuid4()
        now = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[
            _make_result(scalar=0),
            _make_result(scalar=1),
            _make_result(scalar=1),
            _make_result(scalar=1),
            _make_result(scalar=0),
        ])

        result = await db.get_streak(session, user_id, now=now)

        assert result == 3

    @pytest.mark.asyncio
    async def test_streak_ignores_none_scalar(self):
        user_id = uuid.uuid4()
        now = datetime(2025, 7, 22, 10, 0, 0)
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[
            _make_result(scalar=None),
            _make_result(scalar=0),
        ])

        result = await db.get_streak(session, user_id, now=now)

        assert result == 0


class TestExportEntries:
    @pytest.mark.asyncio
    async def test_returns_entries_ascending(self):
        session = AsyncMock()
        entries = [_new_entry(), _new_entry()]
        session.execute = AsyncMock(return_value=_make_result(scalars_all=entries))

        result = await db.export_entries(session, entries[0].user_id)

        assert result == entries


class TestGetRandomEntry:
    @pytest.mark.asyncio
    async def test_returns_entry_when_found(self):
        session = AsyncMock()
        entry = _new_entry()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=entry))

        result = await db.get_random_entry(session, entry.user_id)

        assert result is entry

    @pytest.mark.asyncio
    async def test_returns_none_when_no_entries(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar_one_or_none=None))

        result = await db.get_random_entry(session, uuid.uuid4())

        assert result is None


class TestGetEntryById:
    @pytest.mark.asyncio
    async def test_returns_entry_when_found(self):
        session = AsyncMock()
        entry = _new_entry()
        session.get = AsyncMock(return_value=entry)

        result = await db.get_entry_by_id(session, entry.id)

        assert result is entry

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)

        result = await db.get_entry_by_id(session, uuid.uuid4())

        assert result is None


class TestGetFirstEntryDate:
    @pytest.mark.asyncio
    async def test_returns_date(self):
        session = AsyncMock()
        min_date = datetime(2025, 1, 1)
        session.execute = AsyncMock(return_value=_make_result(scalar=min_date))

        result = await db.get_first_entry_date(session, uuid.uuid4())

        assert result == min_date

    @pytest.mark.asyncio
    async def test_returns_none_when_no_entries(self):
        session = AsyncMock()
        session.execute = AsyncMock(return_value=_make_result(scalar=None))

        result = await db.get_first_entry_date(session, uuid.uuid4())

        assert result is None
