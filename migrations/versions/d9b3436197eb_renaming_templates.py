"""renaming templates

Revision ID: d9b3436197eb
Revises: 3356a2f89a33
Create Date: 2023-06-10 09:28:28.262705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9b3436197eb'
down_revision = '3356a2f89a33'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('agent_templates', 'agent_workflows')
    op.rename_table('agent_template_steps', 'agent_workflow_steps')
    with op.batch_alter_table('agent_workflow_steps') as bop:
        bop.alter_column('agent_template_id', new_column_name='agent_workflow_id')
    with op.batch_alter_table('agents') as bop:
        bop.alter_column('agent_template_id', new_column_name='agent_workflow_id')


def downgrade() -> None:
    op.rename_table('agent_workflows', 'agent_templates')
    op.rename_table('agent_workflow_steps', 'agent_template_steps')
    with op.batch_alter_table('agent_templates') as bop:
        bop.alter_column('agent_workflow_id', new_column_name='agent_template_id')
    with op.batch_alter_table('agents') as bop:
        bop.alter_column('agent_workflow_id', new_column_name='agent_template_id')
