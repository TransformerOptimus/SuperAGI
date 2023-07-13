"""delete_agent_feature

Revision ID: 8bc7b3eaed55
Revises: 467e85d5e1cd
Create Date: 2023-07-13 12:39:28.781355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bc7b3eaed55'
down_revision = '467e85d5e1cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('is_deleted', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'is_deleted')
