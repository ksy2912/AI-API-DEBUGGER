"""pgvector embeddings and generated tests

Revision ID: 004
Revises: 003
Create Date: 2026-06-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector may be unavailable on some hosts (e.g. Render free Postgres)
    vector_available = False
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        vector_available = True
    except Exception:
        pass

    if vector_available:
        op.create_table(
            "log_embeddings",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("source_type", sa.String(length=50), nullable=False),
            sa.Column("source_id", sa.UUID(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("embedding", Vector(1536), nullable=False),
            sa.Column("metadata", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_log_embeddings_source", "log_embeddings", ["source_type", "source_id"])

    http_method = sa.dialects.postgresql.ENUM(
        "GET", "POST", "PUT", "DELETE", "PATCH", name="http_method", create_type=False
    )

    op.create_table(
        "generated_tests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("api_request_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("test_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("method", http_method, nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("headers", sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("expected_status", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["api_request_id"], ["api_requests.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("generated_tests")
    try:
        op.drop_index("ix_log_embeddings_source", table_name="log_embeddings")
        op.drop_table("log_embeddings")
    except Exception:
        pass
