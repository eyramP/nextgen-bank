"""add_bank_account_table

Revision ID: 2d76c7a89092
Revises: 52087587c8a7
Create Date: 2026-07-22 20:33:43.933835
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

revision: str = '2d76c7a89092'
down_revision: Union[str, None] = '52087587c8a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bankaccount',
        sa.Column('account_type', sa.Enum('Current', 'Savings', 'FixedDeposit', 'Business', name='accounttypeenum'), nullable=False),
        sa.Column('currency', sa.Enum('USD', 'EUR', 'GBP', 'GHS', name='accountcurrencyenum'), nullable=False),
        sa.Column('account_status', sa.Enum('Active', 'Inactive', 'Pending', 'Closed', 'Frozen', name='accountstatusenum'), nullable=False),
        sa.Column('account_number', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('account_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('kyc_submitted', sa.Boolean(), nullable=False),
        sa.Column('kyc_verified', sa.Boolean(), nullable=False),
        sa.Column('kyc_verified_by', sa.Uuid(), nullable=True),
        sa.Column('interest_rate', sa.Float(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('kyc_verified_on', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_bankaccount_account_number'), 'bankaccount', ['account_number'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_bankaccount_account_number'), table_name='bankaccount')
    op.drop_table('bankaccount')