import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_gratitude(client: AsyncClient, session):
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
    )
    session.add(user)
    await session.flush()

    response = await client.post(
        "/api/v1/gratitudes",
        params={"user_id": str(user.id)},
        json={"content": "I am grateful for this test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "I am grateful for this test"
    assert data["user_id"] == str(user.id)


@pytest.mark.asyncio
async def test_list_gratitudes(client: AsyncClient, session):
    user = User(
        telegram_id=987654321,
        username="another",
    )
    session.add(user)
    await session.flush()

    from app.models.gratitude import GratitudeEntry

    for i in range(3):
        session.add(
            GratitudeEntry(
                user_id=user.id,
                content=f"Gratitude {i}",
                source="telegram",
            )
        )
    await session.flush()

    response = await client.get(
        "/api/v1/gratitudes",
        params={"user_id": str(user.id)},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
