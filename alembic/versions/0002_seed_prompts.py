"""Seed initial gratitude prompts

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-19
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.sql import text

from app.seed_data import prompts

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "gratitude_bot"


def upgrade() -> None:
    conn = op.get_bind()
    for prompt in prompts:
        conn.execute(
            text(
                f"INSERT INTO {_SCHEMA}.prompts (text, category) "
                "VALUES (:text, :category)"
            ),
            {"text": prompt["text"], "category": prompt["category"]},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text(f"DELETE FROM {_SCHEMA}.prompts"))
