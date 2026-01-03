"""Add budget and spending to User model

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2024-01-01 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('monthly_budget', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('monthly_spending', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('users', sa.Column('last_usage_reset', sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column('users', 'last_usage_reset')
    op.drop_column('users', 'monthly_spending')
    op.drop_column('users', 'monthly_budget')
