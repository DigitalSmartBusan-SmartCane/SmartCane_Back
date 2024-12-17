"""Add username column to user table

Revision ID: d9d2a68e7e86
Revises: 978d307486ce
Create Date: 2024-11-13 11:46:30.662759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9d2a68e7e86'
down_revision: Union[str, None] = '978d307486ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
