import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.telegram.handlers.db import create_entry, get_entries, get_or_create_user


@pytest.mark.asyncio
async def test_create_entry_via_db(session: AsyncSession):
    user = await get_or_create_user(
        session, telegram_id=123456789, username="testuser", first_name="Test"
    )
    entry = await create_entry(session, user.id, "I am grateful for this test")
    assert entry.content == "I am grateful for this test"
    assert entry.user_id == user.id
    assert entry.source == "telegram"


@pytest.mark.asyncio
async def test_list_entries_via_db(session: AsyncSession):
    user = await get_or_create_user(session, telegram_id=987654321, username="another")
    for i in range(3):
        await create_entry(session, user.id, f"Gratitude {i}")

    entries = await get_entries(session, user.id)
    assert len(entries) == 3
