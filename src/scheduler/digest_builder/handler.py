import json
import logging

from sqlalchemy import select

from scheduler.common.database import async_session_factory
from scheduler.common.models import User, UserPreference
from scheduler.digest_builder.builder import build_and_store_digest

logger = logging.getLogger(__name__)

DIGEST_TYPE_MAP = {
    "weekly": "digest_weekly_enabled",
    "monthly": "digest_monthly_enabled",
    "yearly": "digest_yearly_enabled",
}


async def handle_digest_generation(digest_type: str) -> dict:
    if digest_type not in DIGEST_TYPE_MAP:
        logger.error("Unknown digest type: %s", digest_type)
        return {"status": "error", "message": f"Unknown digest type: {digest_type}"}

    pref_field = DIGEST_TYPE_MAP[digest_type]

    async with async_session_factory() as session:
        result = await session.execute(
            select(User)
            .join(UserPreference, UserPreference.user_id == User.id)
            .where(
                UserPreference.onboarding_completed == True,  # noqa: E712
                getattr(UserPreference, pref_field) == True,  # noqa: E712
            )
        )
        users = list(result.scalars().all())

    generated = 0
    errors = 0

    for user in users:
        try:
            msg = await build_and_store_digest(user, digest_type)
            if msg:
                generated += 1
        except Exception:
            logger.exception("Failed to generate %s digest for user %s", digest_type, user.id)
            errors += 1

    logger.info(
        "Digest generation complete: type=%s, generated=%d, errors=%d, users=%d",
        digest_type,
        generated,
        errors,
        len(users),
    )
    return {"status": "ok", "generated": generated, "errors": errors, "users": len(users)}


def lambda_handler(event: dict, _context: object) -> dict:
    logger.info("Received event: %s", json.dumps(event))

    digest_type = event.get("type", "")

    log_level = __import__("os").environ.get("LOG_LEVEL", "INFO")
    logger.setLevel(logging.DEBUG if log_level == "DEBUG" else logging.INFO)

    import asyncio

    result = asyncio.run(handle_digest_generation(digest_type))
    return result
