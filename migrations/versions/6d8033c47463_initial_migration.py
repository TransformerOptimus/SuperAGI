"""Initial migration

Revision ID: 6d8033c47463
Revises: 
Create Date: 2023-05-29 08:14:13.019570

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6d8033c47463'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('agent_configurations',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('agent_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('key', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('value', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='agent_configurations_pkey')
                    )
    op.create_table('organisations',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='organisations_pkey')
                    )
    op.create_table('budgets',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('budget', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
                    sa.Column('cycle', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='budgets_pkey')
                    )
    op.create_table('agent_execution_feeds',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('agent_execution_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('agent_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('feed', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='agent_execution_feeds_pkey')
                    )
    op.create_table('projects',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('organisation_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='projects_pkey')
                    )
    op.create_table('agent_executions',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('agent_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('last_execution_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='agent_executions_pkey')
                    )
    op.create_table('tools',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('folder_name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('class_name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('file_name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='tools_pkey')
                    )
    op.create_table('users',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('organisation', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='users_pkey'),
                    sa.UniqueConstraint('email', name='users_email_key')
                    )
    op.create_table('agents',
                    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='agents_pkey')
                    )

def downgrade() -> None:
    pass
