import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.telegram.messages import EMOJI_GIFT, EMOJI_JAR
from scheduler.common.database import async_session_factory
from scheduler.common.models import GratitudeEntry, ScheduledMessage, User, UserPreference

logger = logging.getLogger(__name__)

_REMINDER_WINDOW_START = 19
_REMINDER_WINDOW_END = 21
_REDISCOVERY_WINDOW_START = 9
_REDISCOVERY_WINDOW_END = 21
_REDISCOVERY_COOLDOWN_HOURS = 4

_sqs_client_factory: Callable[[], Any] | None = None


def _get_sqs_client() -> Any:
    if _sqs_client_factory is not None:
        return _sqs_client_factory()
    import boto3

    return boto3.client("sqs")


def _parse_utc_offset(tz_str: str) -> int:
    if tz_str == "UTC":
        return 0
    offset = tz_str[3:]
    if ":" in offset:
        hours_str, minutes_str = offset.split(":")
        hours = int(hours_str)
        minutes = int(minutes_str)
        return hours * 60 + (minutes if hours >= 0 else -minutes)
    return int(offset) * 60


def _user_local_hour(user_tz: str) -> int:
    now_utc = datetime.now(UTC)
    offset_minutes = _parse_utc_offset(user_tz)
    user_offset = timedelta(minutes=offset_minutes)
    user_now = now_utc + user_offset
    return user_now.hour


def _user_local_date(user_tz: str) -> datetime:
    now_utc = datetime.now(UTC)
    offset_minutes = _parse_utc_offset(user_tz)
    user_offset = timedelta(minutes=offset_minutes)
    user_now = now_utc + user_offset
    return user_now.replace(hour=0, minute=0, second=0, microsecond=0)


def _in_evening_window(user_tz: str) -> bool:
    hour = _user_local_hour(user_tz)
    return _REMINDER_WINDOW_START <= hour < _REMINDER_WINDOW_END


def _in_daytime_window(user_tz: str) -> bool:
    hour = _user_local_hour(user_tz)
    return _REDISCOVERY_WINDOW_START <= hour < _REDISCOVERY_WINDOW_END


async def _get_pending_digests() -> list[ScheduledMessage]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScheduledMessage)
            .join(User, User.id == ScheduledMessage.user_id)
            .join(UserPreference, UserPreference.user_id == User.id)
            .where(
                ScheduledMessage.status == "pending",
                UserPreference.onboarding_completed == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())


async def _get_users_for_reminders() -> list[User]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .join(UserPreference, UserPreference.user_id == User.id)
            .where(
                UserPreference.onboarding_completed == True,  # noqa: E712
                UserPreference.reminder_enabled == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())


async def _has_entry_today(session: AsyncSession, user_id: UUID, user_tz: str) -> bool:
    local_start = _user_local_date(user_tz)
    local_end = local_start + timedelta(days=1)
    result = await session.execute(
        select(func.count()).where(
            GratitudeEntry.user_id == user_id,
            GratitudeEntry.created_at >= local_start,
            GratitudeEntry.created_at < local_end,
        )
    )
    return result.scalar() > 0


async def _get_random_entry(session, user_id: UUID) -> GratitudeEntry | None:
    result = await session.execute(
        select(GratitudeEntry)
        .where(GratitudeEntry.user_id == user_id)
        .order_by(func.random())
        .limit(1)
    )
    return result.scalar_one_or_none()


def build_sqs_payload_from_entry(
    entry: GratitudeEntry,
    chat_id: int,
    prefix: str = "",
) -> str:
    from app.telegram.messages import EMOJI_DELETE, EMOJI_STAR, format_entry_date

    date_str = format_entry_date(entry.created_at)
    star_label = f"{EMOJI_STAR} Unstar" if entry.starred else f"{EMOJI_STAR} Star"
    entry_lines = [
        f'{prefix}"{entry.content}"',
        f"_{date_str}_",
    ]
    text = "\n\n".join(entry_lines)

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": star_label, "callback_data": f"star:{entry.id}"},
                {"text": f"{EMOJI_DELETE} Delete", "callback_data": f"del:{entry.id}"},
            ]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup,
    }
    return json.dumps(payload)


def build_sqs_payload_for_digest(
    msg: ScheduledMessage,
    chat_id: int,
) -> str:
    from app.telegram.messages import EMOJI_STAR

    keyboard = []
    for entry_id in msg.entry_ids:
        keyboard.append(
            [
                {"text": f"{EMOJI_STAR} Star", "callback_data": f"star:{entry_id}"},
            ]
        )

    payload = {
        "chat_id": chat_id,
        "text": msg.message_text,
        "reply_markup": {"inline_keyboard": keyboard},
    }
    return json.dumps(payload)


def _send_to_sqs(sqs_client, queue_url: str, payload: str, msg_id: str) -> bool:
    try:
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=payload,
            MessageGroupId=msg_id,
            MessageDeduplicationId=msg_id,
        )
        return True
    except Exception as e:
        if "NonExistentQueue" in str(e) or "AWS.SimpleQueueService.NonExistentQueue" in str(e):
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=payload,
            )
            return True
        raise


async def dispatch_digests(queue_url: str) -> dict:
    msgs = await _get_pending_digests()
    if not msgs:
        return {"sent": 0}

    sqs = _get_sqs_client()
    sent = 0
    failed = 0

    for msg in msgs:
        user = msg.user
        if not _in_evening_window(user.timezone):
            continue

        try:
            payload = build_sqs_payload_for_digest(msg, user.telegram_id)
            _send_to_sqs(sqs, queue_url, payload, str(msg.id))
            sent += 1

            async with async_session_factory() as session:
                db_msg = await session.get(ScheduledMessage, msg.id)
                if db_msg:
                    db_msg.status = "sent"
                    db_msg.sent_at = datetime.now(UTC)
                    await session.commit()
        except Exception:
            logger.exception("Failed to dispatch digest %s for user %s", msg.id, user.id)
            async with async_session_factory() as session:
                db_msg = await session.get(ScheduledMessage, msg.id)
                if db_msg:
                    db_msg.status = "failed"
                    await session.commit()
            failed += 1

    return {"sent": sent, "failed": failed, "total": len(msgs)}


async def dispatch_reminders(queue_url: str) -> dict:
    users = await _get_users_for_reminders()
    if not users:
        return {"sent": 0}

    sqs = _get_sqs_client()
    sent = 0

    for user in users:
        if not _in_evening_window(user.timezone):
            continue

        async with async_session_factory() as session:
            if await _has_entry_today(session, user.id, user.timezone):
                continue

            prompt = await _get_random_prompt(session)

        payload = {
            "chat_id": user.telegram_id,
            "text": f"How was your day? {EMOJI_JAR}\n\n_{prompt}_",
            "parse_mode": "Markdown",
        }
        try:
            msg_id = f"reminder:{user.id}:{datetime.now(UTC).date()}"
            _send_to_sqs(sqs, queue_url, json.dumps(payload), msg_id)
            sent += 1
        except Exception:
            logger.exception("Failed to dispatch reminder for user %s", user.id)

    return {"sent": sent, "total": len(users)}


async def dispatch_rediscovery(queue_url: str) -> dict:
    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .join(UserPreference, UserPreference.user_id == User.id)
            .where(
                UserPreference.onboarding_completed == True,  # noqa: E712
                UserPreference.rediscovery_enabled == True,  # noqa: E712
            )
        )
        users = list(result.scalars().all())

    if not users:
        return {"sent": 0}

    sqs = _get_sqs_client()
    sent = 0
    now = datetime.now(UTC)
    cooldown = timedelta(hours=_REDISCOVERY_COOLDOWN_HOURS)

    for user in users:
        if not _in_daytime_window(user.timezone):
            continue

        async with async_session_factory() as session:
            pref_result = await session.execute(
                select(UserPreference).where(UserPreference.user_id == user.id)
            )
            pref = pref_result.scalar_one_or_none()
            if not pref:
                continue

            if pref.last_rediscovery_at and (now - pref.last_rediscovery_at) < cooldown:
                continue

            entry = await _get_random_entry(session, user.id)
            if not entry:
                continue

            pref.last_rediscovery_at = now

            payload = build_sqs_payload_from_entry(
                entry,
                user.telegram_id,
                prefix=f"{EMOJI_GIFT} Here's a surprise from your jar:\n\n",
            )
            await session.commit()

        try:
            _send_to_sqs(sqs, queue_url, payload, f"rediscovery:{user.id}:{now.timestamp()}")
            sent += 1
        except Exception:
            logger.exception("Failed to dispatch rediscovery for user %s", user.id)

    return {"sent": sent, "total": len(users)}


async def _get_random_prompt(session) -> str:
    from scheduler.common.models import Prompt

    result = await session.execute(select(Prompt).order_by(func.random()).limit(1))
    prompt = result.scalar_one_or_none()
    if prompt:
        return prompt.text
    from app.telegram.messages import FALLBACK_PROMPT

    return FALLBACK_PROMPT


async def handle_dispatch(queue_url: str) -> dict:
    results = {}

    try:
        results["digests"] = await dispatch_digests(queue_url)
    except Exception:
        logger.exception("Digest dispatch failed")
        results["digests"] = {"error": True}

    try:
        results["reminders"] = await dispatch_reminders(queue_url)
    except Exception:
        logger.exception("Reminder dispatch failed")
        results["reminders"] = {"error": True}

    try:
        results["rediscovery"] = await dispatch_rediscovery(queue_url)
    except Exception:
        logger.exception("Rediscovery dispatch failed")
        results["rediscovery"] = {"error": True}

    return {"status": "ok", "results": results}
