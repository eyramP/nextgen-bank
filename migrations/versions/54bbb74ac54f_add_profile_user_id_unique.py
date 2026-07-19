"""add_profile_user_id_unique

Revision ID: 54bbb74ac54f
Revises: b0773fae636b
Create Date: 2026-07-14 07:38:55.039972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '54bbb74ac54f'
down_revision: Union[str, None] = 'b0773fae636b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CONSTRAINT_NAME = "profile_user_id_key"


def upgrade() -> None:
    op.create_unique_constraint(CONSTRAINT_NAME, 'profile', ['user_id'])


def downgrade() -> None:
    op.drop_constraint(CONSTRAINT_NAME, 'profile', type_='unique')