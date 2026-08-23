"""Seed prompts into the database.

Usage:
    APP_ENV=dev uv run python src/app/seed.py
    or: make seed
"""

import asyncio

from sqlalchemy import text

from app.config import settings
from app.database import async_session_factory
from app.seed_data import prompts


async def seed() -> None:
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM prompts"))
        count = result.scalar()
        if count and count > 0:
            print(f"Prompts table already has {count} rows — skipping seed.")
            return

        for prompt in prompts:
            await session.execute(
                text("INSERT INTO prompts (text, category) VALUES (:text, :category)"),
                {"text": prompt["text"], "category": prompt["category"]},
            )

        await session.commit()
        print(f"Seeded {len(prompts)} prompts into {settings.database_url}")


if __name__ == "__main__":
    asyncio.run(seed())
