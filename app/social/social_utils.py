"""
Social interaction and relationship utility functions.
"""

from typing import Dict, List, Optional, Union, Any
import random
from app.rules.calculation_utils import calculate_save_dc
from app.social.social_models import SocialInteraction, CharacterRelationship
from app.core.database import db
from app.core.utils.error_utils import ValidationError, NotFoundError

def update_relationship(relationship: CharacterRelationship) -> Dict[str, Any]:
    """Update a relationship between characters."""
    try:
        db.session.add(relationship)
        db.session.commit()
        return {
            'success': True,
            'relationship_id': relationship.id,
            'status': get_relationship_status(relationship)
        }
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Error updating relationship: {str(e)}")

def get_relationship_status(relationship: CharacterRelationship) -> Dict[str, Any]:
    """Get the current status of a relationship."""
    return {
        'relationship_type': relationship.relationship_type,
        'trust_level': relationship.trust_level,
        'respect_level': relationship.respect_level
    }

def process_social_interaction(interaction: SocialInteraction) -> Dict[str, Any]:
    """Process a social interaction between characters."""
    try:
        db.session.add(interaction)
        db.session.commit()
        
        # Update or create relationship
        relationship = CharacterRelationship.query.filter_by(
            character_id=interaction.character_id,
            target_id=interaction.target_id
        ).first()
        
        if not relationship:
            relationship = CharacterRelationship(
                character_id=interaction.character_id,
                target_id=interaction.target_id,
                relationship_type='neutral'
            )
            db.session.add(relationship)
        
        # Update relationship based on interaction
        update_relationship_from_interaction(relationship, interaction)
        db.session.commit()
        
        return {
            'success': True,
            'interaction_id': interaction.id,
            'relationship_status': get_relationship_status(relationship)
        }
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Error processing interaction: {str(e)}")

def update_relationship_from_interaction(relationship: CharacterRelationship, interaction: SocialInteraction) -> None:
    """Update relationship metrics based on an interaction."""
    # Define interaction type effects
    interaction_effects = {
        'greeting': {'trust': 1, 'respect': 0},
        'help': {'trust': 2, 'respect': 1},
        'trade': {'trust': 1, 'respect': 1},
        'quest': {'trust': 0, 'respect': 2},
        'hostile': {'trust': -2, 'respect': -1}
    }
    
    if interaction.interaction_type in interaction_effects:
        effects = interaction_effects[interaction.interaction_type]
        relationship.trust_level = max(-100, min(100, relationship.trust_level + effects['trust']))
        relationship.respect_level = max(-100, min(100, relationship.respect_level + effects['respect']))

class SocialInteraction:
    def __init__(self, npc_id: str, relationship_status: str = "neutral"):
        self.npc_id = npc_id
        self.relationship_status = relationship_status  # "ally", "neutral", "enemy"
        self.base_dc = 10
        self.modifiers = {
            "relationship": {
                "ally": -5,
                "neutral": 0,
                "enemy": 5
            },
            "request_difficulty": {
                "very_easy": -2,
                "easy": -1,
                "moderate": 0,
                "hard": 2,
                "very_hard": 5
            },
            "circumstances": {
                "favorable": -2,
                "neutral": 0,
                "unfavorable": 2
            },
            "evidence_leverage": {
                "strong": -2,
                "moderate": -1,
                "none": 0,
                "against": 2
            }
        }

    def calculate_dc(self, 
                    request_difficulty: str,
                    circumstances: str,
                    evidence_leverage: str) -> int:
        """Calculate the final DC for a social interaction."""
        dc = self.base_dc
        dc += self.modifiers["relationship"][self.relationship_status]
        dc += self.modifiers["request_difficulty"][request_difficulty]
        dc += self.modifiers["circumstances"][circumstances]
        dc += self.modifiers["evidence_leverage"][evidence_leverage]
        return max(5, min(30, dc))  # Clamp between 5 and 30

    def perform_social_check(self,
                           character: Dict,
                           skill: str,
                           dc: int,
                           advantage: bool = False,
                           disadvantage: bool = False) -> Dict:
        """Perform a social skill check with optional advantage/disadvantage."""
        # Get character's relevant ability score
        ability = "CHA"  # Default for social skills
        ability_score = character.get(ability, 10)
        
        # Calculate modifier
        modifier = (ability_score - 10) // 2
        
        # Add proficiency bonus if character has the skill
        if skill.lower() in [s.lower() for s in character.get("skills", [])]:
            modifier += 2
            
        # Roll the check
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20) if (advantage or disadvantage) else None
        
        if advantage:
            roll = max(roll1, roll2)
        elif disadvantage:
            roll = min(roll1, roll2)
        else:
            roll = roll1
            
        total = roll + modifier
        success = total >= dc
        
        return {
            "skill": skill,
            "roll": roll,
            "roll2": roll2 if roll2 else None,
            "modifier": modifier,
            "total": total,
            "dc": dc,
            "success": success,
            "margin": total - dc
        }

    def get_interaction_result(self,
                             character: Dict,
                             skill: str,
                             request_difficulty: str,
                             circumstances: str,
                             evidence_leverage: str,
                             advantage: bool = False,
                             disadvantage: bool = False) -> Dict:
        """Get the complete result of a social interaction."""
        dc = self.calculate_dc(request_difficulty, circumstances, evidence_leverage)
        check_result = self.perform_social_check(
            character, skill, dc, advantage, disadvantage
        )
        
        # Determine degree of success/failure
        margin = check_result["margin"]
        if check_result["success"]:
            if margin >= 10:
                degree = "critical_success"
            elif margin >= 5:
                degree = "great_success"
            else:
                degree = "success"
        else:
            if margin <= -10:
                degree = "critical_failure"
            elif margin <= -5:
                degree = "great_failure"
            else:
                degree = "failure"
                
        check_result["degree"] = degree
        return check_result 