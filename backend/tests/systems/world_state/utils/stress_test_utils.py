from typing import List
"""
Stress Test Utilities
Simulates large numbers of world events and memory entries for load testing.
See docs/stubs_needs_consolidation_qna.md for requirements.
"""

from datetime import datetime, timedelta
from firebase_admin import db
import random
from backend.world.utils.world_event_utils import log_world_event


def simulate_world_events(
    event_count=1000, event_types=None, regions=None, factions=None
):
    """
    Simulate a large number of world events for stress testing.
    Args:
        event_count: Number of events to generate
        event_types: List of event types to use
        regions: List of region IDs to affect
        factions: List of faction IDs to affect
    Returns:
        List of event_ids created
    """
    event_types = event_types or [
        "arc_failure",
        "war_outbreak",
        "tension_spike",
        "metropolis_assigned",
    ]
    regions = regions or [f"region_{i}" for i in range(5)]
    factions = factions or [f"faction_{i}" for i in range(5)]
    event_ids = []
    for i in range(event_count):
        event_type = random.choice(event_types)
        region_id = random.choice(regions)
        faction_id = random.choice(factions)
        event_data = {
            "type": event_type,
            "region_id": region_id,
            "faction_id": faction_id,
            "severity": random.randint(1, 5),
            "players_present": [],
            "npcs_present": [],
            "affected_systems": ["test"],
            "details": f"Simulated event {i} of type {event_type} in {region_id} for {faction_id}.",
            "timestamp": (datetime.utcnow() - timedelta(seconds=i)).isoformat(),
        }
        result = log_world_event(event_data)
        event_ids.append(result["event_id"])
    return event_ids


def simulate_memory_entries(entity_type="region", entity_ids=None, entry_count=1000):
    """
    Simulate a large number of memory entries for regions or factions.
    Args:
        entity_type: "region" or "faction"
        entity_ids: List of entity IDs to affect
        entry_count: Number of entries per entity
    Returns:
        None
    """
    entity_ids = entity_ids or [f"{entity_type}_{i}" for i in range(5)]
    for eid in entity_ids:
        mem_ref = db.reference(f"/{entity_type}s/{eid}/memory")
        memory = mem_ref.get() or []
        for i in range(entry_count):
            memory.append(
                {
                    "timestamp": (datetime.utcnow() - timedelta(seconds=i)).isoformat(),
                    "event_type": "test_event",
                    "details": f"Simulated memory entry {i} for {eid}",
                    "core": bool(i % 10 == 0),
                }
            )
        mem_ref.set(memory)
