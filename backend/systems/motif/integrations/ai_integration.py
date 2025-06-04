"""
Motif AI Integration

Provides thematic guidance to AI/LLM systems for consistent narrative generation.
This is the primary integration point for the motif system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from backend.infrastructure.systems.motif.models.models import Motif, MotifScope, MotifLifecycle

logger = logging.getLogger(__name__)

class MotifAIConnector:
    """Connector for integrating motifs with AI/LLM systems"""
    
    def __init__(self, motif_manager):
        self.motif_manager = motif_manager
        
    async def get_narrative_guidance(
        self, 
        context: Dict[str, Any],
        guidance_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Get comprehensive narrative guidance for AI systems
        
        Args:
            context: Context information (location, characters, etc.)
            guidance_type: Type of guidance ('dialogue', 'description', 'event', 'general')
            
        Returns:
            Structured guidance for AI generation
        """
        try:
            # Get applicable motifs based on context
            motifs = await self._get_contextual_motifs(context)
            
            if not motifs:
                return {
                    "has_guidance": False,
                    "guidance_type": guidance_type,
                    "message": "No active motifs affecting this context"
                }
            
            # Generate guidance based on type
            if guidance_type == "dialogue":
                return self._generate_dialogue_guidance(motifs, context)
            elif guidance_type == "description":
                return self._generate_description_guidance(motifs, context)
            elif guidance_type == "event":
                return self._generate_event_guidance(motifs, context)
            else:
                return self._generate_general_guidance(motifs, context)
                
        except Exception as e:
            logger.error(f"Error generating narrative guidance: {e}")
            return {
                "has_guidance": False,
                "guidance_type": guidance_type,
                "error": str(e)
            }
    
    async def _get_contextual_motifs(self, context: Dict[str, Any]) -> List[Motif]:
        """Get motifs applicable to the given context"""
        all_motifs = []
        
        # Always include global motifs
        global_motifs = await self.motif_manager.get_global_motifs()
        all_motifs.extend(global_motifs)
        
        # Include regional motifs if location provided
        if 'region_id' in context:
            regional_motifs = await self.motif_manager.get_regional_motifs(context['region_id'])
            all_motifs.extend(regional_motifs)
        
        # Include local motifs if position provided
        if 'x' in context and 'y' in context:
            local_motifs = await self.motif_manager.get_motifs_at_position(
                context['x'], context['y'], context.get('radius', 50.0)
            )
            all_motifs.extend(local_motifs)
        
        # Filter to active motifs only
        active_motifs = [m for m in all_motifs if m.lifecycle != MotifLifecycle.CONCLUDED]
        
        # Sort by intensity (strongest influence first)
        return sorted(active_motifs, key=lambda x: x.get_effective_intensity(), reverse=True)
    
    def _generate_dialogue_guidance(self, motifs: List[Motif], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guidance specifically for dialogue generation"""
        primary_motifs = motifs[:3]  # Top 3 most influential
        
        tone_guidance = []
        content_guidance = []
        mood_descriptors = []
        
        for motif in primary_motifs:
            # Extract tone guidance
            if motif.category.value in ['despair', 'grief', 'futility']:
                tone_guidance.append("melancholic and heavy")
            elif motif.category.value in ['hope', 'redemption', 'unity']:
                tone_guidance.append("optimistic and uplifting")
            elif motif.category.value in ['betrayal', 'paranoia', 'deception']:
                tone_guidance.append("suspicious and guarded")
            elif motif.category.value in ['power', 'control', 'pride']:
                tone_guidance.append("authoritative and confident")
                
            # Extract content guidance
            content_guidance.append(f"References to {motif.category.value} themes")
            
            # Add mood descriptors
            for descriptor in motif.descriptors[:2]:  # Limit to prevent overwhelming
                mood_descriptors.append(descriptor)
        
        return {
            "has_guidance": True,
            "guidance_type": "dialogue",
            "primary_motifs": [m.category.value for m in primary_motifs],
            "tone_guidance": tone_guidance,
            "content_suggestions": content_guidance,
            "mood_descriptors": mood_descriptors,
            "prompt_addition": f"Dialogue should reflect themes of {', '.join([m.category.value for m in primary_motifs[:2]])} with a {tone_guidance[0] if tone_guidance else 'neutral'} tone."
        }
    
    def _generate_description_guidance(self, motifs: List[Motif], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guidance for environmental/scene descriptions"""
        primary_motifs = motifs[:3]
        
        atmospheric_elements = []
        visual_cues = []
        sensory_details = []
        
        for motif in primary_motifs:
            # Generate atmospheric elements based on category
            if motif.category.value in ['chaos', 'collapse', 'ruin']:
                atmospheric_elements.extend(["disorder", "decay", "instability"])
                visual_cues.extend(["cracked structures", "overgrown vegetation", "scattered debris"])
            elif motif.category.value in ['peace', 'unity', 'harmony']:
                atmospheric_elements.extend(["tranquility", "balance", "serenity"])
                visual_cues.extend(["well-maintained areas", "flowing lines", "natural symmetry"])
            elif motif.category.value in ['shadow', 'mystery', 'silence']:
                atmospheric_elements.extend(["obscurity", "hidden depths", "quiet tension"])
                visual_cues.extend(["deep shadows", "muted lighting", "concealed details"])
                
            # Add intensity-based modifiers
            if motif.get_effective_intensity() >= 8:
                sensory_details.append(f"overwhelming sense of {motif.category.value}")
            elif motif.get_effective_intensity() >= 6:
                sensory_details.append(f"strong presence of {motif.category.value}")
            else:
                sensory_details.append(f"subtle undertones of {motif.category.value}")
        
        return {
            "has_guidance": True,
            "guidance_type": "description",
            "primary_motifs": [m.category.value for m in primary_motifs],
            "atmospheric_elements": atmospheric_elements,
            "visual_cues": visual_cues,
            "sensory_details": sensory_details,
            "prompt_addition": f"Descriptions should emphasize {', '.join(atmospheric_elements[:3])} with visual elements suggesting {', '.join([m.category.value for m in primary_motifs[:2]])}."
        }
    
    def _generate_event_guidance(self, motifs: List[Motif], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guidance for event generation and outcomes"""
        primary_motifs = motifs[:3]
        
        event_tendencies = []
        outcome_biases = []
        thematic_elements = []
        
        for motif in primary_motifs:
            # Determine event tendencies
            if motif.category.value in ['betrayal', 'deception', 'paranoia']:
                event_tendencies.append("trust is broken or tested")
                outcome_biases.append("unexpected reversals")
            elif motif.category.value in ['sacrifice', 'loyalty', 'protection']:
                event_tendencies.append("characters face moral choices")
                outcome_biases.append("heroic actions rewarded")
            elif motif.category.value in ['chaos', 'madness', 'collapse']:
                event_tendencies.append("order breaks down")
                outcome_biases.append("unpredictable consequences")
                
            thematic_elements.append(motif.category.value)
        
        return {
            "has_guidance": True,
            "guidance_type": "event",
            "primary_motifs": [m.category.value for m in primary_motifs],
            "event_tendencies": event_tendencies,
            "outcome_biases": outcome_biases,
            "thematic_elements": thematic_elements,
            "prompt_addition": f"Events should involve {', '.join(event_tendencies[:2])} and outcomes should tend toward {', '.join(outcome_biases[:2])}."
        }
    
    def _generate_general_guidance(self, motifs: List[Motif], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general narrative guidance"""
        if not motifs:
            return {"has_guidance": False}
            
        primary_motif = motifs[0]
        secondary_motifs = motifs[1:4]
        
        # Create synthesis guidance
        themes = [primary_motif.category.value]
        themes.extend([m.category.value for m in secondary_motifs])
        
        overall_tone = self._determine_overall_tone(motifs)
        narrative_direction = self._determine_narrative_direction(motifs)
        
        return {
            "has_guidance": True,
            "guidance_type": "general",
            "primary_theme": primary_motif.category.value,
            "secondary_themes": [m.category.value for m in secondary_motifs],
            "overall_tone": overall_tone,
            "narrative_direction": narrative_direction,
            "intensity_level": primary_motif.get_effective_intensity(),
            "prompt_addition": f"Narrative should emphasize {primary_motif.category.value} themes with a {overall_tone} tone, moving toward {narrative_direction}."
        }
    
    def _determine_overall_tone(self, motifs: List[Motif]) -> str:
        """Determine overall narrative tone from active motifs"""
        positive_categories = {'hope', 'redemption', 'unity', 'peace', 'protection', 'faith'}
        negative_categories = {'despair', 'betrayal', 'chaos', 'collapse', 'ruin', 'madness'}
        
        positive_weight = sum(m.get_effective_intensity() for m in motifs if m.category.value in positive_categories)
        negative_weight = sum(m.get_effective_intensity() for m in motifs if m.category.value in negative_categories)
        
        if positive_weight > negative_weight * 1.5:
            return "hopeful"
        elif negative_weight > positive_weight * 1.5:
            return "dark"
        else:
            return "complex"
    
    def _determine_narrative_direction(self, motifs: List[Motif]) -> str:
        """Determine narrative direction from motif lifecycles"""
        emerging_count = sum(1 for m in motifs if m.lifecycle == MotifLifecycle.EMERGING)
        waning_count = sum(1 for m in motifs if m.lifecycle == MotifLifecycle.WANING)
        
        if emerging_count > waning_count:
            return "rising_action"
        elif waning_count > emerging_count:
            return "resolution"
        else:
            return "steady_development"
    
    async def get_character_interaction_guidance(
        self, 
        character_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get guidance for character interactions based on motifs"""
        motifs = await self._get_contextual_motifs(context)
        
        # Filter to motifs that affect NPC behavior
        relevant_motifs = [m for m in motifs for effect in m.effects if effect.target.value == 'npc']
        
        if not relevant_motifs:
            return {"has_guidance": False, "character_id": character_id}
        
        behavior_modifiers = []
        dialogue_hints = []
        
        for motif in relevant_motifs[:3]:
            if motif.category.value in ['loyalty', 'unity']:
                behavior_modifiers.append("more trusting and cooperative")
            elif motif.category.value in ['betrayal', 'paranoia']:
                behavior_modifiers.append("suspicious and guarded")
            elif motif.category.value in ['despair', 'futility']:
                behavior_modifiers.append("pessimistic and withdrawn")
                
            dialogue_hints.append(f"references to {motif.category.value}")
        
        return {
            "has_guidance": True,
            "character_id": character_id,
            "behavior_modifiers": behavior_modifiers,
            "dialogue_hints": dialogue_hints,
            "affected_motifs": [m.name for m in relevant_motifs],
            "prompt_addition": f"Character behavior should be {', '.join(behavior_modifiers[:2])} with dialogue including {', '.join(dialogue_hints[:2])}."
        } 