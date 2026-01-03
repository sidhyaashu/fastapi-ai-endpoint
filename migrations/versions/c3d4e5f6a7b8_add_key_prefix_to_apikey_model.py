"""Add key_prefix to APIKey model

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2024-01-01 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('api_keys', sa.Column('key_prefix', sa.String(), nullable=False, server_default=''))
    op.create_index(op.f('ix_api_keys_key_prefix'), 'api_keys', ['key_prefix'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_api_keys_key_prefix'), table_name='api_keys')
    op.drop_column('api_keys', 'key_prefix')
