"""Initial motif system schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create motif categories enum
    motif_category_enum = sa.Enum(
        'BETRAYAL', 'CHAOS', 'DEATH', 'DESTRUCTION', 'DESPAIR', 'DOOM', 'EVIL', 'EXILE', 'FALL', 'FEAR',
        'GUILT', 'HATE', 'HUBRIS', 'ISOLATION', 'LOSS', 'MADNESS', 'NEMESIS', 'PRIDE', 'REVENGE', 'SACRIFICE',
        'TEMPTATION', 'TRAGEDY', 'TREACHERY', 'VENGEANCE', 'WRATH', 'HOPE', 'LOVE', 'REDEMPTION', 'COURAGE',
        'WISDOM', 'JUSTICE', 'MERCY', 'FORGIVENESS', 'FRIENDSHIP', 'LOYALTY', 'HONOR', 'DUTY', 'FAITH',
        'COMPASSION', 'HEALING', 'RENEWAL', 'DISCOVERY', 'ADVENTURE', 'MYSTERY', 'WONDER', 'TRANSFORMATION',
        'FREEDOM', 'TRIUMPH', 'PROSPERITY',
        name='motifcategory'
    )
    
    # Create motif scope enum
    motif_scope_enum = sa.Enum(
        'GLOBAL', 'REGIONAL', 'LOCAL', 'PLAYER_CHARACTER',
        name='motifscope'
    )
    
    # Create motif lifecycle enum
    motif_lifecycle_enum = sa.Enum(
        'EMERGING', 'STABLE', 'WANING', 'DORMANT', 'CONCLUDED',
        name='motiflifecycle'
    )
    
    # Create motif evolution trigger enum
    motif_evolution_trigger_enum = sa.Enum(
        'TIME_PROGRESSION', 'PLAYER_ACTION', 'WORLD_EVENT', 'SYSTEM_TRIGGER', 'ADMIN_OVERRIDE',
        name='motifevolutiontrigger'
    )
    
    # Create motifs table
    op.create_table('motifs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', motif_category_enum, nullable=False, index=True),
        sa.Column('scope', motif_scope_enum, nullable=False, index=True),
        sa.Column('lifecycle', motif_lifecycle_enum, nullable=False, index=True, default='EMERGING'),
        sa.Column('intensity', sa.Integer(), nullable=False, default=5, index=True),
        sa.Column('theme', sa.String(255), nullable=True, index=True),
        sa.Column('tone', sa.String(255), nullable=True),
        sa.Column('narrative_direction', sa.String(255), nullable=True),
        sa.Column('descriptors', ARRAY(sa.String), nullable=True),
        sa.Column('x', sa.Float(), nullable=True, index=True),
        sa.Column('y', sa.Float(), nullable=True, index=True),
        sa.Column('radius', sa.Float(), nullable=True),
        sa.Column('region_id', sa.String(255), nullable=True, index=True),
        sa.Column('player_id', sa.String(255), nullable=True, index=True),
        sa.Column('character_id', sa.String(255), nullable=True, index=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_days', sa.Float(), nullable=True),
        sa.Column('is_canonical', sa.Boolean(), default=False, index=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('version', sa.Integer(), default=1, nullable=False),
        
        # Constraints
        sa.CheckConstraint('intensity >= 1 AND intensity <= 10', name='valid_intensity'),
        sa.CheckConstraint(
            "(scope = 'GLOBAL' AND x IS NULL AND y IS NULL) OR "
            "(scope != 'GLOBAL' AND (x IS NOT NULL OR y IS NOT NULL))",
            name='spatial_scope_consistency'
        ),
        sa.CheckConstraint(
            "(scope = 'PLAYER_CHARACTER' AND player_id IS NOT NULL) OR "
            "(scope != 'PLAYER_CHARACTER')",
            name='player_scope_consistency'
        ),
        sa.CheckConstraint(
            "(is_canonical = true AND scope = 'GLOBAL') OR "
            "(is_canonical = false)",
            name='canonical_global_consistency'
        ),
    )
    
    # Create performance indices
    op.create_index('idx_motif_category_lifecycle', 'motifs', ['category', 'lifecycle'])
    op.create_index('idx_motif_scope_intensity', 'motifs', ['scope', 'intensity'])
    op.create_index('idx_motif_spatial', 'motifs', ['x', 'y'])
    op.create_index('idx_motif_regional', 'motifs', ['region_id', 'scope'])
    op.create_index('idx_motif_player', 'motifs', ['player_id', 'character_id'])
    op.create_index('idx_motif_temporal', 'motifs', ['created_at', 'lifecycle'])
    op.create_index('idx_motif_canonical', 'motifs', ['is_canonical', 'category'])
    op.create_index('idx_motif_theme', 'motifs', ['theme', 'category'])
    op.create_index('idx_motif_active_regional', 'motifs', ['scope', 'lifecycle', 'region_id'])
    op.create_index('idx_motif_active_spatial', 'motifs', ['scope', 'lifecycle', 'x', 'y'])
    op.create_index('idx_motif_player_active', 'motifs', ['player_id', 'lifecycle', 'scope'])

    # Create motif_evolutions table
    op.create_table('motif_evolutions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('motif_id', UUID(as_uuid=True), sa.ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('trigger_type', motif_evolution_trigger_enum, nullable=False, index=True),
        sa.Column('trigger_description', sa.Text(), nullable=True),
        sa.Column('old_intensity', sa.Integer(), nullable=True),
        sa.Column('new_intensity', sa.Integer(), nullable=True),
        sa.Column('old_lifecycle', motif_lifecycle_enum, nullable=True),
        sa.Column('new_lifecycle', motif_lifecycle_enum, nullable=True),
        sa.Column('changes_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('created_by', sa.String(255), nullable=True),
    )
    
    op.create_index('idx_evolution_motif_time', 'motif_evolutions', ['motif_id', 'created_at'])
    op.create_index('idx_evolution_trigger', 'motif_evolutions', ['trigger_type', 'created_at'])

    # Create motif_conflicts table
    op.create_table('motif_conflicts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('motif_a_id', UUID(as_uuid=True), sa.ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('motif_b_id', UUID(as_uuid=True), sa.ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('conflict_type', sa.String(100), nullable=False, index=True),
        sa.Column('severity', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, default='active', index=True),
        sa.Column('resolution_method', sa.String(100), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True, index=True),
    )
    
    op.create_index('idx_conflict_unique', 'motif_conflicts', ['motif_a_id', 'motif_b_id'], unique=True)
    op.create_index('idx_conflict_status', 'motif_conflicts', ['status', 'detected_at'])
    op.create_index('idx_conflict_severity', 'motif_conflicts', ['severity', 'status'])

    # Create motif_statistics table
    op.create_table('motif_statistics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('period_type', sa.String(50), nullable=False, index=True),
        sa.Column('total_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('active_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('canonical_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('global_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('regional_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('local_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('player_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('emerging_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('stable_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('waning_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('dormant_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('concluded_motifs', sa.Integer(), nullable=False, default=0),
        sa.Column('active_conflicts', sa.Integer(), nullable=False, default=0),
        sa.Column('average_intensity', sa.Float(), nullable=True),
        sa.Column('evolution_count_24h', sa.Integer(), nullable=False, default=0),
        sa.Column('creation_count_24h', sa.Integer(), nullable=False, default=0),
    )
    
    op.create_index('idx_stats_period', 'motif_statistics', ['period_type', 'recorded_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('motif_statistics')
    op.drop_table('motif_conflicts')
    op.drop_table('motif_evolutions')
    op.drop_table('motifs')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS motifevolutiontrigger')
    op.execute('DROP TYPE IF EXISTS motiflifecycle')
    op.execute('DROP TYPE IF EXISTS motifscope')
    op.execute('DROP TYPE IF EXISTS motifcategory') 