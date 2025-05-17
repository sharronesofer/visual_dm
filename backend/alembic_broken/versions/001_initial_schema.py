"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types using SQLAlchemy
    budget_period = postgresql.ENUM('monthly', 'quarterly', 'yearly', name='budget_period', create_type=True)
    budget_scope = postgresql.ENUM('project', 'team', 'service', name='budget_scope', create_type=True)
    cleanup_status = postgresql.ENUM('identified', 'notified', 'approved', 'cleaned', 'failed', 'exempted', name='cleanup_status', create_type=True)

    # Create cloud_providers table
    op.create_table(
        'cloud_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('api_credentials', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create cloud_resources table
    op.create_table(
        'cloud_resources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.String(length=200), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['provider_id'], ['cloud_providers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cost_entries table
    op.create_table(
        'cost_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=200), nullable=True),
        sa.Column('cost_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['provider_id'], ['cloud_providers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('period', postgresql.ENUM('monthly', 'quarterly', 'yearly', name='budget_period'), nullable=False),
        sa.Column('scope_type', postgresql.ENUM('project', 'team', 'service', name='budget_scope'), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=False),
        sa.Column('alert_thresholds', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create budget_alerts table
    op.create_table(
        'budget_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('current_usage', sa.Float(), nullable=False),
        sa.Column('percentage_used', sa.Float(), nullable=False),
        sa.Column('alert_time', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['budget_id'], ['budgets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create cleanup_entries table
    op.create_table(
        'cleanup_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('estimated_savings', sa.Float(), nullable=True),
        sa.Column('status', postgresql.ENUM('identified', 'notified', 'approved', 'cleaned', 'failed', 'exempted', name='cleanup_status'), nullable=False, server_default='identified'),
        sa.Column('identified_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('notified_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('cleaned_at', sa.DateTime(), nullable=True),
        sa.Column('exemption_reason', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['resource_id'], ['cloud_resources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_cost_entries_start_time', 'cost_entries', ['start_time'])
    op.create_index('ix_cost_entries_end_time', 'cost_entries', ['end_time'])
    op.create_index('ix_cost_entries_service_name', 'cost_entries', ['service_name'])
    op.create_index('ix_cloud_resources_resource_id', 'cloud_resources', ['resource_id'])
    op.create_index('ix_cloud_resources_resource_type', 'cloud_resources', ['resource_type'])
    op.create_index('ix_budgets_scope_type', 'budgets', ['scope_type'])
    op.create_index('ix_budgets_scope_id', 'budgets', ['scope_id'])
    op.create_index('ix_budget_alerts_alert_time', 'budget_alerts', ['alert_time'])
    op.create_index('ix_cleanup_entries_status', 'cleanup_entries', ['status'])
    op.create_index('ix_cleanup_entries_identified_at', 'cleanup_entries', ['identified_at'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_cleanup_entries_identified_at')
    op.drop_index('ix_cleanup_entries_status')
    op.drop_index('ix_budget_alerts_alert_time')
    op.drop_index('ix_budgets_scope_id')
    op.drop_index('ix_budgets_scope_type')
    op.drop_index('ix_cloud_resources_resource_type')
    op.drop_index('ix_cloud_resources_resource_id')
    op.drop_index('ix_cost_entries_service_name')
    op.drop_index('ix_cost_entries_end_time')
    op.drop_index('ix_cost_entries_start_time')

    # Drop tables
    op.drop_table('cleanup_entries')
    op.drop_table('budget_alerts')
    op.drop_table('budgets')
    op.drop_table('cost_entries')
    op.drop_table('cloud_resources')
    op.drop_table('cloud_providers')

    # Drop enum types
    op.execute('DROP TYPE cleanup_status')
    op.execute('DROP TYPE budget_scope')
    op.execute('DROP TYPE budget_period') 