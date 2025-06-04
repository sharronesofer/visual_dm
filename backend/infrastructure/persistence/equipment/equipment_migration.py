"""
Equipment System Database Migration

Creates the equipment system database schema including:
- Equipment instances table
- Applied enchantments table  
- Maintenance records table
- Indexes for performance
- Foreign key constraints

This migration ensures the equipment system has proper database persistence.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Create equipment system tables"""
    
    # Create equipment_instances table
    op.create_table(
        'equipment_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', sa.String(100), nullable=False),
        sa.Column('slot', sa.String(50), nullable=False),
        sa.Column('current_durability', sa.Integer, nullable=False, default=100),
        sa.Column('max_durability', sa.Integer, nullable=False, default=100),
        sa.Column('usage_count', sa.Integer, nullable=False, default=0),
        sa.Column('quality_tier', sa.String(50), nullable=False),
        sa.Column('rarity_tier', sa.String(50), nullable=False),
        sa.Column('enchantment_seed', sa.Integer, nullable=True),
        sa.Column('is_equipped', sa.Boolean, nullable=False, default=False),
        sa.Column('equipment_set', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        
        # Add indexes for performance
        sa.Index('idx_equipment_character_id', 'character_id'),
        sa.Index('idx_equipment_template_id', 'template_id'),
        sa.Index('idx_equipment_slot', 'slot'),
        sa.Index('idx_equipment_set', 'equipment_set'),
        sa.Index('idx_equipment_equipped', 'is_equipped'),
        sa.Index('idx_equipment_character_equipped', 'character_id', 'is_equipped'),
        sa.Index('idx_equipment_quality_tier', 'quality_tier'),
        sa.Index('idx_equipment_rarity_tier', 'rarity_tier'),
    )
    
    # Create applied_enchantments table
    op.create_table(
        'applied_enchantments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enchantment_type', sa.String(100), nullable=False),
        sa.Column('magnitude', sa.Float, nullable=False),
        sa.Column('target_attribute', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('applied_at', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        
        # Foreign key to equipment instances
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment_instances.id'], ondelete='CASCADE'),
        
        # Indexes
        sa.Index('idx_enchantment_equipment_id', 'equipment_id'),
        sa.Index('idx_enchantment_type', 'enchantment_type'),
        sa.Index('idx_enchantment_active', 'is_active'),
    )
    
    # Create maintenance_records table
    op.create_table(
        'maintenance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_type', sa.String(50), nullable=False),  # 'repair', 'upgrade', 'damage', etc.
        sa.Column('durability_before', sa.Integer, nullable=False),
        sa.Column('durability_after', sa.Integer, nullable=False),
        sa.Column('cost', sa.Integer, nullable=True),  # Cost in gold
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('performed_by', sa.String(100), nullable=True),  # Character/NPC who performed action
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.text('NOW()')),
        
        # Foreign key to equipment instances
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment_instances.id'], ondelete='CASCADE'),
        
        # Indexes
        sa.Index('idx_maintenance_equipment_id', 'equipment_id'),
        sa.Index('idx_maintenance_type', 'record_type'),
        sa.Index('idx_maintenance_timestamp', 'timestamp'),
    )


def downgrade():
    """Drop equipment system tables"""
    op.drop_table('maintenance_records')
    op.drop_table('applied_enchantments')
    op.drop_table('equipment_instances') 