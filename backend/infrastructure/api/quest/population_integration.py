"""
Quest System - Population Integration (Infrastructure Layer)

Integrates population system events with quest generation, creating dynamic quests
based on disease outbreaks, population changes, and other population events.

This is infrastructure code that bridges population business logic with quest system.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from backend.systems.population.utils.disease_models import (
    DiseaseType,
    DiseaseStage,
    DISEASE_PROFILES
)

logger = logging.getLogger(__name__)


class QuestPriority(Enum):
    """Quest priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuestType(Enum):
    """Types of quests that can be generated"""
    INVESTIGATION = "investigation"
    GATHERING = "gathering"
    DELIVERY = "delivery"
    PROTECTION = "protection"
    EVACUATION = "evacuation"
    EXTERMINATION = "extermination"
    REBUILDING = "rebuilding"
    MEMORIAL = "memorial"
    ESCORT = "escort"
    RESCUE = "rescue"


@dataclass
class PopulationQuest:
    """Represents a quest generated from population events"""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    priority: QuestPriority
    population_id: str
    event_source: str  # "disease_outbreak", "population_change", etc.
    
    # Quest parameters
    rewards: Dict[str, Any]
    requirements: List[str]
    estimated_duration_hours: int
    max_participants: int
    
    # Population-specific data
    source_event_data: Dict[str, Any]
    location_hint: Optional[str] = None
    expiry_date: Optional[datetime] = None
    
    # Quest state
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class PopulationQuestGenerator:
    """Generates quests based on population system events"""
    
    def __init__(self):
        self.active_quests: Dict[str, PopulationQuest] = {}
        self.quest_templates = self._initialize_quest_templates()
        self.quest_counter = 0
        
    def _initialize_quest_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quest templates for different scenarios"""
        return {
            # Disease outbreak quest templates
            "disease_investigation": {
                "title_template": "Investigate {disease_name} Outbreak",
                "description_template": "Strange reports of {disease_name} have emerged in {location}. Investigate the source and gather information about the outbreak's origins.",
                "quest_type": QuestType.INVESTIGATION,
                "priority": QuestPriority.MEDIUM,
                "requirements": ["investigation_skill", "disease_resistance"],
                "rewards": {"experience": 150, "reputation": 50, "gold": 100},
                "duration_hours": 4,
                "max_participants": 2
            },
            "medicine_gathering": {
                "title_template": "Gather Medicinal Supplies",
                "description_template": "The {disease_name} outbreak requires immediate medical attention. Gather herbs and medical supplies to help treat the afflicted.",
                "quest_type": QuestType.GATHERING,
                "priority": QuestPriority.MEDIUM,
                "requirements": ["herbalism", "foraging"],
                "rewards": {"experience": 100, "items": ["healing_potion", "herb_bundle"], "gold": 75},
                "duration_hours": 3,
                "max_participants": 4
            },
            "emergency_delivery": {
                "title_template": "Emergency Medicine Delivery",
                "description_template": "Rush critical medical supplies to {location} to contain the spreading {disease_name} outbreak before it becomes uncontrollable.",
                "quest_type": QuestType.DELIVERY,
                "priority": QuestPriority.HIGH,
                "requirements": ["fast_travel", "disease_resistance", "courier_experience"],
                "rewards": {"experience": 200, "reputation": 100, "gold": 200},
                "duration_hours": 2,
                "max_participants": 1
            },
            "quarantine_enforcement": {
                "title_template": "Enforce Quarantine Measures",
                "description_template": "Help local authorities enforce quarantine measures to prevent {disease_name} from spreading to neighboring settlements.",
                "quest_type": QuestType.PROTECTION,
                "priority": QuestPriority.HIGH,
                "requirements": ["combat_skill", "persuasion", "authority"],
                "rewards": {"experience": 180, "reputation": 150, "gold": 150},
                "duration_hours": 6,
                "max_participants": 3
            },
            "emergency_evacuation": {
                "title_template": "Emergency Evacuation",
                "description_template": "The {disease_name} outbreak has reached critical levels. Help evacuate healthy citizens from the devastated areas of {location}.",
                "quest_type": QuestType.EVACUATION,
                "priority": QuestPriority.CRITICAL,
                "requirements": ["leadership", "logistics", "disease_immunity"],
                "rewards": {"experience": 300, "reputation": 200, "title": "Life Saver", "gold": 300},
                "duration_hours": 8,
                "max_participants": 5
            },
            "source_elimination": {
                "title_template": "Eliminate Disease Source",
                "description_template": "Find and eliminate the supernatural or unnatural source of the {disease_name} outbreak that has devastated {location}.",
                "quest_type": QuestType.EXTERMINATION,
                "priority": QuestPriority.CRITICAL,
                "requirements": ["combat_skill", "magic_resistance", "disease_immunity", "legendary_weapon"],
                "rewards": {"experience": 500, "reputation": 300, "legendary_item": True, "gold": 500},
                "duration_hours": 12,
                "max_participants": 4
            },
            "community_rebuilding": {
                "title_template": "Rebuild {location}",
                "description_template": "Help rebuild {location} after the devastating {disease_name} outbreak. The community needs resources, expertise, and hope.",
                "quest_type": QuestType.REBUILDING,
                "priority": QuestPriority.LOW,
                "requirements": ["crafting", "leadership", "resources"],
                "rewards": {"experience": 250, "reputation": 200, "property_deed": True, "gold": 200},
                "duration_hours": 24,
                "max_participants": 8
            },
            "memorial_construction": {
                "title_template": "Build Memorial for the Lost",
                "description_template": "Construct a memorial to honor those who perished during the {disease_name} outbreak in {location}.",
                "quest_type": QuestType.MEMORIAL,
                "priority": QuestPriority.LOW,
                "requirements": ["crafting", "stone_working", "artistic_skill"],
                "rewards": {"experience": 150, "reputation": 100, "honor_points": 50, "gold": 100},
                "duration_hours": 16,
                "max_participants": 6
            },
            # Population change quest templates
            "refugee_escort": {
                "title_template": "Escort Refugees",
                "description_template": "Safely escort refugees fleeing from {location} due to {reason} to nearby settlements.",
                "quest_type": QuestType.ESCORT,
                "priority": QuestPriority.MEDIUM,
                "requirements": ["combat_skill", "survival", "leadership"],
                "rewards": {"experience": 180, "reputation": 120, "gold": 150},
                "duration_hours": 8,
                "max_participants": 4
            },
            "population_rescue": {
                "title_template": "Rescue Trapped Citizens",
                "description_template": "Rescue citizens trapped in {location} due to {reason}. Time is of the essence.",
                "quest_type": QuestType.RESCUE,
                "priority": QuestPriority.HIGH,
                "requirements": ["rescue_skill", "combat_skill", "disease_resistance"],
                "rewards": {"experience": 250, "reputation": 180, "gold": 200},
                "duration_hours": 6,
                "max_participants": 3
            }
        }
    
    def generate_disease_outbreak_quests(
        self,
        population_id: str,
        disease_type: DiseaseType,
        disease_stage: DiseaseStage,
        outbreak_data: Dict[str, Any],
        location_name: Optional[str] = None
    ) -> List[PopulationQuest]:
        """Generate quests based on disease outbreak stage"""
        
        profile = DISEASE_PROFILES[disease_type]
        location = location_name or f"Settlement {population_id}"
        quest_list = []
        
        # Generate quests based on disease stage
        if disease_stage == DiseaseStage.EMERGING:
            # Investigation and gathering quests
            quest_list.extend([
                self._create_quest_from_template(
                    "disease_investigation",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                ),
                self._create_quest_from_template(
                    "medicine_gathering",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                )
            ])
            
        elif disease_stage == DiseaseStage.SPREADING:
            # Delivery and protection quests
            quest_list.extend([
                self._create_quest_from_template(
                    "emergency_delivery",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                ),
                self._create_quest_from_template(
                    "quarantine_enforcement",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                )
            ])
            
        elif disease_stage == DiseaseStage.PEAK:
            # Critical evacuation and elimination quests
            quest_list.extend([
                self._create_quest_from_template(
                    "emergency_evacuation",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                ),
                self._create_quest_from_template(
                    "source_elimination",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                )
            ])
            
        elif disease_stage == DiseaseStage.DECLINING:
            # Rebuilding and memorial quests
            quest_list.extend([
                self._create_quest_from_template(
                    "community_rebuilding",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                ),
                self._create_quest_from_template(
                    "memorial_construction",
                    population_id,
                    "disease_outbreak",
                    {
                        "disease_name": profile.name,
                        "location": location,
                        "disease_type": disease_type.value,
                        "stage": disease_stage.value,
                        **outbreak_data
                    }
                )
            ])
        
        # Store generated quests
        for quest in quest_list:
            self.active_quests[quest.quest_id] = quest
            
        return quest_list
    
    def generate_population_change_quests(
        self,
        population_id: str,
        old_count: int,
        new_count: int,
        change_reason: str,
        location_name: Optional[str] = None
    ) -> List[PopulationQuest]:
        """Generate quests based on population changes"""
        
        location = location_name or f"Settlement {population_id}"
        quest_list = []
        
        # Significant population decrease might generate rescue/escort quests
        if new_count < old_count * 0.8:  # 20% or more decrease
            if "disease" in change_reason.lower():
                # Rescue quests for disease-related population loss
                quest_list.append(
                    self._create_quest_from_template(
                        "population_rescue",
                        population_id,
                        "population_change",
                        {
                            "location": location,
                            "reason": change_reason,
                            "population_loss": old_count - new_count,
                            "old_count": old_count,
                            "new_count": new_count
                        }
                    )
                )
            else:
                # General refugee escort quests
                quest_list.append(
                    self._create_quest_from_template(
                        "refugee_escort",
                        population_id,
                        "population_change",
                        {
                            "location": location,
                            "reason": change_reason,
                            "population_loss": old_count - new_count,
                            "old_count": old_count,
                            "new_count": new_count
                        }
                    )
                )
        
        # Store generated quests
        for quest in quest_list:
            self.active_quests[quest.quest_id] = quest
            
        return quest_list
    
    def _create_quest_from_template(
        self,
        template_name: str,
        population_id: str,
        event_source: str,
        template_data: Dict[str, Any]
    ) -> PopulationQuest:
        """Create a quest from a template"""
        
        template = self.quest_templates[template_name]
        self.quest_counter += 1
        
        quest_id = f"pop_quest_{population_id}_{template_name}_{self.quest_counter}"
        
        title = template["title_template"].format(**template_data)
        description = template["description_template"].format(**template_data)
        
        # Set expiry date based on quest type and priority
        expiry_hours = template["duration_hours"] * 2  # Quest expires after double its estimated duration
        expiry_date = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        return PopulationQuest(
            quest_id=quest_id,
            title=title,
            description=description,
            quest_type=template["quest_type"],
            priority=template["priority"],
            population_id=population_id,
            event_source=event_source,
            rewards=template["rewards"],
            requirements=template["requirements"],
            estimated_duration_hours=template["duration_hours"],
            max_participants=template["max_participants"],
            source_event_data=template_data,
            location_hint=template_data.get("location"),
            expiry_date=expiry_date
        )
    
    def get_active_quests_for_population(self, population_id: str) -> List[PopulationQuest]:
        """Get all active quests for a specific population"""
        return [
            quest for quest in self.active_quests.values()
            if quest.population_id == population_id and quest.is_active
        ]
    
    def get_quests_by_priority(self, priority: QuestPriority) -> List[PopulationQuest]:
        """Get all active quests of a specific priority"""
        return [
            quest for quest in self.active_quests.values()
            if quest.priority == priority and quest.is_active
        ]
    
    def complete_quest(self, quest_id: str) -> bool:
        """Mark a quest as completed"""
        if quest_id in self.active_quests:
            self.active_quests[quest_id].is_active = False
            return True
        return False
    
    def expire_old_quests(self) -> List[str]:
        """Expire quests that have passed their expiry date"""
        now = datetime.utcnow()
        expired_quest_ids = []
        
        for quest_id, quest in self.active_quests.items():
            if quest.expiry_date and now > quest.expiry_date and quest.is_active:
                quest.is_active = False
                expired_quest_ids.append(quest_id)
                
        return expired_quest_ids
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated quests"""
        total_quests = len(self.active_quests)
        active_quests = len([q for q in self.active_quests.values() if q.is_active])
        
        priority_counts = {}
        type_counts = {}
        source_counts = {}
        
        for quest in self.active_quests.values():
            if quest.is_active:
                priority_counts[quest.priority.value] = priority_counts.get(quest.priority.value, 0) + 1
                type_counts[quest.quest_type.value] = type_counts.get(quest.quest_type.value, 0) + 1
                source_counts[quest.event_source] = source_counts.get(quest.event_source, 0) + 1
        
        return {
            "total_quests_generated": total_quests,
            "active_quests": active_quests,
            "completed_quests": total_quests - active_quests,
            "quests_by_priority": priority_counts,
            "quests_by_type": type_counts,
            "quests_by_source": source_counts
        }


# Global quest generator instance
population_quest_generator = PopulationQuestGenerator()


# Integration functions for population system events
async def handle_disease_outbreak_quest_generation(
    population_id: str,
    disease_type: DiseaseType,
    disease_stage: DiseaseStage,
    outbreak_data: Dict[str, Any],
    location_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Handle quest generation for disease outbreaks"""
    
    try:
        # Generate quests
        quests = population_quest_generator.generate_disease_outbreak_quests(
            population_id, disease_type, disease_stage, outbreak_data, location_name
        )
        
        # Convert to dict format for API responses
        quest_dicts = []
        for quest in quests:
            quest_dicts.append({
                "quest_id": quest.quest_id,
                "title": quest.title,
                "description": quest.description,
                "type": quest.quest_type.value,
                "priority": quest.priority.value,
                "rewards": quest.rewards,
                "requirements": quest.requirements,
                "estimated_duration_hours": quest.estimated_duration_hours,
                "max_participants": quest.max_participants,
                "location_hint": quest.location_hint,
                "expiry_date": quest.expiry_date.isoformat() if quest.expiry_date else None,
                "created_at": quest.created_at.isoformat()
            })
        
        logger.info(f"Generated {len(quests)} quests for disease outbreak: {disease_type.value} in {population_id}")
        return quest_dicts
        
    except Exception as e:
        logger.error(f"Error generating disease outbreak quests: {str(e)}")
        return []


async def handle_population_change_quest_generation(
    population_id: str,
    old_count: int,
    new_count: int,
    change_reason: str,
    location_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Handle quest generation for population changes"""
    
    try:
        # Only generate quests for significant changes
        change_percentage = abs(new_count - old_count) / old_count if old_count > 0 else 0
        if change_percentage < 0.1:  # Less than 10% change
            return []
        
        # Generate quests
        quests = population_quest_generator.generate_population_change_quests(
            population_id, old_count, new_count, change_reason, location_name
        )
        
        # Convert to dict format
        quest_dicts = []
        for quest in quests:
            quest_dicts.append({
                "quest_id": quest.quest_id,
                "title": quest.title,
                "description": quest.description,
                "type": quest.quest_type.value,
                "priority": quest.priority.value,
                "rewards": quest.rewards,
                "requirements": quest.requirements,
                "estimated_duration_hours": quest.estimated_duration_hours,
                "max_participants": quest.max_participants,
                "location_hint": quest.location_hint,
                "expiry_date": quest.expiry_date.isoformat() if quest.expiry_date else None,
                "created_at": quest.created_at.isoformat()
            })
        
        logger.info(f"Generated {len(quests)} quests for population change: {old_count} -> {new_count} in {population_id}")
        return quest_dicts
        
    except Exception as e:
        logger.error(f"Error generating population change quests: {str(e)}")
        return []


# Export functions and classes
__all__ = [
    "PopulationQuest",
    "QuestPriority", 
    "QuestType",
    "PopulationQuestGenerator",
    "population_quest_generator",
    "handle_disease_outbreak_quest_generation",
    "handle_population_change_quest_generation"
] 