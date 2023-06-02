"""adding agent templates

Revision ID: 1dd573b51af0
Revises: 115a710c4685
Create Date: 2023-05-30 16:20:58.096655

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '1dd573b51af0'
down_revision = '115a710c4685'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'agent_templates',
        sa.Column('id', sa.Integer()),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.TEXT()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'agent_template_steps',
        sa.Column('id', sa.Integer()),
        sa.Column('agent_template_id', sa.Integer()),
        sa.Column('unique_id', sa.String()),
        sa.Column('prompt', sa.TEXT()),
        sa.Column('variables', sa.TEXT()),
        sa.Column('step_type', sa.String(length=256)),
        sa.Column('output_type', sa.String(length=256)),
        sa.Column('next_step_id', sa.Integer()),
        sa.Column('history_enabled', sa.Boolean()),
        sa.Column('completion_prompt', sa.TEXT()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column('agents', sa.Column('agent_template_id', sa.Integer()))
    op.create_index("ix_agents_agnt_template_id", "agents", ['agent_template_id'])

    op.add_column('agent_executions', sa.Column('current_step_id', sa.Integer()))
    op.create_index("ix_aea_step_id", "agent_executions", ['current_step_id'])

    op.create_index("ix_ats_unique_id", "agent_template_steps", ['unique_id'])
    op.create_index("ix_at_name", "agent_templates", ['name'])


def downgrade() -> None:
    pass
