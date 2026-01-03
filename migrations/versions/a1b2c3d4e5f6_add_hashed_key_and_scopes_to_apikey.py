"""Add hashed_key and scopes to APIKey

Revision ID: a1b2c3d4e5f6
Revises: 1234567890ab
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '1234567890ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('api_keys', sa.Column('hashed_key', sa.String(), nullable=False))
    op.add_column('api_keys', sa.Column('scopes', sa.String(), nullable=False, server_default='chat analytics'))
    op.drop_column('api_keys', 'key')


def downgrade() -> None:
    op.add_column('api_keys', sa.Column('key', sa.String(), nullable=False))
    op.drop_column('api_keys', 'scopes')
    op.drop_column('api_keys', 'hashed_key')
