"""
Motif NPC Integration

Provides motif-influenced behavior patterns and dialogue tone for NPCs.
Connects motifs to NPC personality and interaction systems.
"""

from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.systems.motif.models.models import Motif, MotifEffectTarget

logger = logging.getLogger(__name__)

class MotifNPCConnector:
    """Connector for integrating motifs with NPC behavior systems"""
    
    def __init__(self, motif_manager):
        self.motif_manager = motif_manager
    
    async def get_npc_behavior_modifiers(
        self, 
        npc_id: str, 
        location_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get behavior modifiers for an NPC based on active motifs
        
        Args:
            npc_id: ID of the NPC
            location_context: Current location and context
            
        Returns:
            Behavior modification data
        """
        try:
            # Get motifs affecting this location
            motifs = await self._get_location_motifs(location_context)
            
            # Filter to motifs that affect NPCs
            npc_affecting_motifs = [
                m for m in motifs 
                for effect in m.effects 
                if effect.target == MotifEffectTarget.NPC
            ]
            
            if not npc_affecting_motifs:
                return {
                    "has_modifiers": False,
                    "npc_id": npc_id,
                    "message": "No motifs affecting NPC behavior"
                }
            
            # Calculate behavior modifiers
            personality_shifts = self._calculate_personality_shifts(npc_affecting_motifs)
            dialogue_modifiers = self._calculate_dialogue_modifiers(npc_affecting_motifs)
            interaction_patterns = self._calculate_interaction_patterns(npc_affecting_motifs)
            
            return {
                "has_modifiers": True,
                "npc_id": npc_id,
                "affecting_motifs": [
                    {
                        "name": m.name,
                        "category": m.category.value,
                        "intensity": m.get_effective_intensity()
                    } for m in npc_affecting_motifs[:3]
                ],
                "personality_shifts": personality_shifts,
                "dialogue_modifiers": dialogue_modifiers,
                "interaction_patterns": interaction_patterns,
                "last_updated": location_context.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error getting NPC behavior modifiers for {npc_id}: {e}")
            return {
                "has_modifiers": False,
                "npc_id": npc_id,
                "error": str(e)
            }
    
    async def _get_location_motifs(self, location_context: Dict[str, Any]) -> List[Motif]:
        """Get all motifs affecting a location"""
        all_motifs = []
        
        # Global motifs always apply
        global_motifs = await self.motif_manager.get_global_motifs()
        all_motifs.extend(global_motifs)
        
        # Regional motifs
        if 'region_id' in location_context:
            regional_motifs = await self.motif_manager.get_regional_motifs(location_context['region_id'])
            all_motifs.extend(regional_motifs)
        
        # Local motifs
        if 'x' in location_context and 'y' in location_context:
            local_motifs = await self.motif_manager.get_motifs_at_position(
                location_context['x'], 
                location_context['y'],
                location_context.get('radius', 100.0)
            )
            all_motifs.extend(local_motifs)
        
        return all_motifs
    
    def _calculate_personality_shifts(self, motifs: List[Motif]) -> Dict[str, float]:
        """Calculate personality trait shifts based on motifs"""
        shifts = {
            "aggression": 0.0,
            "friendliness": 0.0,
            "suspicion": 0.0,
            "confidence": 0.0,
            "cooperation": 0.0,
            "emotional_stability": 0.0
        }
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            
            # Map motif categories to personality shifts
            if motif.category.value in ['betrayal', 'paranoia', 'deception']:
                shifts["suspicion"] += intensity_factor * 0.3
                shifts["friendliness"] -= intensity_factor * 0.2
                shifts["cooperation"] -= intensity_factor * 0.25
                
            elif motif.category.value in ['unity', 'loyalty', 'protection']:
                shifts["cooperation"] += intensity_factor * 0.3
                shifts["friendliness"] += intensity_factor * 0.2
                shifts["confidence"] += intensity_factor * 0.1
                
            elif motif.category.value in ['chaos', 'madness', 'collapse']:
                shifts["emotional_stability"] -= intensity_factor * 0.4
                shifts["aggression"] += intensity_factor * 0.2
                
            elif motif.category.value in ['power', 'control', 'pride']:
                shifts["confidence"] += intensity_factor * 0.3
                shifts["aggression"] += intensity_factor * 0.1
                
            elif motif.category.value in ['despair', 'grief', 'futility']:
                shifts["emotional_stability"] -= intensity_factor * 0.3
                shifts["friendliness"] -= intensity_factor * 0.1
                
            elif motif.category.value in ['hope', 'redemption', 'peace']:
                shifts["emotional_stability"] += intensity_factor * 0.2
                shifts["friendliness"] += intensity_factor * 0.2
        
        # Clamp values to reasonable ranges
        for key in shifts:
            shifts[key] = max(-1.0, min(1.0, shifts[key]))
        
        return shifts
    
    def _calculate_dialogue_modifiers(self, motifs: List[Motif]) -> Dict[str, Any]:
        """Calculate dialogue tone and content modifiers"""
        tone_weights = {
            "formal": 0.0,
            "casual": 0.0,
            "suspicious": 0.0,
            "friendly": 0.0,
            "melancholic": 0.0,
            "aggressive": 0.0,
            "confident": 0.0,
            "fearful": 0.0
        }
        
        content_themes = []
        word_choices = []
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            
            # Map categories to dialogue tones
            if motif.category.value in ['power', 'control', 'pride']:
                tone_weights["formal"] += intensity_factor
                tone_weights["confident"] += intensity_factor
                word_choices.extend(["authority", "command", "order"])
                
            elif motif.category.value in ['betrayal', 'paranoia', 'deception']:
                tone_weights["suspicious"] += intensity_factor
                word_choices.extend(["careful", "perhaps", "supposedly"])
                
            elif motif.category.value in ['unity', 'loyalty', 'protection']:
                tone_weights["friendly"] += intensity_factor
                word_choices.extend(["together", "trust", "support"])
                
            elif motif.category.value in ['despair', 'grief', 'futility']:
                tone_weights["melancholic"] += intensity_factor
                word_choices.extend(["sorrow", "loss", "pointless"])
                
            elif motif.category.value in ['chaos', 'madness', 'collapse']:
                tone_weights["fearful"] += intensity_factor
                tone_weights["aggressive"] += intensity_factor
                word_choices.extend(["chaos", "falling", "broken"])
            
            # Add thematic content
            content_themes.append(motif.category.value)
        
        # Determine dominant tone
        dominant_tone = max(tone_weights.items(), key=lambda x: x[1])[0]
        
        return {
            "tone_weights": tone_weights,
            "dominant_tone": dominant_tone,
            "content_themes": content_themes[:3],  # Limit to top 3
            "suggested_words": word_choices[:5],  # Limit to top 5
            "formality_level": tone_weights["formal"] - tone_weights["casual"]
        }
    
    def _calculate_interaction_patterns(self, motifs: List[Motif]) -> Dict[str, Any]:
        """Calculate how NPCs should interact with players/other NPCs"""
        patterns = {
            "approach_willingness": 0.5,  # 0-1 scale
            "information_sharing": 0.5,  # 0-1 scale
            "trade_favorability": 0.5,  # 0-1 scale
            "quest_enthusiasm": 0.5,  # 0-1 scale
            "combat_aggression": 0.5,  # 0-1 scale
        }
        
        special_behaviors = []
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            adjustment = intensity_factor * 0.1  # Small adjustments to avoid extremes
            
            if motif.category.value in ['loyalty', 'unity', 'protection']:
                patterns["approach_willingness"] += adjustment
                patterns["information_sharing"] += adjustment
                patterns["quest_enthusiasm"] += adjustment
                special_behaviors.append("offers_assistance")
                
            elif motif.category.value in ['betrayal', 'paranoia', 'deception']:
                patterns["approach_willingness"] -= adjustment
                patterns["information_sharing"] -= adjustment * 1.5
                patterns["trade_favorability"] -= adjustment
                special_behaviors.append("demands_proof")
                
            elif motif.category.value in ['despair', 'futility', 'grief']:
                patterns["quest_enthusiasm"] -= adjustment * 1.5
                patterns["approach_willingness"] -= adjustment
                special_behaviors.append("shares_troubles")
                
            elif motif.category.value in ['power', 'control', 'pride']:
                patterns["trade_favorability"] += adjustment
                patterns["combat_aggression"] += adjustment
                special_behaviors.append("expects_respect")
                
            elif motif.category.value in ['chaos', 'madness', 'collapse']:
                patterns["combat_aggression"] += adjustment * 1.5
                patterns["information_sharing"] -= adjustment
                special_behaviors.append("unpredictable_reactions")
        
        # Clamp all values to 0-1 range
        for key in patterns:
            patterns[key] = max(0.0, min(1.0, patterns[key]))
        
        return {
            "patterns": patterns,
            "special_behaviors": list(set(special_behaviors)),  # Remove duplicates
            "overall_disposition": self._determine_disposition(patterns)
        }
    
    def _determine_disposition(self, patterns: Dict[str, float]) -> str:
        """Determine overall NPC disposition from interaction patterns"""
        avg_positive = (
            patterns["approach_willingness"] + 
            patterns["information_sharing"] + 
            patterns["quest_enthusiasm"]
        ) / 3
        
        if avg_positive >= 0.7:
            return "welcoming"
        elif avg_positive >= 0.5:
            return "neutral"
        elif avg_positive >= 0.3:
            return "cautious"
        else:
            return "hostile"
    
    async def get_dialogue_context_for_npc(
        self, 
        npc_id: str, 
        conversation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get specific dialogue context influenced by motifs"""
        location_context = conversation_context.get('location', {})
        motifs = await self._get_location_motifs(location_context)
        
        # Filter to dialogue-affecting motifs
        dialogue_motifs = [
            m for m in motifs 
            for effect in m.effects 
            if effect.target == MotifEffectTarget.NPC and 
               effect.description and "dialogue" in effect.description.lower()
        ]
        
        if not dialogue_motifs:
            return {"has_context": False, "npc_id": npc_id}
        
        # Generate conversation prompts and restrictions
        conversation_starters = []
        topic_suggestions = []
        mood_indicators = []
        
        for motif in dialogue_motifs[:3]:
            if motif.category.value in ['grief', 'loss', 'despair']:
                conversation_starters.append(f"mentions recent {motif.category.value}")
                topic_suggestions.append("personal hardships")
                mood_indicators.append("somber")
                
            elif motif.category.value in ['hope', 'redemption', 'unity']:
                conversation_starters.append(f"speaks optimistically about {motif.category.value}")
                topic_suggestions.append("future possibilities")
                mood_indicators.append("uplifting")
                
            elif motif.category.value in ['betrayal', 'paranoia', 'deception']:
                conversation_starters.append(f"hints at recent {motif.category.value}")
                topic_suggestions.append("trust issues")
                mood_indicators.append("guarded")
        
        return {
            "has_context": True,
            "npc_id": npc_id,
            "affecting_motifs": [m.name for m in dialogue_motifs],
            "conversation_starters": conversation_starters,
            "topic_suggestions": topic_suggestions,
            "mood_indicators": mood_indicators,
            "dialogue_prompt": f"NPC dialogue should reflect {', '.join(mood_indicators[:2])} mood with topics about {', '.join(topic_suggestions[:2])}"
        } 