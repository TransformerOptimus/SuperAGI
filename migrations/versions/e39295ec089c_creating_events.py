"""creating events

Revision ID: e39295ec089c
Revises: 7a3e336c0fba
Create Date: 2023-06-30 12:23:12.269999

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e39295ec089c'
down_revision = '467e85d5e1cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('events',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_name', sa.String(), nullable=False),
    sa.Column('event_value', sa.Integer(), nullable=False),
    sa.Column('event_property', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('org_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Use naming convention similar to the reference code for the index creation
    op.create_index(op.f('ix_events_agent_id'), 'events', ['agent_id'], unique=False)
    op.create_index(op.f('ix_events_org_id'), 'events', ['org_id'], unique=False)
    op.create_index(op.f('ix_events_event_property'), 'events', ['event_property'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_events_event_property'), table_name='events')
    op.drop_index(op.f('ix_events_org_id'), table_name='events')
    op.drop_index(op.f('ix_events_agent_id'), table_name='events')
    op.drop_table('events')