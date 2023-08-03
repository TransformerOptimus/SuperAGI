"""update agent workflow tables

Revision ID: fe234ea6e9bc
Revises: d8315244ea43
Create Date: 2023-07-18 16:46:29.305378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe234ea6e9bc'
down_revision = 'd8315244ea43'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('agent_workflows', 'iteration_workflows')
    op.rename_table('agent_workflow_steps', 'iteration_workflow_steps')

    with op.batch_alter_table('iteration_workflow_steps') as bop:
        bop.alter_column('agent_workflow_id', new_column_name='iteration_workflow_id')

    with op.batch_alter_table('agent_executions') as bop:
        bop.alter_column('current_step_id', new_column_name='current_agent_step_id')


    op.add_column('agent_executions', sa.Column('iteration_workflow_step_id', sa.Integer(), nullable=True))
    op.add_column('iteration_workflows',
                  sa.Column('has_task_queue', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    op.rename_table('iteration_workflows', 'agent_workflows')
    op.rename_table('iteration_workflow_steps', 'agent_workflow_steps')
    op.drop_column('agent_executions', 'iteration_workflow_step_id')
    op.drop_column('agent_workflows', 'has_task_queue')
