"""Create scheduled_messages table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "gratitude_bot"


def upgrade() -> None:
    op.create_table(
        "scheduled_messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                f"{_SCHEMA}.users.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "message_type",
            sa.Enum("weekly", "monthly", "yearly", name="message_type_enum"),
            nullable=False,
        ),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column(
            "entry_ids",
            postgresql.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("entry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.Enum("pending", "sent", "failed", name="message_status_enum"),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        schema=_SCHEMA,
    )

    op.create_foreign_key(
        "fk_scheduled_messages_user",
        "scheduled_messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
        source_schema=_SCHEMA,
        referent_schema=_SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("scheduled_messages", schema=_SCHEMA)
    op.execute("DROP TYPE IF EXISTS message_type_enum")
    op.execute("DROP TYPE IF EXISTS message_status_enum")
