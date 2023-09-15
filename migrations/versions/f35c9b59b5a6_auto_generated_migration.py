"""auto-generated migration

Revision ID: f35c9b59b5a6
Revises: 661ec8a4c32e
Create Date: 2023-09-15 12:47:15.594246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f35c9b59b5a6'
down_revision = '661ec8a4c32e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('models', sa.Column('state', sa.String(), nullable=False, server_default='INSTALLED'))


def downgrade() -> None:
    op.drop_column('models', 'state')
