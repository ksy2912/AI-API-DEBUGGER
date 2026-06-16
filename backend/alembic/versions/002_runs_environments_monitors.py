"""runs history, environments, monitors

Revision ID: 002
Revises: 001
Create Date: 2026-06-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "environments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("variables", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("secret_keys", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "auth_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "auth_type",
            postgresql.ENUM(
                "none", "bearer", "basic", "api_key", name="auth_type", create_type=False
            ),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.add_column(
        "api_requests",
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "api_requests",
        sa.Column("auth_profile_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_api_requests_environment_id",
        "api_requests",
        "environments",
        ["environment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_api_requests_auth_profile_id",
        "api_requests",
        "auth_profiles",
        ["auth_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "monitor_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("interval_seconds", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["api_request_id"], ["api_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "request_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("api_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("monitor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("environment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "method",
            postgresql.ENUM(
                "GET", "POST", "PUT", "DELETE", "PATCH", name="http_method", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("request_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("request_body", sa.Text(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["api_request_id"], ["api_requests.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["environment_id"], ["environments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["monitor_id"], ["monitor_schedules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("request_runs")
    op.drop_table("monitor_schedules")
    op.drop_constraint("fk_api_requests_auth_profile_id", "api_requests", type_="foreignkey")
    op.drop_constraint("fk_api_requests_environment_id", "api_requests", type_="foreignkey")
    op.drop_column("api_requests", "auth_profile_id")
    op.drop_column("api_requests", "environment_id")
    op.drop_table("auth_profiles")
    op.drop_table("environments")
