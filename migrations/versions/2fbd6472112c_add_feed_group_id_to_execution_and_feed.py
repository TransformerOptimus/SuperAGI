"""add feed group id to execution and feed

Revision ID: 2fbd6472112c
Revises: 5184645e9f12
Create Date: 2023-08-01 17:09:16.183863

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2fbd6472112c'
down_revision = '5184645e9f12'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agent_executions',
                  sa.Column('current_feed_group_id', sa.String(), nullable=True, server_default="DEFAULT"))
    op.add_column('agent_execution_feeds', sa.Column('feed_group_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('agent_executions', 'current_feed_group_id')
    op.drop_column('agent_execution_feeds', 'feed_group_id')
