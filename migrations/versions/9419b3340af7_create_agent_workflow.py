"""create agent workflow

Revision ID: 9419b3340af7
Revises: fe234ea6e9bc
Create Date: 2023-07-18 16:46:03.497943

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9419b3340af7'
down_revision = 'fe234ea6e9bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agent_workflows',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('organisation_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                   )

    op.create_table('agent_workflow_steps',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('step_type', sa.String(), nullable=False),
                    sa.Column('agent_workflow_id', sa.Integer(), nullable=True),
                    sa.Column('action_reference_id', sa.Integer(), nullable=True),
                    sa.Column('action_type', sa.String(), nullable=True),
                    sa.Column('unique_id', sa.String(), nullable=False),
                    sa.Column('next_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('agent_workflow_step_tools',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('unique_id', sa.String(), nullable=True),
                    sa.Column('tool_name', sa.String(), nullable=True),
                    sa.Column('input_instruction', sa.Text(), nullable=True),
                    sa.Column('output_instruction', sa.Text(), nullable=True),
                    sa.Column('history_enabled', sa.Boolean(), nullable=True),
                    sa.Column('completion_prompt', sa.Text(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade() -> None:
    op.drop_table('agent_workflows')
    op.drop_table('agent_workflow_steps')
    op.drop_table('agent_workflow_step_tools')
