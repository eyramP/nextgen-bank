"""make_kyc_verified_on_nullable

Revision ID: 9b41f9a12881
Revises: 2d76c7a89092
Create Date: 2026-07-23 20:05:01.138434

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9b41f9a12881'
down_revision: Union[str, None] = '2d76c7a89092'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "bankaccount", "kyc_verified_on",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "bankaccount", "kyc_verified_on",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )