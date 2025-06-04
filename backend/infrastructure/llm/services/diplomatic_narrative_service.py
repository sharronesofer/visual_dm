"""
Diplomatic Narrative Service

Infrastructure service that integrates LLM capabilities with the diplomacy system
to generate AI-powered diplomatic narratives, dialogue, and storytelling.
"""

from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime

from backend.infrastructure.llm.services.llm_service import LLMService
from backend.infrastructure.llm.services.prompt_manager import PromptManager
from backend.infrastructure.llm.services.context_manager import ContextManager


class DiplomaticNarrativeService:
    """
    Infrastructure service for AI-powered diplomatic narratives.
    
    Integrates with LLM services to generate realistic diplomatic communications,
    treaty narratives, and conflict descriptions based on faction personalities
    and diplomatic contexts.
    """
    
    def __init__(self, 
                 llm_service: Optional[LLMService] = None,
                 prompt_manager: Optional[PromptManager] = None,
                 context_manager: Optional[ContextManager] = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_manager = prompt_manager or PromptManager()
        self.context_manager = context_manager or ContextManager()
    
    async def generate_treaty_announcement(self,
                                         treaty_data: Dict[str, Any],
                                         faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate a narrative announcement for a new treaty."""
        
        context = {
            "treaty_type": treaty_data.get("type"),
            "parties": treaty_data.get("parties", []),
            "terms": treaty_data.get("terms", {}),
            "faction_personalities": faction_personalities,
            "historical_context": treaty_data.get("historical_context", {})
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_treaty_announcement", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7,
            context_name=f"treaty_{treaty_data.get('id')}"
        )
        
        return response.get("content", "A new treaty has been established.")
    
    async def generate_diplomatic_dialogue(self,
                                         faction_a_id: UUID,
                                         faction_b_id: UUID,
                                         conversation_context: Dict[str, Any],
                                         faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate realistic diplomatic dialogue between factions."""
        
        context = {
            "faction_a": {
                "id": str(faction_a_id),
                "personality": faction_personalities.get(faction_a_id, {}),
                "recent_actions": conversation_context.get("faction_a_actions", [])
            },
            "faction_b": {
                "id": str(faction_b_id),
                "personality": faction_personalities.get(faction_b_id, {}),
                "recent_actions": conversation_context.get("faction_b_actions", [])
            },
            "relationship_status": conversation_context.get("relationship_status"),
            "negotiation_topic": conversation_context.get("topic"),
            "current_tensions": conversation_context.get("tensions", 0),
            "historical_events": conversation_context.get("history", [])
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_dialogue", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.8,
            context_name=f"dialogue_{faction_a_id}_{faction_b_id}"
        )
        
        return response.get("content", "The diplomatic discussion continues.")
    
    async def generate_conflict_narrative(self,
                                        conflict_data: Dict[str, Any],
                                        faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate a narrative description of a diplomatic conflict."""
        
        context = {
            "conflict_type": conflict_data.get("type", "border_dispute"),
            "primary_factions": conflict_data.get("factions", []),
            "conflict_causes": conflict_data.get("causes", []),
            "escalation_events": conflict_data.get("events", []),
            "faction_personalities": faction_personalities,
            "regional_context": conflict_data.get("region_info", {}),
            "severity_level": conflict_data.get("severity", "moderate")
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_conflict_narrative", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7,
            context_name=f"conflict_{conflict_data.get('id')}"
        )
        
        return response.get("content", "A diplomatic conflict has emerged.")
    
    async def generate_alliance_story(self,
                                    alliance_data: Dict[str, Any],
                                    faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate a narrative story for alliance formation."""
        
        context = {
            "alliance_type": alliance_data.get("type", "mutual_defense"),
            "member_factions": alliance_data.get("members", []),
            "alliance_goals": alliance_data.get("goals", []),
            "formation_circumstances": alliance_data.get("circumstances", {}),
            "faction_personalities": faction_personalities,
            "mutual_threats": alliance_data.get("threats", []),
            "expected_benefits": alliance_data.get("benefits", [])
        }
        
        prompt = self.prompt_manager.get_prompt("alliance_formation_story", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=450,
            temperature=0.7,
            context_name=f"alliance_{alliance_data.get('id')}"
        )
        
        return response.get("content", "A new alliance has been forged.")
    
    async def generate_decision_rationale(self,
                                        decision_type: str,
                                        decision_context: Dict[str, Any],
                                        faction_personality: Dict[str, Any]) -> str:
        """Generate an explanation for a diplomatic decision."""
        
        context = {
            "decision_type": decision_type,
            "faction_personality": faction_personality,
            "decision_factors": decision_context.get("factors", []),
            "relationship_context": decision_context.get("relationships", {}),
            "strategic_goals": decision_context.get("goals", []),
            "risk_assessment": decision_context.get("risks", {}),
            "timing_factors": decision_context.get("timing", {})
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_decision_rationale", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.6,
            context_name=f"decision_{decision_type}_{decision_context.get('faction_id')}"
        )
        
        return response.get("content", f"The faction has decided to {decision_type}.")
    
    async def generate_ultimatum_text(self,
                                    ultimatum_data: Dict[str, Any],
                                    issuer_personality: Dict[str, Any],
                                    recipient_personality: Dict[str, Any]) -> str:
        """Generate the text content of a diplomatic ultimatum."""
        
        context = {
            "issuer_personality": issuer_personality,
            "recipient_personality": recipient_personality,
            "demands": ultimatum_data.get("demands", []),
            "consequences": ultimatum_data.get("consequences", []),
            "deadline": ultimatum_data.get("deadline"),
            "justification": ultimatum_data.get("justification", ""),
            "relationship_history": ultimatum_data.get("history", []),
            "severity": ultimatum_data.get("severity", "moderate")
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_ultimatum", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=350,
            temperature=0.6,
            context_name=f"ultimatum_{ultimatum_data.get('id')}"
        )
        
        return response.get("content", "An ultimatum has been issued.")
    
    async def enhance_diplomatic_event(self,
                                     event_data: Dict[str, Any],
                                     faction_personalities: Dict[UUID, Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance a diplomatic event with AI-generated narrative elements."""
        
        enhanced_event = event_data.copy()
        
        # Generate narrative description
        narrative = await self.generate_event_narrative(event_data, faction_personalities)
        enhanced_event["narrative_description"] = narrative
        
        # Generate dialogue if applicable
        if event_data.get("involves_communication"):
            dialogue = await self.generate_diplomatic_dialogue(
                event_data.get("primary_faction"),
                event_data.get("secondary_faction"),
                event_data.get("context", {}),
                faction_personalities
            )
            enhanced_event["dialogue"] = dialogue
        
        # Generate consequences narrative
        if event_data.get("consequences"):
            consequences_narrative = await self.generate_consequences_narrative(
                event_data.get("consequences"),
                faction_personalities
            )
            enhanced_event["consequences_narrative"] = consequences_narrative
        
        return enhanced_event
    
    async def generate_event_narrative(self,
                                     event_data: Dict[str, Any],
                                     faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate a narrative description for a diplomatic event."""
        
        context = {
            "event_type": event_data.get("type"),
            "participants": event_data.get("participants", []),
            "location": event_data.get("location"),
            "circumstances": event_data.get("circumstances", {}),
            "faction_personalities": faction_personalities,
            "outcome": event_data.get("outcome"),
            "significance": event_data.get("significance", "minor")
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_event_narrative", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
            context_name=f"event_{event_data.get('id')}"
        )
        
        return response.get("content", "A diplomatic event has occurred.")
    
    async def generate_consequences_narrative(self,
                                           consequences: List[Dict[str, Any]],
                                           faction_personalities: Dict[UUID, Dict[str, Any]]) -> str:
        """Generate narrative for diplomatic consequences."""
        
        context = {
            "consequences": consequences,
            "faction_personalities": faction_personalities,
            "immediate_effects": [c for c in consequences if c.get("timing") == "immediate"],
            "long_term_effects": [c for c in consequences if c.get("timing") == "long_term"]
        }
        
        prompt = self.prompt_manager.get_prompt("diplomatic_consequences", context)
        
        response = await self.llm_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.6,
            context_name="consequences"
        )
        
        return response.get("content", "The diplomatic action has consequences.")


def create_diplomatic_narrative_service() -> DiplomaticNarrativeService:
    """Factory function to create diplomatic narrative service with dependencies."""
    return DiplomaticNarrativeService() 