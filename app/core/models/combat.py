"""
Combat-related models and data structures.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy import Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import db
from app.core.models.base import BaseModel
from app.hexmap.tactical_hex_grid import TacticalHexGrid

"""
Consolidated Combat models.
Provides a single authoritative definition for combat-related classes in the game.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from app.hexmap.tactical_hex_grid import TacticalHexGrid
import math

class CombatState(db.Model):
    """Model for tracking combat state."""
    __tablename__ = 'combat_states'

    id = Column(Integer, primary_key=True)
    combat_id = Column(Integer, ForeignKey('combats.id'), nullable=False)
    round_number = Column(Integer, default=1)
    current_turn = Column(Integer, default=0)
    initiative_order = Column(JSON, default=list)
    status = Column(String(50), default='active')  # active, completed, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    combat = relationship('Combat', back_populates='state')
    participants = relationship('CombatParticipant', back_populates='combat_state')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initiative_order = kwargs.get('initiative_order', [])

    def to_dict(self) -> Dict:
        """Convert combat state to dictionary representation."""
        return {
            'id': self.id,
            'combat_id': self.combat_id,
            'round_number': self.round_number,
            'current_turn': self.current_turn,
            'initiative_order': self.initiative_order,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def next_turn(self) -> None:
        """Advance to the next turn in combat."""
        self.current_turn = (self.current_turn + 1) % len(self.initiative_order)
        if self.current_turn == 0:
            self.round_number += 1
        self.updated_at = datetime.utcnow()

    def get_current_actor(self) -> Optional['CombatParticipant']:
        """Get the participant whose turn it is."""
        if not self.initiative_order:
            return None
        current_id = self.initiative_order[self.current_turn]
        return next((p for p in self.participants if p.id == current_id), None)

class CombatParticipant(db.Model):
    """Model for participants in combat."""
    __tablename__ = 'combat_participants'

    id = Column(Integer, primary_key=True)
    combat_state_id = Column(Integer, ForeignKey('combat_states.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'))
    npc_id = Column(Integer, ForeignKey('npcs.id'))
    initiative = Column(Integer, default=0)
    current_health = Column(Integer, default=0)
    current_mana = Column(Integer, default=0)
    position_q = Column(Integer, default=0)  # q coordinate in hex grid
    position_r = Column(Integer, default=0)  # r coordinate in hex grid
    facing = Column(Integer, default=0)      # Direction facing (0-5 for hex sides)
    status_effects = Column(JSON, default=list)
    used_opportunity_attack = Column(Boolean, default=False)  # Track if opportunity attack was used this round
    reach = Column(Integer, default=1)  # Attack reach in hex cells
    movement_points = Column(Integer)
    action_points = Column(Integer)
    bonus_action_available = Column(Boolean, default=True)
    reaction_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    combat_id = Column(Integer, ForeignKey('combats.id'), nullable=True)

    # Relationships
    combat_state = relationship('CombatState', back_populates='participants')
    character = relationship('Character')
    npc = relationship('NPC')
    combat = relationship('Combat', back_populates='participants')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_effects = kwargs.get('status_effects', [])

    def to_dict(self) -> Dict:
        """Convert combat participant to dictionary representation."""
        return {
            'id': self.id,
            'combat_state_id': self.combat_state_id,
            'character_id': self.character_id,
            'npc_id': self.npc_id,
            'initiative': self.initiative,
            'current_health': self.current_health,
            'current_mana': self.current_mana,
            'position_q': self.position_q,
            'position_r': self.position_r,
            'facing': self.facing,
            'status_effects': self.status_effects,
            'used_opportunity_attack': self.used_opportunity_attack,
            'reach': self.reach,
            'movement_points': self.movement_points,
            'action_points': self.action_points,
            'bonus_action_available': self.bonus_action_available,
            'reaction_available': self.reaction_available,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def take_damage(self, amount: int) -> None:
        """Apply damage to this participant."""
        self.current_health = max(0, self.current_health - amount)
        self.updated_at = datetime.utcnow()

    def heal(self, amount: int) -> None:
        """Apply healing to this participant."""
        if self.character:
            max_health = self.character.max_health
        else:
            max_health = self.npc.max_health
        self.current_health = min(max_health, self.current_health + amount)
        self.updated_at = datetime.utcnow()

    def add_status_effect(self, effect: str, duration: int) -> None:
        """Add a status effect to this participant."""
        self.status_effects.append({
            'name': effect,
            'duration': duration,
            'applied_at': datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()

    def remove_status_effect(self, effect: str) -> None:
        """Remove a status effect from this participant."""
        self.status_effects = [e for e in self.status_effects if e['name'] != effect]
        self.updated_at = datetime.utcnow()

    @property
    def name(self) -> str:
        """Get participant name."""
        return self.character.name if self.character else self.npc.name

    @property
    def position(self) -> tuple[int, int]:
        """Get position as tuple."""
        return (self.position_q, self.position_r)

    @position.setter
    def position(self, pos: tuple[int, int]) -> None:
        """Set position from tuple."""
        self.position_q, self.position_r = pos

    def move_to(self, q: int, r: int) -> None:
        """Move participant to new position."""
        self.position_q = q
        self.position_r = r

    def face_towards(self, target_q: int, target_r: int) -> None:
        """Update facing to look towards a position."""
        # Calculate angle and convert to hex side (0-5)
        dx = target_q - self.position_q
        dy = target_r - self.position_r
        angle = math.atan2(dy, dx)
        self.facing = int(((angle + math.pi) * 3 / math.pi) % 6)

    def reset_round(self) -> None:
        """Reset per-round attributes."""
        self.used_opportunity_attack = False
        self.reaction_available = True
        self.bonus_action_available = True
        self.movement_points = self.get_base_movement()
        self.action_points = self.get_base_actions()

    def get_base_movement(self) -> int:
        """Get base movement points, considering equipment and abilities."""
        base = 6  # Default movement range
        if self.character:
            # Add character-specific modifiers
            base += getattr(self.character, 'movement_bonus', 0)
            
        # Apply status effect modifiers
        if self.status_effects:
            for effect in self.status_effects:
                if effect.get('type') == 'slowed':
                    base = max(1, base // 2)
                elif effect.get('type') == 'hasted':
                    base *= 2
        
        return base

    def get_base_actions(self) -> int:
        """Get base action points, considering equipment and abilities."""
        base = 1  # Default action points
        if self.character:
            # Add character-specific modifiers
            base += getattr(self.character, 'action_bonus', 0)
            
        # Apply status effect modifiers
        if self.status_effects:
            for effect in self.status_effects:
                if effect.get('type') == 'hasted':
                    base += 1
                elif effect.get('type') == 'stunned':
                    base = 0
        
        return base

    def can_make_opportunity_attack(self) -> bool:
        """Check if the participant can make an opportunity attack."""
        if self.used_opportunity_attack or not self.reaction_available:
            return False
            
        # Check if any status effects prevent opportunity attacks
        if self.status_effects:
            for effect in self.status_effects:
                if effect.get('type') in ['stunned', 'incapacitated', 'defeated']:
                    return False
                    
        return True

    def use_opportunity_attack(self) -> None:
        """Mark that an opportunity attack has been used this round."""
        self.used_opportunity_attack = True
        self.reaction_available = False

class CombatEngine:
    """Engine for handling combat logic."""
    
    def __init__(self, combat_state: CombatState):
        self.combat_state = combat_state
        self.participants = combat_state.participants

    def roll_initiative(self) -> None:
        """Roll initiative for all participants."""
        for participant in self.participants:
            participant.initiative = self._roll_d20() + self._get_dex_modifier(participant)
        self.combat_state.initiative_order = sorted(
            [p.id for p in self.participants],
            key=lambda pid: next(p.initiative for p in self.participants if p.id == pid),
            reverse=True
        )
        self.combat_state.updated_at = datetime.utcnow()

    def process_turn(self, action: Dict) -> Dict:
        """Process a combat turn."""
        current_actor = self.combat_state.get_current_actor()
        if not current_actor:
            return {'error': 'No current actor'}

        result = {
            'success': True,
            'actor_id': current_actor.id,
            'action': action,
            'effects': []
        }

        # Process action
        if action['type'] == 'attack':
            target = next(p for p in self.participants if p.id == action['target_id'])
            damage = self._calculate_damage(current_actor, action)
            target.take_damage(damage)
            result['effects'].append({
                'type': 'damage',
                'target_id': target.id,
                'amount': damage
            })
        elif action['type'] == 'spell':
            spell = self._get_spell(action['spell_id'])
            for effect in spell.effects:
                effect_result = effect.apply(current_actor)
                result['effects'].append(effect_result)

        # Advance turn
        self.combat_state.next_turn()

        return result

    def _roll_d20(self) -> int:
        """Roll a d20 die."""
        import random
        return random.randint(1, 20)

    def _get_dex_modifier(self, participant: CombatParticipant) -> int:
        """Get dexterity modifier for a participant."""
        if participant.character:
            return (participant.character.dexterity - 10) // 2
        else:
            return (participant.npc.dexterity - 10) // 2

    def _calculate_damage(self, attacker: CombatParticipant, action: Dict) -> int:
        """Calculate damage for an attack."""
        base_damage = action.get('damage', 0)
        if self._roll_d20() == 20:  # Critical hit
            base_damage *= 2
        return base_damage

    def _get_spell(self, spell_id: int) -> 'Spell':
        """Get a spell by ID."""
        from app.core.models.spell import Spell
        return Spell.query.get(spell_id)

class Combat(BaseModel):
    """Model for active combat encounters."""
    __tablename__ = 'combats'
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default='active')  # active, completed, aborted
    initiative_order: Mapped[List[int]] = mapped_column(JSON, default=list)  # List of participant IDs in initiative order
    current_turn: Mapped[int] = mapped_column(Integer, default=0)  # Index in initiative_order
    environment: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # Environmental conditions
    effects: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # Active effects
    log: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)  # Combat log
    tactical_grid_data: Mapped[Optional[str]] = mapped_column(JSON)  # Serialized grid data
    
    # Foreign Keys
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id', use_alter=True, name='fk_combat_location'), nullable=False)
    
    # Relationships
    location = relationship('Location', back_populates='combats', foreign_keys=[location_id])
    participants = relationship('CombatParticipant', back_populates='combat', cascade='all, delete-orphan', foreign_keys='CombatParticipant.combat_id')
    actions = relationship('CombatAction', back_populates='combat', cascade='all, delete-orphan', foreign_keys='CombatAction.combat_id')
    state = relationship('CombatState', back_populates='combat', uselist=False)
    
    @property
    def tactical_grid(self) -> Optional[TacticalHexGrid]:
        """Get the tactical grid for this combat."""
        if not self.tactical_grid_data:
            return None
        return TacticalHexGrid.from_json(self.tactical_grid_data)

    def set_tactical_grid(self, grid: TacticalHexGrid) -> None:
        """Set the tactical grid for this combat."""
        self.tactical_grid_data = grid.to_json()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'round_number': self.round_number,
            'status': self.status,
            'initiative_order': self.initiative_order,
            'current_turn': self.current_turn,
            'environment': self.environment,
            'effects': self.effects,
            'log': self.log,
            'tactical_grid': self.tactical_grid.to_dict() if self.tactical_grid else None,
            'location_id': self.location_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CombatAction(BaseModel):
    """Model representing an action taken during combat."""
    __tablename__ = 'combat_actions'
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    combat_id: Mapped[int] = mapped_column(Integer, ForeignKey('combats.id', use_alter=True, name='fk_combat_action_combat'), nullable=False)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey('combat_participants.id', use_alter=True, name='fk_combat_action_actor'), nullable=False)
    target_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('combat_participants.id', use_alter=True, name='fk_combat_action_target'))
    action_name: Mapped[str] = mapped_column(String(100))
    damage_dealt: Mapped[Optional[int]] = mapped_column(Integer)
    healing_done: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships
    combat = relationship('Combat', back_populates='actions', foreign_keys=[combat_id])
    actor = relationship('CombatParticipant', foreign_keys=[actor_id])
    target = relationship('CombatParticipant', foreign_keys=[target_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'combat_id': self.combat_id,
            'actor_id': self.actor_id,
            'target_id': self.target_id,
            'action_name': self.action_name,
            'damage_dealt': self.damage_dealt,
            'healing_done': self.healing_done,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CombatStats(BaseModel):
    """
    Represents combat statistics for characters and NPCs
    """
    __tablename__ = 'combat_stats'

    # Basic Stats
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    stamina = Column(Integer, default=100)
    max_stamina = Column(Integer, default=100)
    mana = Column(Integer, default=100)
    max_mana = Column(Integer, default=100)

    # Combat Attributes
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Combat Skills
    melee_attack = Column(Integer, default=0)
    ranged_attack = Column(Integer, default=0)
    magic_attack = Column(Integer, default=0)
    physical_defense = Column(Integer, default=0)
    magic_defense = Column(Integer, default=0)
    dodge = Column(Integer, default=0)
    critical_chance = Column(Float, default=0.05)
    critical_damage = Column(Float, default=1.5)

    # Status
    is_in_combat = Column(Boolean, default=False)
    is_stunned = Column(Boolean, default=False)
    is_poisoned = Column(Boolean, default=False)
    is_bleeding = Column(Boolean, default=False)

    # Relationships
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    character = relationship("Character", back_populates="combat_stats")
    npc_id = Column(Integer, ForeignKey('npcs.id'), nullable=True)
    npc = relationship("NPC", back_populates="combat_stats", foreign_keys=[npc_id])

    def heal(self, amount: int) -> int:
        """
        Heal the entity by the specified amount
        Returns the actual amount healed
        """
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        actual_heal = self.health - old_health
        self.save()
        return actual_heal

    def take_damage(self, amount: int) -> int:
        """
        Deal damage to the entity
        Returns the actual amount of damage dealt
        """
        old_health = self.health
        self.health = max(self.health - amount, 0)
        actual_damage = old_health - self.health
        self.save()
        return actual_damage

    def use_stamina(self, amount: int) -> bool:
        """
        Use stamina for an action
        Returns True if there was enough stamina, False otherwise
        """
        if self.stamina >= amount:
            self.stamina -= amount
            self.save()
            return True
        return False

    def use_mana(self, amount: int) -> bool:
        """
        Use mana for a spell
        Returns True if there was enough mana, False otherwise
        """
        if self.mana >= amount:
            self.mana -= amount
            self.save()
            return True
        return False

    def is_alive(self) -> bool:
        """Check if the entity is alive"""
        return self.health > 0

    def reset_combat_state(self):
        """Reset combat-related states"""
        self.is_in_combat = False
        self.is_stunned = False
        self.is_poisoned = False
        self.is_bleeding = False
        self.save()

    def to_dict(self) -> Dict[str, Any]:
        """Convert combat stats to dictionary"""
        base_dict = super().to_dict()
        combat_dict = {
            'health': self.health,
            'max_health': self.max_health,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'melee_attack': self.melee_attack,
            'ranged_attack': self.ranged_attack,
            'magic_attack': self.magic_attack,
            'physical_defense': self.physical_defense,
            'magic_defense': self.magic_defense,
            'dodge': self.dodge,
            'critical_chance': self.critical_chance,
            'critical_damage': self.critical_damage,
            'is_in_combat': self.is_in_combat,
            'is_stunned': self.is_stunned,
            'is_poisoned': self.is_poisoned,
            'is_bleeding': self.is_bleeding
        }
        return {**base_dict, **combat_dict} 