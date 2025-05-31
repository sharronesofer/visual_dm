"""
Arc system - Quest Integration Service.

This module implements the bridge between arcs and the quest system
for seamless integration and tag-based quest generation.
"""

from typing import Optional, Dict, Any, List
import logging
from uuid import UUID

from backend.infrastructure.models import BaseService
from backend.systems.arc.models.arc import ArcModel

logger = logging.getLogger(__name__)


class QuestIntegrationService(BaseService):
    """Service for integrating arcs with the quest system"""
    
    def __init__(self, db_session=None, quest_service=None, arc_service=None):
        super().__init__(db_session, ArcModel)
        self.quest_service = quest_service
        self.arc_service = arc_service
        self.tag_mappings = self._initialize_tag_mappings()
        
    def _initialize_tag_mappings(self) -> Dict[str, List[str]]:
        """Initialize tag mappings between arcs and quests"""
        return {
            "global": [
                "world_event", "campaign", "epic", "faction_war", 
                "ancient_threat", "divine_intervention", "planar"
            ],
            "regional": [
                "local_politics", "regional_threat", "community", 
                "trade_route", "natural_disaster", "local_legend"
            ],
            "character": [
                "personal_growth", "backstory", "relationship", 
                "skill_development", "moral_choice", "redemption"
            ],
            "npc": [
                "supporting_character", "ally_quest", "rival_story", 
                "mentor_guidance", "romance", "family_ties"
            ],
            "exploration": [
                "dungeon_delve", "wilderness_trek", "ancient_ruins", 
                "hidden_location", "treasure_hunt", "mapping"
            ],
            "social": [
                "diplomacy", "intrigue", "court_politics", "negotiation", 
                "social_event", "reputation", "alliance_building"
            ],
            "mystery": [
                "investigation", "murder_mystery", "conspiracy", 
                "hidden_truth", "ancient_secret", "puzzle"
            ],
            "combat": [
                "monster_hunt", "bandit_clearing", "siege_defense", 
                "arena_combat", "military_campaign", "duel"
            ]
        }
    
    async def generate_quests_for_arc(
        self,
        arc_id: UUID,
        step_number: Optional[int] = None,
        quest_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate quests based on arc content and tags"""
        try:
            # Get arc data (would fetch from repository)
            arc_data = await self._get_arc_data(arc_id)
            
            # Determine arc type and extract tags
            arc_type = arc_data.get("properties", {}).get("arc_type", "global")
            arc_tags = self._extract_arc_tags(arc_data, arc_type)
            
            # Generate quest opportunities
            quest_opportunities = []
            
            for i in range(quest_count):
                quest_data = await self._generate_quest_from_tags(
                    arc_tags, arc_data, step_number, i
                )
                quest_opportunities.append(quest_data)
            
            logger.info(f"Generated {len(quest_opportunities)} quests for arc {arc_id}")
            return quest_opportunities
            
        except Exception as e:
            logger.error(f"Error generating quests for arc: {e}")
            raise
    
    def _extract_arc_tags(self, arc_data: Dict[str, Any], arc_type: str) -> List[str]:
        """Extract relevant tags from arc data"""
        base_tags = self.tag_mappings.get(arc_type, [])
        
        # Add tags based on arc properties
        properties = arc_data.get("properties", {})
        additional_tags = []
        
        # Extract tags from arc description and properties
        description = arc_data.get("description", "").lower()
        
        # Map keywords to tags
        keyword_mappings = {
            "combat": ["combat", "monster_hunt", "bandit_clearing"],
            "mystery": ["investigation", "mystery", "hidden_truth"],
            "political": ["diplomacy", "intrigue", "court_politics"],
            "exploration": ["exploration", "dungeon_delve", "wilderness_trek"],
            "social": ["social", "reputation", "alliance_building"],
            "ancient": ["ancient_ruins", "ancient_secret", "ancient_threat"],
            "faction": ["faction_war", "local_politics", "alliance_building"],
            "personal": ["personal_growth", "backstory", "relationship"]
        }
        
        for keyword, tags in keyword_mappings.items():
            if keyword in description:
                additional_tags.extend(tags)
        
        # Combine and deduplicate tags
        all_tags = list(set(base_tags + additional_tags))
        
        return all_tags[:10]  # Limit to top 10 most relevant tags
    
    async def _generate_quest_from_tags(
        self,
        tags: List[str],
        arc_data: Dict[str, Any],
        step_number: Optional[int],
        quest_index: int
    ) -> Dict[str, Any]:
        """Generate a quest based on tags and arc context"""
        try:
            # Select primary tags for this quest
            primary_tags = tags[:3] if len(tags) >= 3 else tags
            
            # Generate quest based on tags
            quest_templates = {
                "combat": {
                    "title": "Clear the Threat",
                    "description": "Eliminate hostile forces threatening the area",
                    "objectives": ["Locate enemy forces", "Engage in combat", "Secure the area"],
                    "rewards": {"experience": 500, "gold": 100}
                },
                "mystery": {
                    "title": "Uncover the Truth",
                    "description": "Investigate mysterious events and reveal hidden secrets",
                    "objectives": ["Gather clues", "Interview witnesses", "Solve the mystery"],
                    "rewards": {"experience": 400, "reputation": 50}
                },
                "exploration": {
                    "title": "Explore the Unknown",
                    "description": "Venture into uncharted territory and discover new locations",
                    "objectives": ["Map the area", "Discover points of interest", "Report findings"],
                    "rewards": {"experience": 300, "map_data": True}
                },
                "social": {
                    "title": "Build Relationships",
                    "description": "Establish connections and improve standing with key figures",
                    "objectives": ["Meet important NPCs", "Complete social tasks", "Gain reputation"],
                    "rewards": {"reputation": 100, "social_connections": 3}
                }
            }
            
            # Select template based on primary tag
            template_key = "exploration"  # Default
            for tag in primary_tags:
                if tag in ["monster_hunt", "bandit_clearing", "combat"]:
                    template_key = "combat"
                    break
                elif tag in ["investigation", "mystery", "hidden_truth"]:
                    template_key = "mystery"
                    break
                elif tag in ["diplomacy", "social", "reputation"]:
                    template_key = "social"
                    break
                elif tag in ["exploration", "dungeon_delve", "wilderness_trek"]:
                    template_key = "exploration"
                    break
            
            template = quest_templates[template_key]
            
            # Customize quest based on arc context
            quest_data = {
                "id": f"quest_{arc_data.get('id', 'unknown')}_{quest_index}",
                "title": f"{template['title']} - {arc_data.get('name', 'Arc Quest')}",
                "description": f"{template['description']} as part of {arc_data.get('name', 'the current arc')}",
                "objectives": template["objectives"],
                "rewards": template["rewards"],
                "tags": primary_tags,
                "arc_id": arc_data.get("id"),
                "step_number": step_number,
                "quest_type": template_key,
                "priority": "medium",
                "estimated_duration": 60,  # minutes
                "difficulty": self._calculate_quest_difficulty(primary_tags),
                "prerequisites": [],
                "generated": True,
                "generation_context": {
                    "arc_name": arc_data.get("name"),
                    "arc_type": arc_data.get("properties", {}).get("arc_type"),
                    "tags_used": primary_tags
                }
            }
            
            return quest_data
            
        except Exception as e:
            logger.error(f"Error generating quest from tags: {e}")
            raise
    
    def _calculate_quest_difficulty(self, tags: List[str]) -> str:
        """Calculate quest difficulty based on tags"""
        difficulty_weights = {
            "combat": 3,
            "monster_hunt": 4,
            "ancient_threat": 5,
            "faction_war": 4,
            "investigation": 2,
            "mystery": 2,
            "exploration": 2,
            "social": 1,
            "diplomacy": 2
        }
        
        total_weight = sum(difficulty_weights.get(tag, 1) for tag in tags)
        avg_weight = total_weight / len(tags) if tags else 1
        
        if avg_weight >= 4:
            return "hard"
        elif avg_weight >= 2.5:
            return "medium"
        else:
            return "easy"
    
    async def link_quest_to_arc_step(
        self,
        quest_id: UUID,
        arc_id: UUID,
        step_number: int
    ) -> Dict[str, Any]:
        """Link a quest to a specific arc step"""
        try:
            # Create link record
            link_data = {
                "quest_id": str(quest_id),
                "arc_id": str(arc_id),
                "step_number": step_number,
                "link_type": "step_quest",
                "created_at": "now",  # Would use actual timestamp
                "status": "active"
            }
            
            # Update quest with arc context (would call quest service)
            if self.quest_service:
                await self.quest_service.update_quest_context(quest_id, {
                    "arc_id": str(arc_id),
                    "step_number": step_number,
                    "arc_context": True
                })
            
            logger.info(f"Linked quest {quest_id} to arc {arc_id} step {step_number}")
            return link_data
            
        except Exception as e:
            logger.error(f"Error linking quest to arc step: {e}")
            raise
    
    async def get_arc_quest_progress(self, arc_id: UUID) -> Dict[str, Any]:
        """Get progress of all quests linked to an arc"""
        try:
            # This would query linked quests and their progress
            # For now, return mock data
            
            progress_data = {
                "arc_id": str(arc_id),
                "total_quests": 5,
                "completed_quests": 2,
                "active_quests": 2,
                "failed_quests": 1,
                "completion_percentage": 40.0,
                "quest_details": [
                    {
                        "quest_id": "quest_1",
                        "title": "Clear the Threat - Arc Quest",
                        "status": "completed",
                        "step_number": 1,
                        "completion_date": "2024-01-01T12:00:00Z"
                    },
                    {
                        "quest_id": "quest_2",
                        "title": "Uncover the Truth - Arc Quest",
                        "status": "active",
                        "step_number": 2,
                        "progress": 60.0
                    }
                ]
            }
            
            logger.info(f"Retrieved quest progress for arc {arc_id}")
            return progress_data
            
        except Exception as e:
            logger.error(f"Error getting arc quest progress: {e}")
            raise
    
    async def sync_arc_quest_completion(
        self,
        arc_id: UUID,
        completed_quest_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Sync quest completions with arc progression"""
        try:
            # Update arc progression based on completed quests
            sync_results = {
                "arc_id": str(arc_id),
                "processed_quests": len(completed_quest_ids),
                "arc_updates": [],
                "step_progressions": []
            }
            
            for quest_id in completed_quest_ids:
                # Get quest-arc link data
                link_data = await self._get_quest_arc_link(quest_id, arc_id)
                
                if link_data:
                    step_number = link_data.get("step_number")
                    
                    # Update arc step progress
                    step_update = {
                        "step_number": step_number,
                        "quest_completed": str(quest_id),
                        "progress_contribution": 20.0  # Each quest contributes 20% to step
                    }
                    
                    sync_results["step_progressions"].append(step_update)
            
            logger.info(f"Synced {len(completed_quest_ids)} quest completions with arc {arc_id}")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error syncing quest completions: {e}")
            raise
    
    async def _get_arc_data(self, arc_id: UUID) -> Dict[str, Any]:
        """Get arc data (mock implementation)"""
        # This would fetch from the arc repository
        return {
            "id": str(arc_id),
            "name": "Sample Arc",
            "description": "A sample arc for testing quest integration with combat and mystery elements",
            "properties": {
                "arc_type": "regional",
                "complexity": "medium",
                "estimated_duration": 120
            }
        }
    
    async def _get_quest_arc_link(self, quest_id: UUID, arc_id: UUID) -> Optional[Dict[str, Any]]:
        """Get quest-arc link data (mock implementation)"""
        # This would fetch from the link repository
        return {
            "quest_id": str(quest_id),
            "arc_id": str(arc_id),
            "step_number": 2,
            "link_type": "step_quest",
            "status": "active"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "status": "healthy",
            "service": "QuestIntegrationService",
            "tag_mappings_loaded": len(self.tag_mappings),
            "quest_service_available": self.quest_service is not None,
            "arc_service_available": self.arc_service is not None
        }
