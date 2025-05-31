"""
Migration: Create Economy System Tables

This migration creates all the necessary tables for the economy system including
resources, markets, trade routes, and commodity futures.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_economy_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create economy system tables."""
    
    # Create resources table
    op.create_table(
        'resources',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), default=0.0),
        sa.Column('base_value', sa.Float(), default=0.0),
        sa.Column('rarity', sa.String(20), default='common'),
        sa.Column('description', sa.String(500), default=''),
        sa.Column('is_tradeable', sa.Boolean(), default=True),
        sa.Column('is_consumable', sa.Boolean(), default=False),
        sa.Column('weight', sa.Float(), default=0.0),
        sa.Column('volume', sa.Float(), default=0.0),
        sa.Column('durability', sa.Float(), default=100.0),
        sa.Column('quality', sa.String(20), default='standard'),
        sa.Column('minimum_viable_amount', sa.Float(), default=0.0),
        sa.Column('maximum_capacity', sa.Float(), nullable=True),
        sa.Column('production_rate', sa.Float(), default=0.0),
        sa.Column('consumption_rate', sa.Float(), default=0.0),
        sa.Column('seasonal_modifier', sa.Float(), default=1.0),
        sa.Column('resource_metadata', sa.JSON(), default=dict),
        sa.Column('tags', sa.JSON(), default=list),
        sa.Column('properties', sa.JSON(), default=dict)
    )
    
    # Create indexes for resources table
    op.create_index('idx_resources_name', 'resources', ['name'])
    op.create_index('idx_resources_type', 'resources', ['resource_type'])
    op.create_index('idx_resources_region', 'resources', ['region_id'])
    op.create_index('idx_resources_rarity', 'resources', ['rarity'])
    op.create_index('idx_resources_tradeable', 'resources', ['is_tradeable'])
    op.create_index('idx_resources_amount', 'resources', ['amount'])
    op.create_index('idx_resources_value', 'resources', ['base_value'])
    
    # Create markets table
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('market_type', sa.String(50), default='general'),
        sa.Column('price_modifiers', sa.JSON(), default=dict),
        sa.Column('supply_demand', sa.JSON(), default=dict),
        sa.Column('trading_volume', sa.JSON(), default=dict),
        sa.Column('tax_rate', sa.Float(), default=0.05),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('market_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for markets table
    op.create_index('idx_markets_name', 'markets', ['name'])
    op.create_index('idx_markets_region', 'markets', ['region_id'])
    op.create_index('idx_markets_type', 'markets', ['market_type'])
    op.create_index('idx_markets_active', 'markets', ['is_active'])
    op.create_index('idx_markets_tax_rate', 'markets', ['tax_rate'])
    
    # Create trade_routes table
    op.create_table(
        'trade_routes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('origin_region_id', sa.Integer(), nullable=False),
        sa.Column('destination_region_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),  # Primary resource
        sa.Column('resource_ids', sa.JSON(), default=list),  # All resources traded
        sa.Column('volume', sa.Float(), default=0.0),
        sa.Column('profit', sa.Float(), default=0.0),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_trade_time', sa.DateTime(), nullable=True),
        sa.Column('route_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for trade_routes table
    op.create_index('idx_trade_routes_name', 'trade_routes', ['name'])
    op.create_index('idx_trade_routes_origin', 'trade_routes', ['origin_region_id'])
    op.create_index('idx_trade_routes_destination', 'trade_routes', ['destination_region_id'])
    op.create_index('idx_trade_routes_resource', 'trade_routes', ['resource_id'])
    op.create_index('idx_trade_routes_status', 'trade_routes', ['status'])
    op.create_index('idx_trade_routes_active', 'trade_routes', ['is_active'])
    op.create_index('idx_trade_routes_volume', 'trade_routes', ['volume'])
    op.create_index('idx_trade_routes_profit', 'trade_routes', ['profit'])
    
    # Create commodity_futures table
    op.create_table(
        'commodity_futures',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('market_id', sa.String(), nullable=False),
        sa.Column('seller_id', sa.String(), nullable=False),
        sa.Column('buyer_id', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('strike_price', sa.Float(), nullable=False),
        sa.Column('expiration_date', sa.DateTime(), nullable=False),
        sa.Column('settlement_date', sa.DateTime(), nullable=True),
        sa.Column('is_settled', sa.Boolean(), default=False),
        sa.Column('premium', sa.Float(), default=0.0),
        sa.Column('contract_type', sa.String(20), default='future'),
        sa.Column('status', sa.String(20), default='open'),
        sa.Column('terms', sa.JSON(), default=dict)
    )
    
    # Create indexes for commodity_futures table
    op.create_index('idx_futures_resource', 'commodity_futures', ['resource_id'])
    op.create_index('idx_futures_market', 'commodity_futures', ['market_id'])
    op.create_index('idx_futures_seller', 'commodity_futures', ['seller_id'])
    op.create_index('idx_futures_buyer', 'commodity_futures', ['buyer_id'])
    op.create_index('idx_futures_expiration', 'commodity_futures', ['expiration_date'])
    op.create_index('idx_futures_status', 'commodity_futures', ['status'])
    op.create_index('idx_futures_settled', 'commodity_futures', ['is_settled'])
    op.create_index('idx_futures_strike_price', 'commodity_futures', ['strike_price'])
    
    # Create economic_transactions table for transaction history
    op.create_table(
        'economic_transactions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),  # buy, sell, transfer, trade
        sa.Column('buyer_id', sa.String(), nullable=True),
        sa.Column('seller_id', sa.String(), nullable=True),
        sa.Column('market_id', sa.Integer(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_value', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), default=0.0),
        sa.Column('fees', sa.Float(), default=0.0),
        sa.Column('origin_region_id', sa.Integer(), nullable=True),
        sa.Column('destination_region_id', sa.Integer(), nullable=True),
        sa.Column('trade_route_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('transaction_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for economic_transactions table
    op.create_index('idx_transactions_type', 'economic_transactions', ['transaction_type'])
    op.create_index('idx_transactions_buyer', 'economic_transactions', ['buyer_id'])
    op.create_index('idx_transactions_seller', 'economic_transactions', ['seller_id'])
    op.create_index('idx_transactions_market', 'economic_transactions', ['market_id'])
    op.create_index('idx_transactions_resource', 'economic_transactions', ['resource_id'])
    op.create_index('idx_transactions_created', 'economic_transactions', ['created_at'])
    op.create_index('idx_transactions_value', 'economic_transactions', ['total_value'])
    op.create_index('idx_transactions_status', 'economic_transactions', ['status'])
    
    # Create price_history table for tracking price changes
    op.create_table(
        'price_history',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('market_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), default=0.0),
        sa.Column('supply', sa.Float(), default=0.0),
        sa.Column('demand', sa.Float(), default=0.0),
        sa.Column('price_modifier', sa.Float(), default=1.0),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=True),  # tick, trade, event, manual
        sa.Column('price_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for price_history table
    op.create_index('idx_price_history_resource', 'price_history', ['resource_id'])
    op.create_index('idx_price_history_market', 'price_history', ['market_id'])
    op.create_index('idx_price_history_timestamp', 'price_history', ['timestamp'])
    op.create_index('idx_price_history_price', 'price_history', ['price'])
    op.create_index('idx_price_history_event', 'price_history', ['event_type'])
    op.create_index('idx_price_history_resource_market', 'price_history', ['resource_id', 'market_id'])
    
    # Create economic_events table for tracking economic events
    op.create_table(
        'economic_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.Column('market_id', sa.Integer(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('trade_route_id', sa.Integer(), nullable=True),
        sa.Column('severity', sa.String(20), default='minor'),  # minor, moderate, major, critical
        sa.Column('impact_type', sa.String(50), nullable=True),  # price, supply, demand, volume
        sa.Column('impact_value', sa.Float(), default=0.0),
        sa.Column('duration', sa.Integer(), default=1),  # Duration in ticks
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('event_metadata', sa.JSON(), default=dict)
    )
    
    # Create indexes for economic_events table
    op.create_index('idx_economic_events_type', 'economic_events', ['event_type'])
    op.create_index('idx_economic_events_region', 'economic_events', ['region_id'])
    op.create_index('idx_economic_events_market', 'economic_events', ['market_id'])
    op.create_index('idx_economic_events_resource', 'economic_events', ['resource_id'])
    op.create_index('idx_economic_events_severity', 'economic_events', ['severity'])
    op.create_index('idx_economic_events_active', 'economic_events', ['is_active'])
    op.create_index('idx_economic_events_expires', 'economic_events', ['expires_at'])
    op.create_index('idx_economic_events_created', 'economic_events', ['created_at'])

def downgrade():
    """Drop economy system tables."""
    op.drop_table('economic_events')
    op.drop_table('price_history')
    op.drop_table('economic_transactions')
    op.drop_table('commodity_futures')
    op.drop_table('trade_routes')
    op.drop_table('markets')
    op.drop_table('resources') 