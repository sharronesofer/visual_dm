from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Region:
    id: str
    name: str
    description: str
    climate: str
    terrain: str
    population: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Faction:
    id: str
    name: str
    description: str
    alignment: str
    goals: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Quest:
    id: str
    title: str
    description: str
    difficulty: str
    rewards: Dict[str, int]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class World:
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        self.factions: Dict[str, Faction] = {}
        self.quests: Dict[str, Quest] = {}
        
    def add_region(self, region_data: Dict) -> Region:
        region = Region(**region_data)
        self.regions[region.id] = region
        return region
        
    def get_region(self, region_id: str) -> Optional[Region]:
        return self.regions.get(region_id)
        
    def add_faction(self, faction_data: Dict) -> Faction:
        faction = Faction(**faction_data)
        self.factions[faction.id] = faction
        return faction
        
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        return self.factions.get(faction_id)
        
    def add_quest(self, quest_data: Dict) -> Quest:
        quest = Quest(**quest_data)
        self.quests[quest.id] = quest
        return quest
        
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        return self.quests.get(quest_id)
        
    def get_world_data(self) -> Dict:
        return {
            'regions': [vars(region) for region in self.regions.values()],
            'factions': [vars(faction) for faction in self.factions.values()],
            'quests': [vars(quest) for quest in self.quests.values()]
        } 