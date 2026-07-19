"""Create initial tables

Revision ID: 0001
Revises:
Create Date: 2026-07-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "gratitude_bot"


def upgrade() -> None:
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {_SCHEMA}"))

    op.create_table(
        "prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        schema=_SCHEMA,
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("telegram_id", sa.BigInteger(), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        schema=_SCHEMA,
    )

    op.create_table(
        "gratitude_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(16), nullable=False, server_default="telegram"),
        sa.Column("starred", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        schema=_SCHEMA,
    )

    op.create_foreign_key(
        "fk_gratitude_entries_user",
        "gratitude_entries", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE",
        source_schema=_SCHEMA,
        referent_schema=_SCHEMA,
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column("digest_weekly_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("digest_monthly_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("digest_yearly_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("rediscovery_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_rediscovery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        schema=_SCHEMA,
    )

    op.create_foreign_key(
        "fk_user_preferences_user",
        "user_preferences", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE",
        source_schema=_SCHEMA,
        referent_schema=_SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("user_preferences", schema=_SCHEMA)
    op.drop_table("gratitude_entries", schema=_SCHEMA)
    op.drop_table("users", schema=_SCHEMA)
    op.drop_table("prompts", schema=_SCHEMA)
    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {_SCHEMA}"))
