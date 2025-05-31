"""
Rumor integration for dialogue system.

Provides integration between dialogue processing and rumor systems
for spreading information and managing narrative elements.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DialogueRumorIntegration:
    """
    Integration layer between dialogue and rumor systems.
    
    Handles spreading rumors through dialogue, tracking rumor propagation,
    and managing narrative information flow.
    """
    
    def __init__(self, rumor_manager=None):
        """
        Initialize dialogue rumor integration.
        
        Args:
            rumor_manager: Optional rumor manager instance
        """
        self.rumor_manager = rumor_manager
        self.rumor_cache = {}
        
    def extract_rumors_from_dialogue(
        self,
        dialogue_text: str,
        speaker_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract potential rumors from dialogue text.
        
        Args:
            dialogue_text: Text to analyze for rumors
            speaker_id: ID of the speaker
            context: Optional context information
            
        Returns:
            List of extracted rumors
        """
        try:
            # Simple keyword-based rumor detection
            rumor_keywords = [
                'heard', 'rumor', 'gossip', 'whisper', 'secret', 'told me',
                'they say', 'word is', 'apparently', 'supposedly'
            ]
            
            rumors = []
            text_lower = dialogue_text.lower()
            
            for keyword in rumor_keywords:
                if keyword in text_lower:
                    rumors.append({
                        "content": dialogue_text,
                        "speaker_id": speaker_id,
                        "keyword": keyword,
                        "confidence": 0.5,  # Basic confidence score
                        "context": context or {}
                    })
                    break  # Only one rumor per dialogue for simplicity
            
            return rumors
            
        except Exception as e:
            logger.error(f"Failed to extract rumors from dialogue: {e}")
            return []
    
    def propagate_rumor(
        self,
        rumor_data: Dict[str, Any],
        target_audience: List[str]
    ) -> bool:
        """
        Propagate a rumor to target audience.
        
        Args:
            rumor_data: Rumor information
            target_audience: List of target IDs
            
        Returns:
            True if propagated successfully
        """
        try:
            if self.rumor_manager:
                return self.rumor_manager.propagate_rumor(rumor_data, target_audience)
            
            # Fallback: store in cache
            rumor_id = f"rumor_{len(self.rumor_cache)}"
            self.rumor_cache[rumor_id] = {
                **rumor_data,
                "targets": target_audience,
                "propagated": True
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to propagate rumor: {e}")
            return False
    
    def get_relevant_rumors(
        self,
        character_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get rumors relevant to a character.
        
        Args:
            character_id: Character ID
            context: Optional context for filtering
            
        Returns:
            List of relevant rumors
        """
        try:
            if self.rumor_manager:
                return self.rumor_manager.get_rumors_for_character(character_id, context)
            
            # Fallback: return from cache
            relevant_rumors = []
            for rumor_id, rumor_data in self.rumor_cache.items():
                if character_id in rumor_data.get("targets", []):
                    relevant_rumors.append(rumor_data)
            
            return relevant_rumors
            
        except Exception as e:
            logger.error(f"Failed to get relevant rumors: {e}")
            return [] 