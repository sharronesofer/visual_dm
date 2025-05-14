"""
NPC utility functions.
"""

import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import db
from app.core.utils.error_utils import ValidationError, NotFoundError, DatabaseError
from app.models.npc import NPC
from app.core.services.ai import LLMService
from app.core.utils.config_utils import get_config
from app.core.utils.firebase_utils import get_firestore_client, get_firebase_db
from app.core.utils.gpt.client import GPTClient

def create_npc(data: dict) -> NPC:
    """Create a new NPC."""
    try:
        npc = NPC(
            name=data.get('name'),
            role=data.get('role'),
            description=data.get('description'),
            personality=data.get('personality'),
            background=data.get('background'),
            region_id=data.get('region_id'),
            faction_id=data.get('faction_id'),
            stats=data.get('stats', {}),
            inventory=data.get('inventory', []),
            quests=data.get('quests', []),
            dialogue=data.get('dialogue', {}),
            is_quest_giver=data.get('is_quest_giver', False),
            is_merchant=data.get('is_merchant', False),
            is_trainer=data.get('is_trainer', False)
        )
        db.session.add(npc)
        db.session.commit()
        return npc
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error creating NPC: {str(e)}")

def get_npc(npc_id: str) -> NPC:
    """Get an NPC by ID."""
    npc = NPC.query.get(npc_id)
    if not npc:
        raise NotFoundError(f"NPC with ID {npc_id} not found")
    return npc

def update_npc(npc_id: str, data: dict) -> NPC:
    """Update an NPC."""
    try:
        npc = get_npc(npc_id)
        for key, value in data.items():
            if hasattr(npc, key):
                setattr(npc, key, value)
        db.session.commit()
        return npc
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating NPC: {str(e)}")

def delete_npc(npc_id: str) -> None:
    """Delete an NPC."""
    try:
        npc = get_npc(npc_id)
        db.session.delete(npc)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting NPC: {str(e)}")

def get_npcs_by_location(location_id: str) -> List[NPC]:
    """Get all NPCs at a location."""
    try:
        return NPC.query.filter_by(region_id=location_id).all()
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error fetching NPCs: {str(e)}")

def update_relationship(npc_id: str, target_id: str, change: int) -> None:
    """Update an NPC's relationship with another entity."""
    try:
        npc = get_npc(npc_id)
        npc.add_relationship(target_id, 'updated', change)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error updating relationship: {str(e)}")

def add_rumor(npc_id: str, rumor_id: str, confidence: float) -> None:
    """Add or update a rumor for an NPC."""
    try:
        npc = get_npc(npc_id)
        if not npc.dialogue:
            npc.dialogue = {}
        if 'rumors' not in npc.dialogue:
            npc.dialogue['rumors'] = {}
        npc.dialogue['rumors'][rumor_id] = confidence
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding rumor: {str(e)}")

def should_abandon(npc_id: str) -> bool:
    """Check if an NPC should abandon their faction."""
    npc = get_npc(npc_id)
    if not npc.faction_id:
        return False
    # Add your faction abandonment logic here
    return False

def get_relationship_tier(npc_id: str, target_id: str) -> str:
    """Get the relationship tier between an NPC and another entity."""
    npc = get_npc(npc_id)
    relationship = npc.get_relationship(target_id)
    if not relationship:
        return 'neutral'
    strength = relationship.get('strength', 0)
    if strength >= 0.8:
        return 'best_friend'
    elif strength >= 0.5:
        return 'friend'
    elif strength >= 0.2:
        return 'acquaintance'
    elif strength >= -0.2:
        return 'neutral'
    elif strength >= -0.5:
        return 'dislike'
    elif strength >= -0.8:
        return 'enemy'
    else:
        return 'nemesis'

def sync_event_beliefs(npc_id: str, event_id: str, confidence: float) -> None:
    """Sync an NPC's beliefs about an event."""
    try:
        npc = get_npc(npc_id)
        if not npc.dialogue:
            npc.dialogue = {}
        if 'event_beliefs' not in npc.dialogue:
            npc.dialogue['event_beliefs'] = {}
        npc.dialogue['event_beliefs'][event_id] = confidence
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error syncing event beliefs: {str(e)}") 