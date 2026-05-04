"""add cheat_mode table

Revision ID: a4f2c8d9e6b7
Revises: 922b6da97d7e
Create Date: 2026-05-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a4f2c8d9e6b7"
down_revision = "922b6da97d7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cheat_mode",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.execute(sa.text("INSERT INTO cheat_mode (id, enabled) VALUES (1, false)"))


def downgrade() -> None:
    op.drop_table("cheat_mode")
