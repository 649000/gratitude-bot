import json
import uuid
from datetime import UTC, date, datetime
from unittest.mock import patch

import pytest

from scheduler.common.models import GratitudeEntry, ScheduledMessage
from scheduler.dispatcher.dispatch import (
    _in_daytime_window,
    _in_evening_window,
    _parse_utc_offset,
    _user_local_date,
    _user_local_hour,
    build_sqs_payload_for_digest,
    build_sqs_payload_from_entry,
)


def _entry(content="Test entry", starred=False, created_at=None):
    return GratitudeEntry(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        content=content,
        starred=starred,
        source="telegram",
        created_at=created_at or datetime(2025, 7, 20, 10, 30),
    )


def _scheduled_message(
    message_type="weekly",
    entry_ids=None,
    message_text="Hello world",
):
    return ScheduledMessage(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        message_type=message_type,
        message_text=message_text,
        entry_ids=entry_ids or [],
        period_start=date(2025, 7, 14),
        period_end=date(2025, 7, 20),
        entry_count=len(entry_ids) if entry_ids else 0,
        status="pending",
    )


class TestParseUtcOffset:
    def test_positive_integer(self):
        assert _parse_utc_offset("UTC+8") == 480

    def test_negative_integer(self):
        assert _parse_utc_offset("UTC-5") == -300

    def test_zero(self):
        assert _parse_utc_offset("UTC") == 0

    def test_positive_with_minutes(self):
        assert _parse_utc_offset("UTC+5:30") == 330

    def test_negative_with_minutes(self):
        assert _parse_utc_offset("UTC-3:30") == -210

    def test_positive_single_digit(self):
        assert _parse_utc_offset("UTC+1") == 60


class TestUserLocalHour:
    @pytest.mark.parametrize(
        "utc_hour, tz, expected_local_hour",
        [
            (10, "UTC+8", 18),
            (10, "UTC+0", 10),
            (10, "UTC-5", 5),
            (0, "UTC+8", 8),
            (20, "UTC+5:30", 2),
        ],
    )
    def test_converts_utc_to_local_hour(self, utc_hour, tz, expected_local_hour):
        fake_utc_now = datetime(2025, 7, 22, utc_hour, 30, 0, tzinfo=UTC)
        with patch("scheduler.dispatcher.dispatch.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc_now
            mock_dt.UTC = UTC

            result = _user_local_hour(tz)

        assert result == expected_local_hour


class TestUserLocalDate:
    def test_converts_utc_to_local_date(self):
        fake_utc_now = datetime(2025, 7, 22, 20, 0, 0, tzinfo=UTC)
        with patch("scheduler.dispatcher.dispatch.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc_now
            mock_dt.UTC = UTC

            result = _user_local_date("UTC+8")

        assert result.date() == date(2025, 7, 23)

    def test_same_day_for_positive_offset(self):
        fake_utc_now = datetime(2025, 7, 22, 10, 0, 0, tzinfo=UTC)
        with patch("scheduler.dispatcher.dispatch.datetime") as mock_dt:
            mock_dt.now.return_value = fake_utc_now
            mock_dt.UTC = UTC

            result = _user_local_date("UTC+8")

        assert result.date() == date(2025, 7, 22)


class TestInEveningWindow:
    def test_inside_window_7pm(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=19):
            assert _in_evening_window("UTC+8") is True

    def test_inside_window_8pm(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=20):
            assert _in_evening_window("UTC+8") is True

    def test_outside_window_before_7pm(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=18):
            assert _in_evening_window("UTC+8") is False

    def test_outside_window_9pm(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=21):
            assert _in_evening_window("UTC+8") is False


class TestInDaytimeWindow:
    def test_inside_window_noon(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=12):
            assert _in_daytime_window("UTC+8") is True

    def test_inside_window_9am(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=9):
            assert _in_daytime_window("UTC+8") is True

    def test_outside_window_8am(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=8):
            assert _in_daytime_window("UTC+8") is False

    def test_outside_window_9pm(self):
        with patch("scheduler.dispatcher.dispatch._user_local_hour", return_value=21):
            assert _in_daytime_window("UTC+8") is False


class TestBuildSqsPayloadFromEntry:
    def test_includes_content_in_payload(self):
        entry = _entry("Grateful for sunshine")

        payload = build_sqs_payload_from_entry(entry, chat_id=12345)

        data = json.loads(payload)
        assert "Grateful for sunshine" in data["text"]

    def test_includes_chat_id(self):
        entry = _entry("Test")

        payload = build_sqs_payload_from_entry(entry, chat_id=99999)

        data = json.loads(payload)
        assert data["chat_id"] == 99999

    def test_starred_entry_shows_unstar_label(self):
        entry = _entry("Test", starred=True)

        payload = build_sqs_payload_from_entry(entry, chat_id=12345)

        data = json.loads(payload)
        buttons = data["reply_markup"]["inline_keyboard"][0]
        star_button = buttons[0]
        assert "Unstar" in star_button["text"]

    def test_unstarred_entry_shows_star_label(self):
        entry = _entry("Test", starred=False)

        payload = build_sqs_payload_from_entry(entry, chat_id=12345)

        data = json.loads(payload)
        buttons = data["reply_markup"]["inline_keyboard"][0]
        star_button = buttons[0]
        assert star_button["text"].startswith("\u2b50")

    def test_includes_prefix(self):
        entry = _entry("Test")

        payload = build_sqs_payload_from_entry(
            entry, chat_id=12345, prefix="Custom prefix:\n\n"
        )

        data = json.loads(payload)
        assert data["text"].startswith("Custom prefix:")

    def test_includes_delete_button(self):
        entry = _entry("Test")

        payload = build_sqs_payload_from_entry(entry, chat_id=12345)

        data = json.loads(payload)
        buttons = data["reply_markup"]["inline_keyboard"][0]
        assert len(buttons) == 2
        assert any("Delete" in b["text"] for b in buttons)

    def test_uses_markdown_parse_mode(self):
        entry = _entry("Test")

        payload = build_sqs_payload_from_entry(entry, chat_id=12345)

        data = json.loads(payload)
        assert data["parse_mode"] == "Markdown"


class TestBuildSqsPayloadForDigest:
    def test_includes_message_text(self):
        msg = _scheduled_message(message_text="Your weekly digest")

        payload = build_sqs_payload_for_digest(msg, chat_id=12345)

        data = json.loads(payload)
        assert data["text"] == "Your weekly digest"

    def test_creates_keyboard_from_entry_ids(self):
        msg = _scheduled_message(
            entry_ids=["aaa-bbb", "ccc-ddd"],
        )

        payload = build_sqs_payload_for_digest(msg, chat_id=12345)

        data = json.loads(payload)
        keyboard = data["reply_markup"]["inline_keyboard"]
        assert len(keyboard) == 2
        assert keyboard[0][0]["callback_data"] == "star:aaa-bbb"
        assert keyboard[1][0]["callback_data"] == "star:ccc-ddd"

    def test_empty_entry_ids_returns_empty_keyboard(self):
        msg = _scheduled_message(entry_ids=[])

        payload = build_sqs_payload_for_digest(msg, chat_id=12345)

        data = json.loads(payload)
        assert data["reply_markup"]["inline_keyboard"] == []
