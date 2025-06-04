"""
Database schema definitions for the motif system.

SQLAlchemy table definitions with optimized indices for performance.
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, Boolean, 
    Index, CheckConstraint, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from enum import Enum

from backend.infrastructure.systems.motif.models import (
    MotifCategory, MotifScope, MotifLifecycle, MotifEvolutionTrigger
)

Base = declarative_base()


class MotifTable(Base):
    """
    Main motif table with optimized structure for performance.
    """
    __tablename__ = "motifs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(MotifCategory), nullable=False, index=True)
    scope = Column(SQLEnum(MotifScope), nullable=False, index=True)
    lifecycle = Column(SQLEnum(MotifLifecycle), nullable=False, index=True, default=MotifLifecycle.EMERGING)
    
    # Intensity and strength
    intensity = Column(Integer, nullable=False, default=5, index=True)
    
    # Thematic content
    theme = Column(String(255), nullable=True, index=True)
    tone = Column(String(255), nullable=True)
    narrative_direction = Column(String(255), nullable=True)
    descriptors = Column(ARRAY(String), nullable=True)
    
    # Spatial data (nullable for global motifs)
    x = Column(Float, nullable=True, index=True)
    y = Column(Float, nullable=True, index=True)
    radius = Column(Float, nullable=True)
    region_id = Column(String(255), nullable=True, index=True)
    
    # Player character association
    player_id = Column(String(255), nullable=True, index=True)
    character_id = Column(String(255), nullable=True, index=True)
    
    # Lifecycle and timing
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_days = Column(Float, nullable=True)
    
    # System metadata
    is_canonical = Column(Boolean, default=False, index=True)
    source = Column(String(255), nullable=True)  # How motif was created
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Constraints
    __table_args__ = (
        # Intensity bounds
        CheckConstraint('intensity >= 1 AND intensity <= 10', name='valid_intensity'),
        
        # Spatial consistency
        CheckConstraint(
            '(scope = \'GLOBAL\' AND x IS NULL AND y IS NULL) OR '
            '(scope != \'GLOBAL\' AND (x IS NOT NULL OR y IS NOT NULL))',
            name='spatial_scope_consistency'
        ),
        
        # Player character scope validation
        CheckConstraint(
            '(scope = \'PLAYER_CHARACTER\' AND player_id IS NOT NULL) OR '
            '(scope != \'PLAYER_CHARACTER\')',
            name='player_scope_consistency'
        ),
        
        # Canonical motifs must be global
        CheckConstraint(
            '(is_canonical = true AND scope = \'GLOBAL\') OR '
            '(is_canonical = false)',
            name='canonical_global_consistency'
        ),
        
        # Performance indices
        Index('idx_motif_category_lifecycle', 'category', 'lifecycle'),
        Index('idx_motif_scope_intensity', 'scope', 'intensity'),
        Index('idx_motif_spatial', 'x', 'y'),
        Index('idx_motif_regional', 'region_id', 'scope'),
        Index('idx_motif_player', 'player_id', 'character_id'),
        Index('idx_motif_temporal', 'created_at', 'lifecycle'),
        Index('idx_motif_canonical', 'is_canonical', 'category'),
        Index('idx_motif_theme', 'theme', 'category'),
        
        # Composite indices for common queries
        Index('idx_motif_active_regional', 'scope', 'lifecycle', 'region_id'),
        Index('idx_motif_active_spatial', 'scope', 'lifecycle', 'x', 'y'),
        Index('idx_motif_player_active', 'player_id', 'lifecycle', 'scope'),
    )


class MotifEvolutionTable(Base):
    """
    Track motif evolution history and triggers.
    """
    __tablename__ = "motif_evolutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    motif_id = Column(UUID(as_uuid=True), ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Evolution details
    trigger_type = Column(SQLEnum(MotifEvolutionTrigger), nullable=False, index=True)
    trigger_description = Column(Text, nullable=True)
    
    # Before/after state
    old_intensity = Column(Integer, nullable=True)
    new_intensity = Column(Integer, nullable=True)
    old_lifecycle = Column(SQLEnum(MotifLifecycle), nullable=True)
    new_lifecycle = Column(SQLEnum(MotifLifecycle), nullable=True)
    
    # Additional changes
    changes_json = Column(Text, nullable=True)  # JSON string of other changes
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_by = Column(String(255), nullable=True)  # System, player, admin, etc.
    
    __table_args__ = (
        Index('idx_evolution_motif_time', 'motif_id', 'created_at'),
        Index('idx_evolution_trigger', 'trigger_type', 'created_at'),
    )


class MotifConflictTable(Base):
    """
    Track detected conflicts between motifs.
    """
    __tablename__ = "motif_conflicts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    motif_a_id = Column(UUID(as_uuid=True), ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True)
    motif_b_id = Column(UUID(as_uuid=True), ForeignKey('motifs.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Conflict details
    conflict_type = Column(String(100), nullable=False, index=True)  # 'opposing_themes', 'intensity_clash', etc.
    severity = Column(String(50), nullable=False, index=True)  # 'low', 'medium', 'high'
    
    # Status
    status = Column(String(50), nullable=False, default='active', index=True)  # 'active', 'resolved', 'ignored'
    resolution_method = Column(String(100), nullable=True)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    __table_args__ = (
        # Prevent duplicate conflicts
        Index('idx_conflict_unique', 'motif_a_id', 'motif_b_id', unique=True),
        Index('idx_conflict_status', 'status', 'detected_at'),
        Index('idx_conflict_severity', 'severity', 'status'),
    )


class MotifStatisticsTable(Base):
    """
    Aggregate statistics for system monitoring.
    """
    __tablename__ = "motif_statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time period
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    period_type = Column(String(50), nullable=False, index=True)  # 'hourly', 'daily', 'weekly'
    
    # Counts
    total_motifs = Column(Integer, nullable=False, default=0)
    active_motifs = Column(Integer, nullable=False, default=0)
    canonical_motifs = Column(Integer, nullable=False, default=0)
    
    # By scope
    global_motifs = Column(Integer, nullable=False, default=0)
    regional_motifs = Column(Integer, nullable=False, default=0)
    local_motifs = Column(Integer, nullable=False, default=0)
    player_motifs = Column(Integer, nullable=False, default=0)
    
    # By lifecycle
    emerging_motifs = Column(Integer, nullable=False, default=0)
    stable_motifs = Column(Integer, nullable=False, default=0)
    waning_motifs = Column(Integer, nullable=False, default=0)
    dormant_motifs = Column(Integer, nullable=False, default=0)
    concluded_motifs = Column(Integer, nullable=False, default=0)
    
    # System health
    active_conflicts = Column(Integer, nullable=False, default=0)
    average_intensity = Column(Float, nullable=True)
    
    # Performance metrics
    evolution_count_24h = Column(Integer, nullable=False, default=0)
    creation_count_24h = Column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        Index('idx_stats_period', 'period_type', 'recorded_at'),
    )


# Create all tables
def create_tables(engine):
    """Create all motif system tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all motif system tables (for testing)."""
    Base.metadata.drop_all(bind=engine) 