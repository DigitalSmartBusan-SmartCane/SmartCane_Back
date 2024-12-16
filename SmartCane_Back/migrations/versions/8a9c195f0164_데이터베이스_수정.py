"""데이터베이스 수정

Revision ID: 8a9c195f0164
Revises: d9d2a68e7e86
Create Date: 2024-11-15 09:12:26.939808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9c195f0164'
down_revision: Union[str, None] = 'd9d2a68e7e86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
