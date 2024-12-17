"""empty message

Revision ID: f51037c92c7d
Revises: 106187772cd4
Create Date: 2024-11-12 12:13:39.117653

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f51037c92c7d'
down_revision: Union[str, None] = '106187772cd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
