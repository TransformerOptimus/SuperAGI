"""delete_agent_feature

Revision ID: cac478732572
Revises: e39295ec089c
Create Date: 2023-07-13 17:18:42.003412

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cac478732572'
down_revision = 'e39295ec089c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('is_deleted', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('agents', 'is_deleted')
