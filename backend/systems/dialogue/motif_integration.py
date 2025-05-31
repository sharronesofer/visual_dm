"""
Motif integration for dialogue system.

Provides integration between dialogue processing and motif systems
for tracking narrative themes and story elements.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DialogueMotifIntegration:
    """
    Integration layer between dialogue and motif systems.
    
    Handles tracking narrative motifs in dialogue, identifying themes,
    and managing story element progression.
    """
    
    def __init__(self, motif_manager=None):
        """
        Initialize dialogue motif integration.
        
        Args:
            motif_manager: Optional motif manager instance
        """
        self.motif_manager = motif_manager
        self.motif_cache = {}
        
    def extract_motifs_from_dialogue(
        self,
        dialogue_text: str,
        speaker_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract narrative motifs from dialogue text.
        
        Args:
            dialogue_text: Text to analyze for motifs
            speaker_id: ID of the speaker
            context: Optional context information
            
        Returns:
            List of extracted motifs
        """
        try:
            # Simple keyword-based motif detection
            motif_patterns = {
                'heroism': ['brave', 'courage', 'hero', 'noble', 'sacrifice'],
                'betrayal': ['betray', 'deceive', 'backstab', 'treachery'],
                'love': ['love', 'romance', 'heart', 'affection', 'beloved'],
                'revenge': ['revenge', 'vengeance', 'payback', 'retribution'],
                'mystery': ['mystery', 'secret', 'hidden', 'unknown', 'puzzle'],
                'power': ['power', 'control', 'dominance', 'authority', 'rule']
            }
            
            motifs = []
            text_lower = dialogue_text.lower()
            
            for motif_type, keywords in motif_patterns.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        motifs.append({
                            "type": motif_type,
                            "keyword": keyword,
                            "content": dialogue_text,
                            "speaker_id": speaker_id,
                            "confidence": 0.6,
                            "context": context or {}
                        })
                        break  # Only one motif per type per dialogue
            
            return motifs
            
        except Exception as e:
            logger.error(f"Failed to extract motifs from dialogue: {e}")
            return []
    
    def track_motif_progression(
        self,
        motif_data: Dict[str, Any],
        character_id: str
    ) -> bool:
        """
        Track progression of a motif for a character.
        
        Args:
            motif_data: Motif information
            character_id: Character ID
            
        Returns:
            True if tracked successfully
        """
        try:
            if self.motif_manager:
                return self.motif_manager.track_progression(motif_data, character_id)
            
            # Fallback: store in cache
            cache_key = f"{character_id}:{motif_data.get('type', 'unknown')}"
            if cache_key not in self.motif_cache:
                self.motif_cache[cache_key] = []
            
            self.motif_cache[cache_key].append(motif_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track motif progression: {e}")
            return False
    
    def get_character_motifs(
        self,
        character_id: str,
        motif_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get motifs associated with a character.
        
        Args:
            character_id: Character ID
            motif_type: Optional motif type filter
            
        Returns:
            List of character motifs
        """
        try:
            if self.motif_manager:
                return self.motif_manager.get_character_motifs(character_id, motif_type)
            
            # Fallback: return from cache
            character_motifs = []
            for cache_key, motifs in self.motif_cache.items():
                if character_id in cache_key:
                    if motif_type is None or motif_type in cache_key:
                        character_motifs.extend(motifs)
            
            return character_motifs
            
        except Exception as e:
            logger.error(f"Failed to get character motifs: {e}")
            return [] 