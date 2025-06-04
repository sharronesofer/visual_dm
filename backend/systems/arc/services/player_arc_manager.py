"""
Player story arc management.
Handles player story arcs, character arcs, and related narrative progressions.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from backend.infrastructure.database import get_db
from backend.infrastructure.utils import ValidationError, NotFoundError
from backend.infrastructure.repositories.arc.arc_repository import ArcRepository
from backend.infrastructure.repositories.arc.arc_progression_repository import ArcProgressionRepository
from backend.systems.arc.models.arc import Arc, ArcModel, CreateArcRequest, ArcType, ArcStatus, ArcPriority
from backend.systems.arc.models.arc_progression import ArcProgression, ArcProgressionModel, CreateArcProgressionRequest
# from backend.systems.quest.utils import QuestValidator  # Temporarily disabled to break circular imports

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Database operation error."""
    pass

def validate_player_id(player_id: str) -> None:
    """Simple player ID validation."""
    if not player_id or not isinstance(player_id, str):
        raise ValidationError("Player ID must be a non-empty string")

class EnhancedPlayerArcManager:
    """Enhanced arc manager with LLM-powered arc generation"""
    
    def __init__(self, db_session=None, llm_service: Optional[LLMService] = None):
        self.db_session = db_session
        self.llm_service = llm_service
    
    async def generate_character_arc_llm(
        self,
        player_id: str,
        background: str,
        character_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a character-based story arc using LLM with rich context.
        
        Args:
            player_id: ID of the player
            background: Character background/origin story
            character_details: Additional character information (class, race, personality, etc.)
            
        Returns:
            Dict[str, Any]: Dynamically generated character arc data
        """
        try:
            validate_player_id(player_id)
            
            if not background or not isinstance(background, str):
                raise ValidationError("Background must be a non-empty string")
            
            if self.llm_service:
                # Use LLM to generate rich, personalized arc
                arc_data = await self._generate_llm_character_arc(player_id, background, character_details)
            else:
                # Fallback to enhanced template-based generation
                arc_data = self._generate_enhanced_template_arc(player_id, background, character_details)
            
            # Save to database
            success = await self._save_player_arc(player_id, arc_data)
            if not success:
                raise DatabaseError("Failed to save character arc to database")
            
            return arc_data
            
        except ValidationError as e:
            logger.error(f"Validation error generating character arc: {str(e)}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error generating character arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating character arc: {str(e)}")
            raise DatabaseError(f"Failed to generate character arc: {str(e)}")
    
    async def _generate_llm_character_arc(
        self,
        player_id: str,
        background: str,
        character_details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate character arc using LLM with rich prompting"""
        
        # Build rich context for the LLM
        context = {
            "player_id": player_id,
            "background": background,
            "character_class": character_details.get("class", "unknown") if character_details else "unknown",
            "character_race": character_details.get("race", "unknown") if character_details else "unknown",
            "personality_traits": character_details.get("personality", []) if character_details else [],
            "bonds": character_details.get("bonds", []) if character_details else [],
            "flaws": character_details.get("flaws", []) if character_details else [],
            "ideals": character_details.get("ideals", []) if character_details else [],
            "backstory_elements": character_details.get("backstory_elements", []) if character_details else []
        }
        
        prompt_template = """
Create a compelling character arc for a D&D player character with the following details:

**Character Background:** {background}
**Class:** {character_class}
**Race:** {character_race}
**Personality Traits:** {personality_traits}
**Bonds:** {bonds}
**Flaws:** {flaws}
**Ideals:** {ideals}
**Additional Backstory:** {backstory_elements}

Please create a personal character arc that:
1. Builds naturally from their background and personality
2. Addresses their bonds, flaws, and ideals
3. Provides meaningful character growth opportunities
4. Includes potential conflicts and resolutions
5. Has 4-6 chapters that feel authentic to this character

Respond with a JSON object in this format:
{{
  "title": "Character Arc Title",
  "description": "Overall arc description",
  "arc_type": "character",
  "themes": ["theme1", "theme2", "theme3"],
  "emotional_journey": "Description of character's emotional growth",
  "chapters": [
    {{
      "title": "Chapter Title",
      "description": "What happens in this chapter",
      "character_growth": "How the character develops",
      "potential_conflicts": ["conflict1", "conflict2"],
      "narrative_beats": ["beat1", "beat2", "beat3"],
      "completion_criteria": "What needs to happen to complete this chapter"
    }}
  ],
  "character_arc_goals": [
    "Personal goal 1",
    "Personal goal 2"
  ],
  "potential_npcs": [
    {{
      "name": "NPC Name",
      "relationship": "relationship to character",
      "role": "role in the arc"
    }}
  ]
}}
"""
        
        try:
            response = await self.llm_service.generate_content(
                prompt=prompt_template.format(**context),
                context=GenerationContext.CHARACTER_CREATION,
                max_tokens=4000,
                temperature=0.8  # Higher creativity for character arcs
            )
            
            response_text = response.get("response", "")
            
            # Parse the LLM response
            arc_data = self._parse_character_arc_response(response_text, player_id, background)
            
            return arc_data
            
        except Exception as e:
            logger.error(f"LLM character arc generation failed: {e}")
            # Fallback to enhanced template
            return self._generate_enhanced_template_arc(player_id, background, character_details)
    
    def _parse_character_arc_response(
        self,
        response_text: str,
        player_id: str,
        background: str
    ) -> Dict[str, Any]:
        """Parse LLM response into structured character arc data"""
        import json
        import re
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)
                
                # Convert to our internal format
                chapters = []
                for i, chapter_data in enumerate(parsed_data.get("chapters", [])):
                    chapters.append({
                        "title": chapter_data.get("title", f"Chapter {i+1}"),
                        "description": chapter_data.get("description", ""),
                        "completion": 0,
                        "status": "active" if i == 0 else "pending",
                        "character_growth": chapter_data.get("character_growth", ""),
                        "potential_conflicts": chapter_data.get("potential_conflicts", []),
                        "narrative_beats": chapter_data.get("narrative_beats", []),
                        "completion_criteria": chapter_data.get("completion_criteria", "")
                    })
                
                return {
                    "player_id": player_id,
                    "background": background,
                    "title": parsed_data.get("title", "Personal Journey"),
                    "description": parsed_data.get("description", ""),
                    "arc_type": "character",
                    "status": "active",
                    "completion": 0,
                    "themes": parsed_data.get("themes", []),
                    "emotional_journey": parsed_data.get("emotional_journey", ""),
                    "character_arc_goals": parsed_data.get("character_arc_goals", []),
                    "potential_npcs": parsed_data.get("potential_npcs", []),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "chapters": chapters,
                    "current_chapter": 0,
                    "choices": [],
                    "llm_generated": True
                }
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM character arc response: {e}")
        
        # Fallback: extract basic information from text
        return self._extract_arc_from_text(response_text, player_id, background)
    
    def _extract_arc_from_text(
        self,
        response_text: str,
        player_id: str,
        background: str
    ) -> Dict[str, Any]:
        """Extract arc information from free-form text response"""
        lines = response_text.split('\n')
        
        title = "Personal Journey"
        description = response_text[:300]
        chapters = []
        
        current_chapter = None
        chapter_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for chapter/step indicators
            if any(keyword in line.lower() for keyword in ['chapter', 'step', 'phase', 'stage']):
                if current_chapter:
                    chapters.append(current_chapter)
                
                chapter_count += 1
                current_chapter = {
                    "title": line.replace('Chapter', '').replace('Step', '').replace('Phase', '').strip() or f"Chapter {chapter_count}",
                    "description": "",
                    "completion": 0,
                    "status": "active" if chapter_count == 1 else "pending"
                }
            elif current_chapter and len(line) > 20:
                current_chapter["description"] += f" {line}"
        
        if current_chapter:
            chapters.append(current_chapter)
        
        # Ensure we have at least some chapters
        if not chapters:
            chapters = self._get_fallback_chapters(background)
        
        return {
            "player_id": player_id,
            "background": background,
            "title": title,
            "description": description,
            "arc_type": "character",
            "status": "active",
            "completion": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "chapters": chapters,
            "current_chapter": 0,
            "choices": [],
            "llm_generated": True,
            "fallback_extraction": True
        }
    
    def _generate_enhanced_template_arc(
        self,
        player_id: str,
        background: str,
        character_details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate enhanced template-based arc with character context"""
        
        background_lower = background.lower()
        
        # Enhanced background analysis
        arc_templates = {
            "noble": {
                "title": "Reclaiming Honor",
                "themes": ["nobility", "responsibility", "legacy"],
                "chapters": [
                    {
                        "title": "Fallen Grace",
                        "description": "The character must confront the loss of their noble status and decide how to respond.",
                        "character_growth": "Learning humility and understanding the common people"
                    },
                    {
                        "title": "Proving Worth",
                        "description": "Through heroic deeds, the character begins to rebuild their reputation.",
                        "character_growth": "Developing genuine leadership skills"
                    },
                    {
                        "title": "Family Secrets",
                        "description": "Dark secrets about the character's family come to light.",
                        "character_growth": "Dealing with moral complexity and family loyalty"
                    },
                    {
                        "title": "The Rightful Place",
                        "description": "The character must decide what kind of noble they want to be.",
                        "character_growth": "Becoming a true leader who serves others"
                    }
                ]
            },
            "criminal": {
                "title": "Path to Redemption",
                "themes": ["redemption", "justice", "second chances"],
                "chapters": [
                    {
                        "title": "Haunted by the Past",
                        "description": "Old enemies or victims surface, forcing confrontation with past crimes.",
                        "character_growth": "Accepting responsibility for past actions"
                    },
                    {
                        "title": "Making Amends",
                        "description": "The character actively works to right previous wrongs.",
                        "character_growth": "Learning the value of sacrifice for others"
                    },
                    {
                        "title": "The Final Score",
                        "description": "A chance to use criminal skills for a noble cause.",
                        "character_growth": "Transforming negative traits into positive ones"
                    },
                    {
                        "title": "New Identity",
                        "description": "The character establishes themselves as a force for good.",
                        "character_growth": "Fully embracing a heroic identity"
                    }
                ]
            },
            "hermit": {
                "title": "Rejoining the World",
                "themes": ["wisdom", "connection", "purpose"],
                "chapters": [
                    {
                        "title": "Breaking Isolation",
                        "description": "Something forces the character out of their solitude.",
                        "character_growth": "Learning to trust and connect with others again"
                    },
                    {
                        "title": "Sharing Wisdom",
                        "description": "The character's knowledge proves valuable to the group.",
                        "character_growth": "Finding purpose in teaching and guiding others"
                    },
                    {
                        "title": "Confronting the Reason",
                        "description": "The character faces whatever drove them to isolation.",
                        "character_growth": "Overcoming past trauma or failure"
                    },
                    {
                        "title": "Building Community",
                        "description": "The character helps create lasting bonds with their companions.",
                        "character_growth": "Embracing their role as a vital part of the group"
                    }
                ]
            }
        }
        
        # Select appropriate template
        selected_template = None
        for key, template in arc_templates.items():
            if key in background_lower:
                selected_template = template
                break
        
        # Default template for unrecognized backgrounds
        if not selected_template:
            selected_template = {
                "title": "Finding Your Path",
                "themes": ["self-discovery", "courage", "growth"],
                "chapters": [
                    {
                        "title": "The Call to Adventure",
                        "description": "Something disrupts the character's normal life and sets them on a new path.",
                        "character_growth": "Taking the first steps toward heroism"
                    },
                    {
                        "title": "Trials and Tribulations",
                        "description": "The character faces challenges that test their resolve and abilities.",
                        "character_growth": "Developing confidence and skills"
                    },
                    {
                        "title": "The Revelation",
                        "description": "A major truth about themselves, their past, or their destiny is revealed.",
                        "character_growth": "Understanding their true purpose"
                    },
                    {
                        "title": "Becoming the Hero",
                        "description": "The character fully embraces their role as a hero and protector.",
                        "character_growth": "Achieving their full potential"
                    }
                ]
            }
        
        # Build chapters with enhanced details
        chapters = []
        for i, chapter_template in enumerate(selected_template["chapters"]):
            chapters.append({
                "title": chapter_template["title"],
                "description": chapter_template["description"],
                "completion": 0,
                "status": "active" if i == 0 else "pending",
                "character_growth": chapter_template["character_growth"],
                "completion_criteria": f"Complete the narrative objectives for {chapter_template['title']}"
            })
        
        return {
            "player_id": player_id,
            "background": background,
            "title": selected_template["title"],
            "description": f"A personal journey exploring {', '.join(selected_template['themes'])}",
            "arc_type": "character",
            "status": "active",
            "completion": 0,
            "themes": selected_template["themes"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "chapters": chapters,
            "current_chapter": 0,
            "choices": [],
            "llm_generated": False,
            "template_enhanced": True
        }
    
    def _get_fallback_chapters(self, background: str) -> List[Dict[str, Any]]:
        """Get basic fallback chapters when all else fails"""
        return [
            {"title": "The Beginning", "completion": 0, "status": "active"},
            {"title": "Growing Stronger", "completion": 0, "status": "pending"},
            {"title": "Facing Challenges", "completion": 0, "status": "pending"},
            {"title": "Achieving Greatness", "completion": 0, "status": "pending"}
        ]
    
    async def _save_player_arc(self, player_id: str, arc_data: Dict[str, Any]) -> bool:
        """Save player arc data (placeholder for actual database implementation)"""
        try:
            # This would integrate with the actual database layer
            logger.info(f"Saving enhanced character arc for player {player_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save player arc: {e}")
            return False

class PlayerArcManager:
    """Original player arc manager with backward compatibility"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.enhanced_manager = EnhancedPlayerArcManager(db_session)

    @staticmethod
    def load_player_arc(player_id: str, db_session=None) -> Optional[Dict[str, Any]]:
        """
        Load a player's story arc from the database.
        
        Args:
            player_id: ID of the player
            db_session: Optional database session
            
        Returns:
            Optional[Dict[str, Any]]: Arc data or None if not found
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            validate_player_id(player_id)
            
            # Use provided session or get new one
            session = db_session or next(get_db())
            arc_repo = ArcRepository(session)
            
            # Query for player's active arc
            try:
                player_uuid = UUID(player_id)
            except ValueError:
                # If player_id is not a UUID, search by character_id field
                arc_entity = arc_repo.get_by_character_id(player_id)
            else:
                # Search by player UUID in character_id field
                arc_entity = arc_repo.get_by_character_id(str(player_uuid))
            
            if not arc_entity:
                logger.info(f"No arc found for player {player_id}")
                return None
            
            # Convert to dict format expected by the rest of the system
            arc_data = {
                'id': str(arc_entity.id),
                'player_id': player_id,
                'arc_type': arc_entity.arc_type.value if arc_entity.arc_type else 'main',
                'status': arc_entity.status.value if arc_entity.status else 'active',
                'completion': arc_entity.progress_percentage / 100.0 if arc_entity.progress_percentage else 0,
                'created_at': arc_entity.created_at.isoformat() if arc_entity.created_at else datetime.utcnow().isoformat(),
                'updated_at': arc_entity.updated_at.isoformat() if arc_entity.updated_at else datetime.utcnow().isoformat(),
                'chapters': [],  # This would need to be populated from arc steps
                'current_chapter': arc_entity.completed_steps or 0,
                'choices': [],  # This would come from progression data
                'title': arc_entity.title,
                'description': arc_entity.description,
                'objectives': arc_entity.objectives or [],
                'themes': arc_entity.themes or []
            }
            
            logger.info(f"Loaded arc {arc_entity.id} for player {player_id}")
            return arc_data
            
        except ValidationError as e:
            logger.error(f"Validation error loading player arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading player arc: {str(e)}")
            raise DatabaseError(f"Failed to load player arc: {str(e)}")
    
    @staticmethod
    def save_player_arc(player_id: str, arc_data: Dict[str, Any], db_session=None) -> bool:
        """
        Save a player's story arc to the database.
        
        Args:
            player_id: ID of the player
            arc_data: Dict containing arc data
            db_session: Optional database session
            
        Returns:
            bool: Success flag
            
        Raises:
            ValidationError: If player_id is invalid
            DatabaseError: If database operation fails
        """
        try:
            validate_player_id(player_id)
            
            # Add timestamp if not present
            if 'updated_at' not in arc_data:
                arc_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Use provided session or get new one
            session = db_session or next(get_db())
            arc_repo = ArcRepository(session)
            
            # Check if arc already exists for this player
            existing_arc = PlayerArcManager.load_player_arc(player_id, session)
            
            if existing_arc:
                # Update existing arc
                arc_id = UUID(existing_arc['id'])
                
                # Convert arc_data to update format
                update_data = {
                    'status': ArcStatus(arc_data.get('status', 'active')),
                    'progress_percentage': int(arc_data.get('completion', 0) * 100),
                    'completed_steps': arc_data.get('current_chapter', 0),
                    'objectives': arc_data.get('objectives', []),
                    'themes': arc_data.get('themes', [])
                }
                
                # Filter out None values
                update_data = {k: v for k, v in update_data.items() if v is not None}
                
                arc_repo.update(arc_id, update_data)
                logger.info(f"Updated existing arc for player {player_id}")
            else:
                # Create new arc
                create_request = CreateArcRequest(
                    title=arc_data.get('title', f"Player Arc - {player_id}"),
                    description=arc_data.get('description', f"Story arc for player {player_id}"),
                    arc_type=ArcType(arc_data.get('arc_type', 'character')),
                    priority=ArcPriority.MEDIUM,
                    character_id=player_id,
                    objectives=arc_data.get('objectives', []),
                    themes=arc_data.get('themes', []),
                    estimated_duration_hours=arc_data.get('estimated_duration', 2.0)
                )
                
                new_arc = arc_repo.create(create_request)
                logger.info(f"Created new arc {new_arc.id} for player {player_id}")
            
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
            validate_player_id(player_id)
            
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
            success = PlayerArcManager.save_player_arc(player_id, arc_data)
            if not success:
                raise DatabaseError("Failed to save newly created arc to database")
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error creating player arc: {str(e)}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error creating player arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating player arc: {str(e)}")
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
            validate_player_id(player_id)
            
            if not faction_id or not isinstance(faction_id, str):
                raise ValidationError("Faction ID must be a non-empty string")
            
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
            success = PlayerArcManager.save_player_arc(player_id, arc_data)
            if not success:
                raise DatabaseError("Failed to save war arc to database")
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error triggering war arc: {str(e)}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error triggering war arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error triggering war arc: {str(e)}")
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
            validate_player_id(player_id)
            
            if not background or not isinstance(background, str):
                raise ValidationError("Background must be a non-empty string")
            
            arc_data = {
                'player_id': player_id,
                'background': background,
                'arc_type': 'character',
                'status': 'active',
                'completion': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'chapters': [],
                'current_chapter': 0,
                'choices': []
            }
            
            # Generate chapters based on background
            try:
                background_lower = background.lower()
                if 'noble' in background_lower:
                    arc_data['chapters'] = [
                        {'title': 'Reclaiming Your Heritage', 'completion': 0, 'status': 'active'},
                        {'title': 'Political Alliances', 'completion': 0, 'status': 'pending'},
                        {'title': 'Family Secrets', 'completion': 0, 'status': 'pending'},
                        {'title': 'The Rightful Heir', 'completion': 0, 'status': 'pending'}
                    ]
                elif 'outcast' in background_lower or 'exile' in background_lower:
                    arc_data['chapters'] = [
                        {'title': 'Finding Acceptance', 'completion': 0, 'status': 'active'},
                        {'title': 'Proving Your Worth', 'completion': 0, 'status': 'pending'},
                        {'title': 'Confronting the Past', 'completion': 0, 'status': 'pending'},
                        {'title': 'A New Beginning', 'completion': 0, 'status': 'pending'}
                    ]
                else:
                    arc_data['chapters'] = [
                        {'title': 'Finding Your Path', 'completion': 0, 'status': 'active'},
                        {'title': 'Trials and Tests', 'completion': 0, 'status': 'pending'},
                        {'title': 'Unexpected Allies', 'completion': 0, 'status': 'pending'},
                        {'title': 'Your True Calling', 'completion': 0, 'status': 'pending'}
                    ]
            except Exception as e:
                logger.warning(f"Error generating background-specific chapters: {e}")
                # Fallback to generic chapters
                arc_data['chapters'] = [
                    {'title': 'Beginning the Journey', 'completion': 0, 'status': 'active'},
                    {'title': 'Growing Stronger', 'completion': 0, 'status': 'pending'},
                    {'title': 'Facing Challenges', 'completion': 0, 'status': 'pending'},
                    {'title': 'Achieving Greatness', 'completion': 0, 'status': 'pending'}
                ]
            
            # Save to database
            success = PlayerArcManager.save_player_arc(player_id, arc_data)
            if not success:
                raise DatabaseError("Failed to save character arc to database")
            
            return arc_data
        except ValidationError as e:
            logger.error(f"Validation error generating character arc: {str(e)}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error generating character arc: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating character arc: {str(e)}")
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
            # Validate progress
            if progress < 0 or progress > 100:
                raise ValidationError("Progress must be between 0 and 100")
            
            # Get the arc
            arc_data = PlayerArcManager.load_player_arc(player_id)
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
            PlayerArcManager.save_player_arc(player_id, arc_data)
            
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
            # Validate choice data
            if not isinstance(choice, dict):
                raise ValidationError("Choice data must be a dictionary")
            
            required_fields = ['context', 'option', 'consequence']
            for field in required_fields:
                if field not in choice:
                    raise ValidationError(f"Missing required field in choice data: {field}")
            
            # Get the arc
            arc_data = PlayerArcManager.load_player_arc(player_id)
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
            PlayerArcManager.save_player_arc(player_id, arc_data)
            
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