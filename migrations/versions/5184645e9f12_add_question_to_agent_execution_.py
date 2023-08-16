"""add question to agent execution permission

Revision ID: 5184645e9f12
Revises: 9419b3340af7
Create Date: 2023-07-21 08:16:14.702389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5184645e9f12'
down_revision = '9419b3340af7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agent_execution_permissions', sa.Column('question', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('agent_execution_permissions', "question")
