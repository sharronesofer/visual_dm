"""Add diplomacy system schema

Revision ID: 001_diplomacy
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_diplomacy'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database with diplomacy system schema."""
    
    # Create diplomatic status enum
    diplomatic_status = postgresql.ENUM(
        'NEUTRAL', 'FRIENDLY', 'ALLIED', 'HOSTILE', 'AT_WAR',
        name='diplomatic_status'
    )
    diplomatic_status.create(op.get_bind())
    
    # Create treaty type enum
    treaty_type = postgresql.ENUM(
        'TRADE_AGREEMENT', 'MUTUAL_DEFENSE', 'NON_AGGRESSION',
        'ALLIANCE', 'PEACE_TREATY', 'CEASEFIRE', 'CUSTOMS_UNION',
        name='treaty_type'
    )
    treaty_type.create(op.get_bind())
    
    # Create treaty status enum
    treaty_status = postgresql.ENUM(
        'DRAFT', 'NEGOTIATING', 'PENDING_RATIFICATION', 'ACTIVE',
        'EXPIRED', 'TERMINATED', 'VIOLATED',
        name='treaty_status'
    )
    treaty_status.create(op.get_bind())
    
    # Create negotiation status enum
    negotiation_status = postgresql.ENUM(
        'INITIATED', 'IN_PROGRESS', 'STALLED', 'CONCLUDED',
        'FAILED', 'CANCELLED',
        name='negotiation_status'
    )
    negotiation_status.create(op.get_bind())
    
    # Create diplomatic event type enum
    diplomatic_event_type = postgresql.ENUM(
        'TREATY_SIGNED', 'TREATY_VIOLATED', 'ALLIANCE_FORMED',
        'ALLIANCE_BROKEN', 'WAR_DECLARED', 'PEACE_ESTABLISHED',
        'TRADE_EMBARGO', 'SANCTIONS_IMPOSED', 'AMBASSADOR_RECALLED',
        'DIPLOMATIC_INCIDENT', 'BORDER_DISPUTE', 'ULTIMATUM_ISSUED',
        name='diplomatic_event_type'
    )
    diplomatic_event_type.create(op.get_bind())
    
    # Create sanction type enum
    sanction_type = postgresql.ENUM(
        'TRADE_EMBARGO', 'ARMS_EMBARGO', 'FINANCIAL_SANCTIONS',
        'TRAVEL_BAN', 'ASSET_FREEZE', 'DIPLOMATIC_SANCTIONS',
        name='sanction_type'
    )
    sanction_type.create(op.get_bind())
    
    # Create sanction status enum
    sanction_status = postgresql.ENUM(
        'PROPOSED', 'ACTIVE', 'SUSPENDED', 'LIFTED', 'EXPIRED',
        name='sanction_status'
    )
    sanction_status.create(op.get_bind())
    
    # Create ultimatum status enum
    ultimatum_status = postgresql.ENUM(
        'ISSUED', 'ACKNOWLEDGED', 'ACCEPTED', 'REJECTED',
        'EXPIRED', 'WITHDRAWN',
        name='ultimatum_status'
    )
    ultimatum_status.create(op.get_bind())
    
    # Create incident type enum
    incident_type = postgresql.ENUM(
        'BORDER_VIOLATION', 'TRADE_DISPUTE', 'ESPIONAGE_DISCOVERY',
        'DIPLOMATIC_INSULT', 'TREATY_BREACH', 'RESOURCE_CONFLICT',
        'TERRITORIAL_CLAIM', 'CULTURAL_OFFENSE',
        name='incident_type'
    )
    incident_type.create(op.get_bind())
    
    # Create faction_relationships table
    op.create_table('faction_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('faction_a_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('faction_b_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', diplomatic_status, nullable=False, default='NEUTRAL'),
        sa.Column('tension_level', sa.Integer(), nullable=False, default=0),
        sa.Column('trust_level', sa.Integer(), nullable=False, default=0),
        sa.Column('trade_volume', sa.Float(), nullable=False, default=0.0),
        sa.Column('military_access', sa.Boolean(), nullable=False, default=False),
        sa.Column('embassy_established', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_interaction', sa.DateTime(timezone=True)),
        sa.Column('relationship_history', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('faction_a_id', 'faction_b_id', name='unique_faction_relationship'),
        sa.Index('idx_faction_relationships_status', 'status'),
        sa.Index('idx_faction_relationships_tension', 'tension_level')
    )
    
    # Create treaties table
    op.create_table('treaties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', treaty_type, nullable=False),
        sa.Column('status', treaty_status, nullable=False, default='DRAFT'),
        sa.Column('parties', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('terms', sa.JSON(), nullable=False),
        sa.Column('conditions', sa.JSON()),
        sa.Column('start_date', sa.DateTime(timezone=True)),
        sa.Column('end_date', sa.DateTime(timezone=True)),
        sa.Column('ratification_date', sa.DateTime(timezone=True)),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('auto_renewal', sa.Boolean(), nullable=False, default=False),
        sa.Column('violation_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_violation_date', sa.DateTime(timezone=True)),
        sa.Column('enforcement_actions', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('negotiation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_treaties_status', 'status'),
        sa.Index('idx_treaties_type', 'type'),
        sa.Index('idx_treaties_parties', 'parties', postgresql_using='gin')
    )
    
    # Create negotiations table
    op.create_table('negotiations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parties', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('initiator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('treaty_type', treaty_type, nullable=False),
        sa.Column('status', negotiation_status, nullable=False, default='INITIATED'),
        sa.Column('current_round', sa.Integer(), nullable=False, default=1),
        sa.Column('deadline', sa.DateTime(timezone=True)),
        sa.Column('mediator_id', postgresql.UUID(as_uuid=True)),
        sa.Column('location', sa.String(255)),
        sa.Column('public_visibility', sa.Boolean(), nullable=False, default=False),
        sa.Column('negotiation_rules', sa.JSON()),
        sa.Column('context', sa.JSON()),
        sa.Column('metadata', sa.JSON()),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_negotiations_status', 'status'),
        sa.Index('idx_negotiations_parties', 'parties', postgresql_using='gin'),
        sa.Index('idx_negotiations_initiator', 'initiator_id')
    )
    
    # Create negotiation_offers table
    op.create_table('negotiation_offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('negotiation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('terms', sa.JSON(), nullable=False),
        sa.Column('counter_offer_id', postgresql.UUID(as_uuid=True)),
        sa.Column('status', sa.String(50), nullable=False, default='PENDING'),
        sa.Column('justification', sa.Text()),
        sa.Column('private_notes', sa.JSON()),
        sa.Column('expiration_date', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['negotiation_id'], ['negotiations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['counter_offer_id'], ['negotiation_offers.id']),
        sa.Index('idx_negotiation_offers_negotiation', 'negotiation_id'),
        sa.Index('idx_negotiation_offers_faction', 'faction_id'),
        sa.Index('idx_negotiation_offers_round', 'round_number')
    )
    
    # Create diplomatic_events table
    op.create_table('diplomatic_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', diplomatic_event_type, nullable=False),
        sa.Column('primary_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('secondary_faction_id', postgresql.UUID(as_uuid=True)),
        sa.Column('affected_factions', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('consequences', sa.JSON()),
        sa.Column('context', sa.JSON()),
        sa.Column('severity', sa.String(50), nullable=False, default='MINOR'),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('location', sa.String(255)),
        sa.Column('related_treaty_id', postgresql.UUID(as_uuid=True)),
        sa.Column('related_negotiation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('metadata', sa.JSON()),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['related_treaty_id'], ['treaties.id']),
        sa.ForeignKeyConstraint(['related_negotiation_id'], ['negotiations.id']),
        sa.Index('idx_diplomatic_events_type', 'type'),
        sa.Index('idx_diplomatic_events_primary_faction', 'primary_faction_id'),
        sa.Index('idx_diplomatic_events_occurred_at', 'occurred_at'),
        sa.Index('idx_diplomatic_events_affected_factions', 'affected_factions', postgresql_using='gin')
    )
    
    # Create treaty_violations table
    op.create_table('treaty_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('treaty_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violator_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('affected_faction_id', postgresql.UUID(as_uuid=True)),
        sa.Column('violation_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False, default='MINOR'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON()),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolution_details', sa.Text()),
        sa.Column('penalties_imposed', sa.JSON()),
        sa.Column('diplomatic_impact', sa.JSON()),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reported_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['treaty_id'], ['treaties.id'], ondelete='CASCADE'),
        sa.Index('idx_treaty_violations_treaty', 'treaty_id'),
        sa.Index('idx_treaty_violations_violator', 'violator_faction_id'),
        sa.Index('idx_treaty_violations_severity', 'severity'),
        sa.Index('idx_treaty_violations_occurred_at', 'occurred_at')
    )
    
    # Create sanctions table
    op.create_table('sanctions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('imposer_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sanction_type, nullable=False),
        sa.Column('status', sanction_status, nullable=False, default='PROPOSED'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('conditions_for_lifting', sa.JSON()),
        sa.Column('economic_impact', sa.JSON()),
        sa.Column('supporting_factions', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('opposing_factions', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('violation_penalties', sa.JSON()),
        sa.Column('monitoring_requirements', sa.JSON()),
        sa.Column('start_date', sa.DateTime(timezone=True)),
        sa.Column('end_date', sa.DateTime(timezone=True)),
        sa.Column('review_date', sa.DateTime(timezone=True)),
        sa.Column('metadata', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_sanctions_imposer', 'imposer_faction_id'),
        sa.Index('idx_sanctions_target', 'target_faction_id'),
        sa.Index('idx_sanctions_type', 'type'),
        sa.Index('idx_sanctions_status', 'status')
    )
    
    # Create sanction_violations table
    op.create_table('sanction_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sanction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violator_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violation_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evidence', sa.JSON()),
        sa.Column('penalties_imposed', sa.JSON()),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sanction_id'], ['sanctions.id'], ondelete='CASCADE'),
        sa.Index('idx_sanction_violations_sanction', 'sanction_id'),
        sa.Index('idx_sanction_violations_violator', 'violator_faction_id'),
        sa.Index('idx_sanction_violations_occurred_at', 'occurred_at')
    )
    
    # Create ultimatums table
    op.create_table('ultimatums',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issuer_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', ultimatum_status, nullable=False, default='ISSUED'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('demands', sa.JSON(), nullable=False),
        sa.Column('consequences', sa.JSON(), nullable=False),
        sa.Column('justification', sa.Text()),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('response', sa.Text()),
        sa.Column('response_details', sa.JSON()),
        sa.Column('escalation_actions', sa.JSON()),
        sa.Column('supporting_evidence', sa.JSON()),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('responded_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_ultimatums_issuer', 'issuer_faction_id'),
        sa.Index('idx_ultimatums_recipient', 'recipient_faction_id'),
        sa.Index('idx_ultimatums_status', 'status'),
        sa.Index('idx_ultimatums_deadline', 'deadline')
    )
    
    # Create diplomatic_incidents table
    op.create_table('diplomatic_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', incident_type, nullable=False),
        sa.Column('perpetrator_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('victim_faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False, default='MINOR'),
        sa.Column('location', sa.String(255)),
        sa.Column('evidence', sa.JSON()),
        sa.Column('witnesses', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('diplomatic_impact', sa.JSON()),
        sa.Column('demands_for_resolution', sa.JSON()),
        sa.Column('offered_compensation', sa.JSON()),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('resolution_details', sa.Text()),
        sa.Column('escalation_potential', sa.String(50), nullable=False, default='LOW'),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reported_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_diplomatic_incidents_type', 'type'),
        sa.Index('idx_diplomatic_incidents_perpetrator', 'perpetrator_faction_id'),
        sa.Index('idx_diplomatic_incidents_victim', 'victim_faction_id'),
        sa.Index('idx_diplomatic_incidents_severity', 'severity'),
        sa.Index('idx_diplomatic_incidents_occurred_at', 'occurred_at')
    )
    
    # Create tension_history table for tracking tension changes
    op.create_table('tension_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('previous_tension', sa.Integer(), nullable=False),
        sa.Column('new_tension', sa.Integer(), nullable=False),
        sa.Column('change_amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('triggering_event_id', postgresql.UUID(as_uuid=True)),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['relationship_id'], ['faction_relationships.id'], ondelete='CASCADE'),
        sa.Index('idx_tension_history_relationship', 'relationship_id'),
        sa.Index('idx_tension_history_changed_at', 'changed_at')
    )


def downgrade() -> None:
    """Downgrade database by removing diplomacy system schema."""
    
    # Drop tables in reverse order
    op.drop_table('tension_history')
    op.drop_table('diplomatic_incidents')
    op.drop_table('ultimatums')
    op.drop_table('sanction_violations')
    op.drop_table('sanctions')
    op.drop_table('treaty_violations')
    op.drop_table('diplomatic_events')
    op.drop_table('negotiation_offers')
    op.drop_table('negotiations')
    op.drop_table('treaties')
    op.drop_table('faction_relationships')
    
    # Drop enums
    postgresql.ENUM(name='incident_type').drop(op.get_bind())
    postgresql.ENUM(name='ultimatum_status').drop(op.get_bind())
    postgresql.ENUM(name='sanction_status').drop(op.get_bind())
    postgresql.ENUM(name='sanction_type').drop(op.get_bind())
    postgresql.ENUM(name='diplomatic_event_type').drop(op.get_bind())
    postgresql.ENUM(name='negotiation_status').drop(op.get_bind())
    postgresql.ENUM(name='treaty_status').drop(op.get_bind())
    postgresql.ENUM(name='treaty_type').drop(op.get_bind())
    postgresql.ENUM(name='diplomatic_status').drop(op.get_bind()) 