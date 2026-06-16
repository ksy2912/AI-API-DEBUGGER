"""debug sessions

Revision ID: 003
Revises: 002
Create Date: 2026-06-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    debug_mode = postgresql.ENUM("single", "multi_agent", name="debug_mode", create_type=False)
    debug_mode.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "debug_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mode", debug_mode, nullable=False),
        sa.Column("cause", sa.Text(), nullable=True),
        sa.Column("fix", sa.Text(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("suggested_fix", sa.Text(), nullable=True),
        sa.Column("validated_fix", sa.Text(), nullable=True),
        sa.Column("optimized_request", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("agent_trace", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("llm_used", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["request_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("debug_sessions")
    op.execute("DROP TYPE IF EXISTS debug_mode")
