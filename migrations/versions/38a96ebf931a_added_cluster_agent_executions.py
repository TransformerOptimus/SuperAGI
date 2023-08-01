"""Added cluster agent executions

Revision ID: 38a96ebf931a
Revises: ce3bfaa4159c
Create Date: 2023-07-28 10:52:06.782523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38a96ebf931a'
down_revision = 'ce3bfaa4159c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cluster_agent_executions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_execution_id', sa.Integer(), nullable=True),
    sa.Column('cluster_execution_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('knowledge_configs', 'knowledge_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('knowledges', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('vector_db_configs', 'vector_db_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('vector_db_indices', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('vector_dbs', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('vector_dbs', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('vector_db_indices', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('vector_db_configs', 'vector_db_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('knowledges', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('knowledge_configs', 'knowledge_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_table('cluster_agent_executions')
    # ### end Alembic commands ###
