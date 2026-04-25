"""add role to users

Revision ID: d0db296d2629
Revises: 3720ae06f582
Create Date: 2026-04-11 22:06:51.370964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0db296d2629'
down_revision: Union[str, Sequence[str], None] = '3720ae06f582'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
