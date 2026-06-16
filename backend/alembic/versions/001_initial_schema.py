"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    http_method = postgresql.ENUM(
        "GET", "POST", "PUT", "DELETE", "PATCH", name="http_method", create_type=False
    )
    auth_type = postgresql.ENUM(
        "none", "bearer", "basic", "api_key", name="auth_type", create_type=False
    )
    http_method.create(op.get_bind(), checkfirst=True)
    auth_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "api_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("method", http_method, nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("query_params", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("auth_type", auth_type, nullable=False),
        sa.Column("auth_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("api_requests")
    op.drop_table("collections")
    op.execute("DROP TYPE IF EXISTS auth_type")
    op.execute("DROP TYPE IF EXISTS http_method")
