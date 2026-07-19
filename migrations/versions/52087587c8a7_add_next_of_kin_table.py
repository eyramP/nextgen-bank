"""add_next_of_kin_table

Revision ID: 52087587c8a7
Revises: 54bbb74ac54f
Create Date: 2026-07-19 01:16:18.917096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '52087587c8a7'
down_revision: Union[str, None] = '54bbb74ac54f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'nextofkin',
        sa.Column('full_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('relationship', sa.Enum('Spouse', 'Parent', 'Child', 'Sibling', 'Other', name='relationshiptypeenum'), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('phone_number', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('address', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('city', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('nationality', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('id_number', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('passport_number', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('nextofkin')