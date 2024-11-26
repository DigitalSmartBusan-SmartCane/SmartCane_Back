"""empty message

Revision ID: 978d307486ce
Revises: f51037c92c7d
Create Date: 2024-11-13 11:46:02.154838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '978d307486ce'
down_revision: Union[str, None] = 'f51037c92c7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
