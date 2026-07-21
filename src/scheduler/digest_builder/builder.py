import logging
from datetime import date, datetime, timedelta
from uuid import UUID

import pytz
from sqlalchemy import select

from scheduler.common.database import async_session_factory
from scheduler.common.models import GratitudeEntry, ScheduledMessage, User
from scheduler.common.scoring import select_highlights
from scheduler.common.summarizer import DigestSummarizer, get_summarizer

logger = logging.getLogger(__name__)

_summarizer: DigestSummarizer | None = None


def _get_summarizer() -> DigestSummarizer:
    global _summarizer
    if _summarizer is None:
        _summarizer = get_summarizer()
    return _summarizer


_WEEKLY_N = 5
_MONTHLY_N = 8
_YEARLY_N = 12


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


def _get_period(digest_type: str, user_tz: str) -> tuple[date, date]:
    utc = pytz.UTC
    now_utc = datetime.now(utc)
    offset_minutes = _parse_utc_offset(user_tz)
    tz = __import__("datetime", fromlist=["timezone"]).timezone(
        __import__("datetime", fromlist=["timedelta"]).timedelta(minutes=offset_minutes)
    )
    user_now = now_utc.astimezone(tz)
    today = user_now.date()

    if digest_type == "weekly":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif digest_type == "monthly":
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif digest_type == "yearly":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
    else:
        raise ValueError(f"Unknown digest type: {digest_type}")

    return start, end


def _get_top_n(digest_type: str) -> int:
    return {
        "weekly": _WEEKLY_N,
        "monthly": _MONTHLY_N,
        "yearly": _YEARLY_N,
    }.get(digest_type, _WEEKLY_N)


async def build_and_store_digest(
    user: User,
    digest_type: str,
) -> ScheduledMessage | None:
    start_date, end_date = _get_period(digest_type, user.timezone)

    async with async_session_factory() as session:
        entries = await _query_entries(session, user.id, start_date, end_date)

        if not entries:
            logger.debug("No entries for user %s in period %s–%s", user.id, start_date, end_date)
            return None

        highlights = select_highlights(entries, _get_top_n(digest_type))

        summarizer = _get_summarizer()
        result = await summarizer.summarize(
            user=user,
            digest_type=digest_type,
            period_start=start_date,
            period_end=end_date,
            highlights=highlights,
        )
        message_text = f"{result['intro']}\n\n{result['body']}"

        entry_ids = [str(e.id) for e in highlights]

        existing = await session.execute(
            select(ScheduledMessage).where(
                ScheduledMessage.user_id == user.id,
                ScheduledMessage.message_type == digest_type,
                ScheduledMessage.period_start == start_date,
                ScheduledMessage.period_end == end_date,
            )
        )
        msg = existing.scalar_one_or_none()

        if msg:
            msg.message_text = message_text
            msg.entry_ids = entry_ids
            msg.entry_count = len(highlights)
            msg.status = "pending"
        else:
            msg = ScheduledMessage(
                user_id=user.id,
                message_type=digest_type,
                message_text=message_text,
                entry_ids=entry_ids,
                period_start=start_date,
                period_end=end_date,
                entry_count=len(highlights),
                status="pending",
            )
            session.add(msg)

        await session.commit()
        logger.info(
            "Stored %s digest for user %s: %d entries, period %s–%s",
            digest_type,
            user.id,
            len(highlights),
            start_date,
            end_date,
        )
        return msg


async def _query_entries(session, user_id: UUID, start: date, end: date):
    utc = pytz.UTC
    start_dt = utc.localize(datetime(start.year, start.month, start.day, 0, 0, 0))
    end_dt = utc.localize(datetime(end.year, end.month, end.day, 23, 59, 59))

    result = await session.execute(
        select(GratitudeEntry)
        .where(
            GratitudeEntry.user_id == user_id,
            GratitudeEntry.created_at >= start_dt,
            GratitudeEntry.created_at <= end_dt,
        )
        .order_by(GratitudeEntry.created_at.desc())
    )
    return list(result.scalars().all())
