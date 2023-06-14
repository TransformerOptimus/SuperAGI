"""adding marketplace_template_id to agent tempaltes

Revision ID: 516ecc1c723d
Revises: 8962bed0d809
Create Date: 2023-06-13 17:10:06.262764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '516ecc1c723d'
down_revision = '8962bed0d809'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agent_templates', sa.Column('marketplace_template_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('agent_templates', sa.Column('marketplace_template_id', sa.Integer(), nullable=True))
