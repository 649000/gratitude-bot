"""Seed prompts into the database.

Usage:
    APP_ENV=dev uv run python scripts/seed.py
"""

import asyncio

from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.seed_data import prompts


async def seed() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM prompts"))
        count = result.scalar()
        if count and count > 0:
            print(f"Prompts table already has {count} rows — skipping seed.")
            return

        for prompt in prompts:
            await conn.execute(
                text("INSERT INTO prompts (text, category) VALUES (:text, :category)"),
                {"text": prompt["text"], "category": prompt["category"]},
            )

        await conn.commit()
        print(f"Seeded {len(prompts)} prompts into {settings.database_url}")


if __name__ == "__main__":
    asyncio.run(seed())
