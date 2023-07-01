"""is_delete column is added in agents table

Revision ID: 61257b93d83e
Revises: 1d54db311055
Create Date: 2023-06-28 15:26:43.626146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61257b93d83e'
down_revision = '1d54db311055'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('is_deleted', sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column('agents', 'is_deleted')