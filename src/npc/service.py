from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import NPC, NPCTrait, NPCRelationship, NPCSchedule, NPCScheduleEvent
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import time, datetime as dt

TRAIT_TYPES = [
    'bravery', 'intelligence', 'kindness', 'aggression', 'curiosity', 'loyalty'
]

DEFAULT_ROUTINE = [
    {'start': time(6, 0), 'end': time(8, 0), 'activity': 'breakfast', 'location': 'home', 'event_type': 'routine'},
    {'start': time(8, 0), 'end': time(17, 0), 'activity': 'work', 'location': 'workplace', 'event_type': 'routine'},
    {'start': time(17, 0), 'end': time(19, 0), 'activity': 'dinner', 'location': 'home', 'event_type': 'routine'},
    {'start': time(19, 0), 'end': time(22, 0), 'activity': 'leisure', 'location': 'town', 'event_type': 'routine'},
    {'start': time(22, 0), 'end': time(6, 0), 'activity': 'sleep', 'location': 'home', 'event_type': 'routine'},
]

class NPCService:
    """
    Service class for managing NPCs, their traits, and relationships.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_npc(self, data: Dict[str, Any], traits: Optional[List[Dict[str, Any]]] = None) -> NPC:
        """
        Create a new NPC with optional traits.
        """
        npc = NPC(name=data['name'], is_active=data.get('is_active', True))
        self.db_session.add(npc)
        self.db_session.flush()  # Assigns ID
        if traits:
            for trait in traits:
                npc_trait = NPCTrait(npc_id=npc.id, trait_type=trait['trait_type'], value=trait['value'])
                self.db_session.add(npc_trait)
        self.db_session.commit()
        return npc

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        return self.db_session.query(NPC).filter_by(id=npc_id).first()

    def update_npc(self, npc_id: str, data: Dict[str, Any]) -> Optional[NPC]:
        npc = self.get_npc(npc_id)
        if not npc:
            return None
        for key, value in data.items():
            if hasattr(npc, key):
                setattr(npc, key, value)
        self.db_session.commit()
        return npc

    def delete_npc(self, npc_id: str) -> bool:
        npc = self.get_npc(npc_id)
        if not npc:
            return False
        self.db_session.delete(npc)
        self.db_session.commit()
        return True

    def list_npcs(self) -> List[NPC]:
        return self.db_session.query(NPC).all()

    def update_relationships(self, npc_id: str, target_id: str, change: Dict[str, Any]) -> Optional[NPCRelationship]:
        rel = self.db_session.query(NPCRelationship).filter_by(npc_id=npc_id, target_id=target_id).first()
        if not rel:
            rel = NPCRelationship(npc_id=npc_id, target_id=target_id, relationship_type=change['relationship_type'], value=change['value'])
            self.db_session.add(rel)
        else:
            rel.relationship_type = change.get('relationship_type', rel.relationship_type)
            rel.value = change.get('value', rel.value)
        self.db_session.commit()
        return rel

    def generate_traits(self, predefined: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Generate a list of traits for an NPC, either randomly or from a predefined list.
        """
        if predefined:
            return predefined
        traits = []
        for trait_type in TRAIT_TYPES:
            value = round(random.uniform(0.0, 1.0), 2)
            traits.append({'trait_type': trait_type, 'value': value})
        return traits

    def evolve_traits(self, npc_id: str, experience: Dict[str, Any]) -> List[NPCTrait]:
        """
        Evolve NPC's traits based on an experience dict (e.g., {'bravery': +0.1}).
        """
        traits = self.db_session.query(NPCTrait).filter_by(npc_id=npc_id).all()
        for trait in traits:
            if trait.trait_type in experience:
                trait.value = min(max(trait.value + experience[trait.trait_type], 0.0), 1.0)
        self.db_session.commit()
        return traits

    def get_relationship(self, npc_id: str, target_id: str) -> Optional[NPCRelationship]:
        """
        Retrieve the relationship between two NPCs (or NPC and player).
        """
        return self.db_session.query(NPCRelationship).filter_by(npc_id=npc_id, target_id=target_id).first()

    def evolve_relationship(self, npc_id: str, target_id: str, interaction_type: str, delta: float) -> NPCRelationship:
        """
        Evolve the relationship value based on interaction type and delta.
        """
        rel = self.get_relationship(npc_id, target_id)
        if not rel:
            rel = NPCRelationship(npc_id=npc_id, target_id=target_id, relationship_type=interaction_type, value=delta)
            self.db_session.add(rel)
        else:
            rel.value = min(max(rel.value + delta, 0.0), 1.0)
            rel.relationship_type = interaction_type
        self.db_session.commit()
        return rel

    def list_relationships(self, npc_id: str) -> List[NPCRelationship]:
        """
        List all relationships for a given NPC.
        """
        return self.db_session.query(NPCRelationship).filter_by(npc_id=npc_id).all()

    def query_traits(self, npc_id: str) -> List[NPCTrait]:
        """
        Retrieve all traits for a given NPC.
        """
        return self.db_session.query(NPCTrait).filter_by(npc_id=npc_id).all()

    def generate_daily_schedule(self, npc_id: str, day_of_week: int, routine: Optional[List[Dict[str, Any]]] = None) -> NPCSchedule:
        """
        Generate a daily schedule for an NPC. Routine can be customized or use default.
        """
        routine = routine or DEFAULT_ROUTINE
        schedule = NPCSchedule(npc_id=npc_id, day_of_week=day_of_week)
        self.db_session.add(schedule)
        self.db_session.flush()
        for event in routine:
            event_obj = NPCScheduleEvent(
                schedule_id=schedule.id,
                start_time=event['start'],
                end_time=event['end'],
                activity=event['activity'],
                location=event['location'],
                event_type=event.get('event_type', 'routine')
            )
            self.db_session.add(event_obj)
        self.db_session.commit()
        return schedule

    def add_schedule_event(self, schedule_id: int, event: Dict[str, Any]) -> NPCScheduleEvent:
        """
        Add an event to an existing schedule.
        """
        event_obj = NPCScheduleEvent(
            schedule_id=schedule_id,
            start_time=event['start'],
            end_time=event['end'],
            activity=event['activity'],
            location=event['location'],
            event_type=event.get('event_type', 'special')
        )
        self.db_session.add(event_obj)
        self.db_session.commit()
        return event_obj

    def get_schedule_for_day(self, npc_id: str, day_of_week: int) -> Optional[NPCSchedule]:
        """
        Retrieve the schedule for a given NPC and day.
        """
        return self.db_session.query(NPCSchedule).filter_by(npc_id=npc_id, day_of_week=day_of_week).first()

    def get_npc_state_at_time(self, npc_id: str, day_of_week: int, query_time: time) -> Optional[Dict[str, Any]]:
        """
        Determine the NPC's activity and location at a specific time.
        """
        schedule = self.get_schedule_for_day(npc_id, day_of_week)
        if not schedule:
            return None
        for event in schedule.events:
            if event.start_time <= query_time < event.end_time or (
                event.start_time > event.end_time and (query_time >= event.start_time or query_time < event.end_time)
            ):
                return {
                    'activity': event.activity,
                    'location': event.location,
                    'event_type': event.event_type
                }
        return None

    def add_special_event(self, npc_id: str, day_of_week: int, event: Dict[str, Any]) -> NPCScheduleEvent:
        """
        Add a special event to an NPC's schedule for a given day.
        """
        schedule = self.get_schedule_for_day(npc_id, day_of_week)
        if not schedule:
            schedule = self.generate_daily_schedule(npc_id, day_of_week)
        return self.add_schedule_event(schedule.id, event)
