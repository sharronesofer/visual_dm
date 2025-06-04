"""
Equipment Tables Database Migration

Creates all necessary tables for the equipment system.
Run this migration to set up equipment database schema.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade():
    """Create equipment system tables"""
    
    # Quality Tiers table
    op.create_table(
        'quality_tiers',
        sa.Column('tier_name', sa.String(20), primary_key=True),
        sa.Column('display_name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('durability_weeks', sa.Integer, nullable=False, default=1),
        sa.Column('degradation_rate', sa.Float, default=1.0),
        sa.Column('value_multiplier', sa.Float, default=1.0),
        sa.Column('enchantment_capacity', sa.Integer, default=5),
        sa.Column('max_enchantment_power', sa.Integer, default=75),
        sa.Column('color_code', sa.String(10)),
        sa.Column('rarity_weight', sa.Float, default=1.0),
        sa.Column('id', UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Equipment Templates table
    op.create_table(
        'equipment_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', sa.String(100), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('item_type', sa.String(50), nullable=False),
        sa.Column('quality_tier', sa.String(20), nullable=False, default='basic'),
        sa.Column('rarity', sa.String(20), default='common'),
        sa.Column('base_value', sa.Integer, nullable=False, default=100),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('durability_multiplier', sa.Float, default=1.0),
        sa.Column('base_stats', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('equipment_slots', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('abilities', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('compatible_enchantments', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('thematic_tags', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('restrictions', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('material', sa.String(100)),
        sa.Column('visual_description', sa.Text),
        sa.Column('lore_text', sa.Text),
        sa.Column('crafting_requirements', JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Create indexes for equipment templates
    op.create_index('ix_equipment_templates_template_id', 'equipment_templates', ['template_id'])
    op.create_index('ix_equipment_templates_item_type', 'equipment_templates', ['item_type'])
    
    # Magical Effects table
    op.create_table(
        'magical_effects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('effect_id', sa.String(100), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('effect_type', sa.String(50), nullable=False),
        sa.Column('school', sa.String(50)),
        sa.Column('rarity', sa.String(20), default='common'),
        sa.Column('base_power', sa.Integer, default=50),
        sa.Column('scaling_type', sa.String(20), default='linear'),
        sa.Column('parameters', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('min_quality_tier', sa.String(20), default='basic'),
        sa.Column('compatible_item_types', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Equipment Instances table
    op.create_table(
        'equipment_instances',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', sa.String(100), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('quality_tier', sa.String(20), nullable=False, default='basic'),
        sa.Column('custom_name', sa.String(200)),
        sa.Column('durability', sa.Float, nullable=False, default=100.0),
        sa.Column('max_durability', sa.Float, nullable=False, default=100.0),
        sa.Column('is_equipped', sa.Boolean, default=False),
        sa.Column('equipped_slot', sa.String(50)),
        sa.Column('creation_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_used', sa.DateTime(timezone=True)),
        sa.Column('total_usage_hours', sa.Float, default=0.0),
        sa.Column('stat_modifiers', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Add foreign key constraint to equipment templates
    op.create_foreign_key(
        'fk_equipment_instances_template',
        'equipment_instances', 
        'equipment_templates',
        ['template_id'], 
        ['template_id']
    )
    
    # Create indexes for equipment instances
    op.create_index('ix_equipment_instances_owner_id', 'equipment_instances', ['owner_id'])
    op.create_index('ix_equipment_instances_owner_equipped', 'equipment_instances', ['owner_id', 'is_equipped'])
    op.create_index('ix_equipment_instances_template_quality', 'equipment_instances', ['template_id', 'quality_tier'])
    
    # Character Equipment Slots table
    op.create_table(
        'character_equipment_slots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('character_id', UUID(as_uuid=True), nullable=False),
        sa.Column('slot_name', sa.String(50), nullable=False),
        sa.Column('equipment_id', UUID(as_uuid=True)),
        sa.Column('equipped_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Add foreign key constraint to equipment instances
    op.create_foreign_key(
        'fk_character_equipment_slots_equipment',
        'character_equipment_slots',
        'equipment_instances',
        ['equipment_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create unique constraint and index for character equipment slots
    op.create_index(
        'ix_character_equipment_slots_character_slot',
        'character_equipment_slots',
        ['character_id', 'slot_name'],
        unique=True
    )
    op.create_index('ix_character_equipment_slots_character_id', 'character_equipment_slots', ['character_id'])
    
    # Equipment Magical Effects association table
    op.create_table(
        'equipment_magical_effects',
        sa.Column('equipment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('effect_id', UUID(as_uuid=True), nullable=False),
        sa.Column('power_level', sa.Integer, default=50),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_equipment_magical_effects_equipment',
        'equipment_magical_effects',
        'equipment_instances',
        ['equipment_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_equipment_magical_effects_effect',
        'equipment_magical_effects',
        'magical_effects',
        ['effect_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create primary key for association table
    op.create_primary_key('pk_equipment_magical_effects', 'equipment_magical_effects', ['equipment_id', 'effect_id'])
    
    # Equipment Maintenance Records table
    op.create_table(
        'equipment_maintenance_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('equipment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_description', sa.Text),
        sa.Column('durability_before', sa.Float, nullable=False),
        sa.Column('durability_after', sa.Float, nullable=False),
        sa.Column('durability_change', sa.Float, nullable=False),
        sa.Column('cause', sa.String(100)),
        sa.Column('location', sa.String(200)),
        sa.Column('event_data', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('cost_paid', sa.Integer, default=0),
        sa.Column('materials_used', JSONB, default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_equipment_maintenance_records_equipment',
        'equipment_maintenance_records',
        'equipment_instances',
        ['equipment_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create index for maintenance records
    op.create_index('ix_equipment_maintenance_created', 'equipment_maintenance_records', ['equipment_id', 'created_at'])


def downgrade():
    """Drop equipment system tables"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('equipment_maintenance_records')
    op.drop_table('equipment_magical_effects')
    op.drop_table('character_equipment_slots')
    op.drop_table('equipment_instances')
    op.drop_table('magical_effects')
    op.drop_table('equipment_templates')
    op.drop_table('quality_tiers') 