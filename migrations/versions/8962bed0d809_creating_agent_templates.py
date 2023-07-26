"""creating agent templates

Revision ID: 8962bed0d809
Revises: d9b3436197eb
Create Date: 2023-06-10 15:40:08.942612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8962bed0d809'
down_revision = 'd9b3436197eb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agent_templates',
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('organisation_id', sa.Integer(), nullable=True),
                    sa.Column('agent_workflow_id', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('agent_template_configs',
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('agent_template_id', sa.Integer(), nullable=True),
                    sa.Column('key', sa.String(), nullable=True),
                    sa.Column('value', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index("ix_atc_agnt_template_id_key", "agent_template_configs", ['agent_template_id', 'key'])
    op.create_index("ix_agt_agnt_organisation_id", "agent_templates", ['organisation_id'])
    op.create_index("ix_agt_agnt_workflow_id", "agent_templates", ['agent_workflow_id'])
    op.create_index("ix_agt_agnt_name", "agent_templates", ['name'])


def downgrade() -> None:
    op.drop_table('agent_template_configs')
    op.drop_table('agent_templates')
