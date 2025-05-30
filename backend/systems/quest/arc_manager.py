"""
Player story arc management.
Handles player story arcs, character arcs, and related narrative progressions.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from backend.core.utils.firebase_utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from backend.core.utils.error import ValidationError, NotFoundError, DatabaseError
from .utils import QuestValidator

logger = logging.getLogger(__name__)


class ArcManager:
    """Manages player story arcs and narrative progressions."""
    
    @staticmethod
    def load_player_arc(player_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a player's story arc from the database.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Optional[Dict[str, Any]]: Arc data or None if not found
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            arc_data = get_document(f"player_arcs/{player_id}")
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error loading player arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading player arc: {str(e)}")
            raise DatabaseError(f"Failed to load player arc: {str(e)}")
    
    @staticmethod
    def save_player_arc(player_id: str, arc_data: Dict[str, Any]) -> bool:
        """
        Save a player's story arc to the database.
        
        Args:
            player_id: ID of the player
            arc_data: Dict containing arc data
            
        Returns:
            bool: Success flag
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            # Add timestamp if not present
            if 'updated_at' not in arc_data:
                arc_data['updated_at'] = datetime.utcnow().isoformat()
                
            # Save to database
            set_document(f"player_arcs/{player_id}", arc_data)
            
            return True
        except ValidationError as e:
            logger.error(f"Validation error saving player arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error saving player arc: {str(e)}")
            raise DatabaseError(f"Failed to save player arc: {str(e)}")
    
    @staticmethod
    def create_player_arc(player_id: str) -> Dict[str, Any]:
        """
        Create a default story arc for a player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            Dict[str, Any]: Created story arc data
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            arc_data = {
                'player_id': player_id,
                'arc_type': 'main',
                'status': 'active',
                'completion': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'chapters': [],
                'current_chapter': 0,
                'choices': []
            }
            
            # Save to database
            ArcManager.save_player_arc(player_id, arc_data)
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error creating player arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating player arc: {str(e)}")
            raise DatabaseError(f"Failed to create player arc: {str(e)}")
    
    @staticmethod
    def trigger_war_arc(player_id: str, faction_id: str) -> Dict[str, Any]:
        """
        Trigger a war-themed story arc for a player.
        
        Args:
            player_id: ID of the player
            faction_id: ID of the faction involved in the war
            
        Returns:
            Dict[str, Any]: War arc data
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            arc_data = {
                'player_id': player_id,
                'faction_id': faction_id,
                'arc_type': 'war',
                'status': 'active',
                'completion': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'chapters': [
                    {'title': 'The Call to Arms', 'completion': 0, 'status': 'active'},
                    {'title': 'Gathering Forces', 'completion': 0, 'status': 'pending'},
                    {'title': 'The First Battle', 'completion': 0, 'status': 'pending'},
                    {'title': 'Strategic Decisions', 'completion': 0, 'status': 'pending'},
                    {'title': 'The Final Confrontation', 'completion': 0, 'status': 'pending'}
                ],
                'current_chapter': 0,
                'choices': []
            }
            
            # Save to database
            ArcManager.save_player_arc(player_id, arc_data)
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error triggering war arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error triggering war arc: {str(e)}")
            raise DatabaseError(f"Failed to trigger war arc: {str(e)}")
    
    @staticmethod
    def generate_character_arc(player_id: str, background: str) -> Dict[str, Any]:
        """
        Generate a character-based story arc for a player based on their background.
        
        Args:
            player_id: ID of the player
            background: Character background/origin story
            
        Returns:
            Dict[str, Any]: Character arc data
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            # Generate chapters based on background
            chapters = []
            if 'noble' in background.lower():
                chapters = [
                    {'title': 'Reclaiming Your Heritage', 'completion': 0, 'status': 'active'},
                    {'title': 'Political Alliances', 'completion': 0, 'status': 'pending'},
                    {'title': 'Family Secrets', 'completion': 0, 'status': 'pending'},
                    {'title': 'The Rightful Heir', 'completion': 0, 'status': 'pending'}
                ]
            elif 'outcast' in background.lower() or 'exile' in background.lower():
                chapters = [
                    {'title': 'Finding Acceptance', 'completion': 0, 'status': 'active'},
                    {'title': 'Proving Your Worth', 'completion': 0, 'status': 'pending'},
                    {'title': 'Confronting the Past', 'completion': 0, 'status': 'pending'},
                    {'title': 'A New Beginning', 'completion': 0, 'status': 'pending'}
                ]
            else:
                chapters = [
                    {'title': 'Finding Your Path', 'completion': 0, 'status': 'active'},
                    {'title': 'Trials and Tests', 'completion': 0, 'status': 'pending'},
                    {'title': 'Unexpected Allies', 'completion': 0, 'status': 'pending'},
                    {'title': 'Your True Calling', 'completion': 0, 'status': 'pending'}
                ]
            
            arc_data = {
                'player_id': player_id,
                'background': background,
                'arc_type': 'character',
                'status': 'active',
                'completion': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'chapters': chapters,
                'current_chapter': 0,
                'choices': []
            }
            
            # Save to database
            ArcManager.save_player_arc(player_id, arc_data)
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error generating character arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating character arc: {str(e)}")
            raise DatabaseError(f"Failed to generate character arc: {str(e)}")
    
    @staticmethod
    def update_arc_progress(player_id: str, chapter_index: int, progress: int) -> Dict[str, Any]:
        """
        Update the progress of a specific chapter in the player's story arc.
        
        Args:
            player_id: ID of the player
            chapter_index: Index of the chapter to update
            progress: Progress percentage (0-100)
            
        Returns:
            Dict[str, Any]: Updated arc data
            
        Raises:
            ValidationError: If player_id is invalid or progress is out of range
            NotFoundError: If arc or chapter not found
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            # Validate progress
            if progress < 0 or progress > 100:
                raise ValidationError("Progress must be between 0 and 100")
            
            # Get the arc
            arc_data = ArcManager.load_player_arc(player_id)
            if not arc_data:
                raise NotFoundError(f"Arc for player {player_id} not found")
            
            # Check if the chapter exists
            chapters = arc_data.get('chapters', [])
            if chapter_index < 0 or chapter_index >= len(chapters):
                raise ValidationError(f"Chapter index {chapter_index} out of range")
            
            # Update the chapter progress
            chapters[chapter_index]['completion'] = progress
            
            # Mark as completed if progress is 100%
            if progress == 100:
                chapters[chapter_index]['status'] = 'completed'
                
                # Advance to next chapter if available
                if chapter_index + 1 < len(chapters):
                    chapters[chapter_index + 1]['status'] = 'active'
                    arc_data['current_chapter'] = chapter_index + 1
                else:
                    # Mark arc as completed if all chapters are done
                    arc_data['status'] = 'completed'
            
            # Calculate overall arc completion
            if chapters:
                total_completion = sum(chapter.get('completion', 0) for chapter in chapters)
                arc_data['completion'] = total_completion // len(chapters)
            
            # Update the arc
            arc_data['updated_at'] = datetime.utcnow().isoformat()
            arc_data['chapters'] = chapters
            ArcManager.save_player_arc(player_id, arc_data)
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error updating arc progress: {str(e)}")
            raise
        except NotFoundError as e:
            logger.error(f"Not found error updating arc progress: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error updating arc progress: {str(e)}")
            raise DatabaseError(f"Failed to update arc progress: {str(e)}")
    
    @staticmethod
    def record_arc_choice(player_id: str, choice: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a narrative choice made by the player in their story arc.
        
        Args:
            player_id: ID of the player
            choice: Dict containing choice data
            
        Returns:
            Dict[str, Any]: Updated arc data
            
        Raises:
            ValidationError: If player_id is invalid or choice data is invalid
            NotFoundError: If arc not found
            DatabaseError: If database operation fails
        """
        try:
            QuestValidator.validate_player_id(player_id)
            
            # Validate choice data
            if not isinstance(choice, dict):
                raise ValidationError("Choice data must be a dictionary")
            
            required_fields = ['context', 'option', 'consequence']
            for field in required_fields:
                if field not in choice:
                    raise ValidationError(f"Missing required field in choice data: {field}")
            
            # Get the arc
            arc_data = ArcManager.load_player_arc(player_id)
            if not arc_data:
                raise NotFoundError(f"Arc for player {player_id} not found")
            
            # Add timestamp to choice
            choice['timestamp'] = datetime.utcnow().isoformat()
            
            # Add choice to arc data
            if 'choices' not in arc_data:
                arc_data['choices'] = []
                
            arc_data['choices'].append(choice)
            
            # Update the arc
            arc_data['updated_at'] = datetime.utcnow().isoformat()
            ArcManager.save_player_arc(player_id, arc_data)
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error recording arc choice: {str(e)}")
            raise
        except NotFoundError as e:
            logger.error(f"Not found error recording arc choice: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error recording arc choice: {str(e)}")
            raise DatabaseError(f"Failed to record arc choice: {str(e)}") 