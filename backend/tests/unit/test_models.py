import pytest
from backend.models.world import World
from backend.models.npc import NPC
from backend.models.quest import Quest

def test_world_creation():
    world = World(name="TestWorld", time=0)
    assert world.name == "TestWorld"
    assert world.time == 0

def test_npc_creation():
    npc = NPC(name="Alice", traits={"friendliness": 0.8})
    assert npc.name == "Alice"
    assert "friendliness" in npc.traits

def test_quest_serialization():
    quest = Quest(id="q1", title="Test Quest", description="Desc")
    data = quest.serialize()
    assert data["id"] == "q1"
    assert data["title"] == "Test Quest" 