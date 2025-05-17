"""
Combat-related models and data structures.
"""

from typing import Dict, List, Optional, Any, Union, ClassVar
from dataclasses import dataclass, field
from sqlalchemy import Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.enums import DamageType
from datetime import datetime
import math

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

@dataclass
class DamageComposition:
    """
    Represents a composition of multiple damage types and their respective amounts.
    Example: {DamageType.FIRE: 10, DamageType.PHYSICAL: 5}
    """
    amounts: Dict[DamageType, float] = field(default_factory=dict)

    def add(self, damage_type: DamageType, amount: float) -> None:
        self.amounts[damage_type] = self.amounts.get(damage_type, 0) + amount

    def total(self) -> float:
        return sum(self.amounts.values())

    def serialize(self) -> Dict[str, Any]:
        return {dt.value: amt for dt, amt in self.amounts.items()}

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> 'DamageComposition':
        comp = DamageComposition()
        for k, v in data.items():
            comp.add(DamageType(k), v)
        return comp

    def __getitem__(self, damage_type: DamageType) -> float:
        return self.amounts.get(damage_type, 0)

    def __setitem__(self, damage_type: DamageType, amount: float) -> None:
        self.amounts[damage_type] = amount

    def __contains__(self, damage_type: DamageType) -> bool:
        return damage_type in self.amounts

    def items(self):
        return self.amounts.items()

    def copy(self) -> 'DamageComposition':
        return DamageComposition(amounts=self.amounts.copy())

    def combine(self, other: 'DamageComposition') -> 'DamageComposition':
        result = self.copy()
        for dt, amt in other.amounts.items():
            result.add(dt, amt)
        return result

    def is_empty(self) -> bool:
        return not self.amounts

class DamageEffectivenessMatrix:
    """
    Stores the effectiveness multipliers for each (attacker_type, defender_type) pair.
    Used to define type interactions (e.g., fire vs. ice = 2.0, fire vs. fire = 0.5).
    Supports serialization, deserialization, versioning, and application to DamageComposition.
    Designed for integration with designer tools and visual editors.
    """
    def __init__(self, matrix=None, version=1):
        # matrix: Dict[DamageType, Dict[DamageType, float]]
        self.matrix = matrix or {}
        self.version = version

    def set_effectiveness(self, attacker_type, defender_type, multiplier):
        if attacker_type not in self.matrix:
            self.matrix[attacker_type] = {}
        self.matrix[attacker_type][defender_type] = multiplier

    def get_effectiveness(self, attacker_type, defender_type):
        return self.matrix.get(attacker_type, {}).get(defender_type, 1.0)

    def serialize(self):
        # Convert to a JSON-serializable dict (use .value for enums)
        return {
            'version': self.version,
            'matrix': {
                atk.value if hasattr(atk, 'value') else str(atk): {
                    defn.value if hasattr(defn, 'value') else str(defn): mult
                    for defn, mult in defn_map.items()
                }
                for atk, defn_map in self.matrix.items()
            }
        }

    @classmethod
    def deserialize(cls, data):
        from app.core.enums import DamageType
        version = data.get('version', 1)
        matrix = {}
        for atk, defn_map in data['matrix'].items():
            atk_enum = DamageType(atk)
            matrix[atk_enum] = {}
            for defn, mult in defn_map.items():
                defn_enum = DamageType(defn)
                matrix[atk_enum][defn_enum] = mult
        return cls(matrix=matrix, version=version)

    def apply_to_composition(self, composition, defender_type):
        # Returns a new DamageComposition with effectiveness multipliers applied
        from app.core.models.combat import DamageComposition
        result = DamageComposition()
        for dt, amt in composition.amounts.items():
            mult = self.get_effectiveness(dt, defender_type)
            result.add(dt, amt * mult)
        return result

    def bump_version(self):
        self.version += 1

class ResistanceComponent:
    """
    Component for managing resistances and vulnerabilities for an entity.
    Supports:
    - Percentage-based resistance/vulnerability (e.g., 0.5 for 50% reduction, -0.2 for 20% vulnerability)
    - Flat reduction (e.g., -10 for -10 damage taken)
    - Permanent, temporary, and conditional resistances
    - Stacking and runtime modification
    """
    def __init__(self):
        # Structure: {damage_type: {"percent": [..], "flat": [..]}}
        self._resistances = {}
        self._vulnerabilities = {}
        self._temporary = []  # List of (damage_type, kind, value, duration)

    def add_resistance(self, damage_type: str, value: float, kind: str = "percent", duration: int = None):
        """Add a resistance. kind: 'percent' or 'flat'. duration=None for permanent."""
        if kind not in ("percent", "flat"):
            raise ValueError("kind must be 'percent' or 'flat'")
        if damage_type not in self._resistances:
            self._resistances[damage_type] = {"percent": [], "flat": []}
        self._resistances[damage_type][kind].append(value)
        if duration:
            self._temporary.append((damage_type, kind, value, duration))

    def add_vulnerability(self, damage_type: str, value: float, kind: str = "percent", duration: int = None):
        if kind not in ("percent", "flat"):
            raise ValueError("kind must be 'percent' or 'flat'")
        if damage_type not in self._vulnerabilities:
            self._vulnerabilities[damage_type] = {"percent": [], "flat": []}
        self._vulnerabilities[damage_type][kind].append(value)
        if duration:
            self._temporary.append((damage_type, kind, value, duration, True))

    def remove_resistance(self, damage_type: str, value: float, kind: str = "percent"):
        if damage_type in self._resistances and value in self._resistances[damage_type][kind]:
            self._resistances[damage_type][kind].remove(value)

    def remove_vulnerability(self, damage_type: str, value: float, kind: str = "percent"):
        if damage_type in self._vulnerabilities and value in self._vulnerabilities[damage_type][kind]:
            self._vulnerabilities[damage_type][kind].remove(value)

    def tick(self):
        """Reduce duration of temporary resistances, remove expired."""
        still_active = []
        for entry in self._temporary:
            if len(entry) == 4:
                damage_type, kind, value, duration = entry
                is_vuln = False
            else:
                damage_type, kind, value, duration, is_vuln = entry
            duration -= 1
            if duration > 0:
                still_active.append((damage_type, kind, value, duration) if not is_vuln else (damage_type, kind, value, duration, True))
            else:
                if is_vuln:
                    self.remove_vulnerability(damage_type, value, kind)
                else:
                    self.remove_resistance(damage_type, value, kind)
        self._temporary = still_active

    def get_total_resistance(self, damage_type: str) -> float:
        """Sum all percent resistances for a type (clamped 0-1)."""
        vals = self._resistances.get(damage_type, {"percent": []})["percent"]
        return max(0.0, min(1.0, sum(vals)))

    def get_total_flat_resistance(self, damage_type: str) -> float:
        vals = self._resistances.get(damage_type, {"flat": []})["flat"]
        return sum(vals)

    def get_total_vulnerability(self, damage_type: str) -> float:
        vals = self._vulnerabilities.get(damage_type, {"percent": []})["percent"]
        return max(0.0, sum(vals))

    def get_total_flat_vulnerability(self, damage_type: str) -> float:
        vals = self._vulnerabilities.get(damage_type, {"flat": []})["flat"]
        return sum(vals)

    def query(self, damage_type: str) -> Dict[str, float]:
        """Return all modifiers for a given type."""
        return {
            "percent_resistance": self.get_total_resistance(damage_type),
            "flat_resistance": self.get_total_flat_resistance(damage_type),
            "percent_vulnerability": self.get_total_vulnerability(damage_type),
            "flat_vulnerability": self.get_total_flat_vulnerability(damage_type),
        }

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
    """
    Engine for handling combat logic.
    All damage (attacks, spells, effects) is routed through the advanced DamageCalculator and event-driven pipeline.
    To extend or modify damage logic, register new pipeline modifiers or update the DamageCalculator configuration.
    Legacy direct damage logic is deprecated.
    """
    def __init__(self, combat_state: CombatState, status_system=None, battlefield=None, effectiveness_matrix=None):
        self.combat_state = combat_state
        self.participants = combat_state.participants
        self.status_system = status_system or StatusEffectsSystem()
        self.battlefield = battlefield or BattlefieldConditionsManager()
        self.damage_calculator = DamageCalculator(
            status_system=self.status_system,
            battlefield=self.battlefield,
            combat_stats_lookup=self._lookup_stats,
            effectiveness_matrix=effectiveness_matrix
        )

    def _lookup_stats(self, participant_id):
        # Find participant by ID and return their character/npc combat_stats
        p = next((p for p in self.participants if p.id == participant_id), None)
        if p:
            if p.character and hasattr(p.character, 'combat_stats'):
                return p.character.combat_stats
            elif p.npc and hasattr(p.npc, 'combat_stats'):
                return p.npc.combat_stats
        return None

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

        # --- Natural Language Action Handling ---
        if action.get('type') == 'natural_language':
            handler = CombatActionHandler(self.combat_state)
            result = handler.process_action(action)
            return result

        result = {
            'success': True,
            'actor_id': current_actor.id,
            'action': action,
            'effects': []
        }

        # Process action
        if action['type'] == 'attack':
            target = next(p for p in self.participants if p.id == action['target_id'])
            # Use new DamageCalculator for attack
            comp = None
            base_damage = action.get('damage', 0)
            damage_type = action.get('damage_type', DamageType.PHYSICAL)
            # Compose multi-type if bonus_damage present
            bonus_damage = action.get('bonus_damage', None)
            if bonus_damage:
                from app.core.models.combat import DamageComposition
                comp = DamageComposition()
                comp.add(damage_type, base_damage)
                for dt, amt in bonus_damage.items():
                    comp.add(dt, amt)
            else:
                comp = base_damage
            # Calculate damage using pipeline
            roll = self.damage_calculator.calculate_damage(
                attacker_id=current_actor.id,
                target_id=target.id,
                damage=comp,
                damage_type=damage_type
            )
            target.take_damage(roll.total_damage)
            result['effects'].append({
                'type': 'damage',
                'target_id': target.id,
                'amount': roll.total_damage,
                'composition': roll.composition.serialize() if hasattr(roll.composition, 'serialize') else roll.composition
            })
        elif action['type'] == 'spell':
            spell = self._get_spell(action['spell_id'])
            for effect in spell.effects:
                # If effect is damage, use pipeline
                if hasattr(effect, 'damage') and hasattr(effect, 'damage_type'):
                    target = current_actor  # Default to self if not specified
                    if hasattr(effect, 'target_id'):
                        target = next((p for p in self.participants if p.id == effect.target_id), current_actor)
                    comp = effect.damage
                    damage_type = effect.damage_type
                    roll = self.damage_calculator.calculate_damage(
                        attacker_id=current_actor.id,
                        target_id=target.id,
                        damage=comp,
                        damage_type=damage_type
                    )
                    target.take_damage(roll.total_damage)
                    result['effects'].append({
                        'type': 'damage',
                        'target_id': target.id,
                        'amount': roll.total_damage,
                        'composition': roll.composition.serialize() if hasattr(roll.composition, 'serialize') else roll.composition
                    })
                else:
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
        # Deprecated: use DamageCalculator instead
        base_damage = action.get('damage', 0)
        damage_type = action.get('damage_type', DamageType.PHYSICAL)
        comp = base_damage
        if 'bonus_damage' in action:
            from app.core.models.combat import DamageComposition
            comp = DamageComposition()
            comp.add(damage_type, base_damage)
            for dt, amt in action['bonus_damage'].items():
                comp.add(dt, amt)
        roll = self.damage_calculator.calculate_damage(
            attacker_id=attacker.id,
            target_id=action['target_id'],
            damage=comp,
            damage_type=damage_type
        )
        return roll.total_damage

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

    # Resistances and Vulnerabilities (per damage type, 0.0-1.0 for resist, 0.0+ for vuln)
    resistances = Column(JSON, default=dict)  # e.g., {"fire": 0.5, "cold": 0.2}
    vulnerabilities = Column(JSON, default=dict)  # e.g., {"fire": 0.5, "cold": 0.2}

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

    # New field
    resistance_component: ClassVar[Optional[ResistanceComponent]] = None

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

    def set_resistance(self, damage_type: str, value: float) -> None:
        if self.resistance_component:
            self.resistance_component.add_resistance(damage_type, value, kind="percent")
        else:
            if not self.resistances:
                self.resistances = {}
            self.resistances[damage_type] = value
        self.save()

    def get_resistance(self, damage_type: str) -> float:
        if self.resistance_component:
            return self.resistance_component.get_total_resistance(damage_type)
        if not self.resistances:
            return 0.0
        return float(self.resistances.get(damage_type, 0.0))

    def set_vulnerability(self, damage_type: str, value: float) -> None:
        if self.resistance_component:
            self.resistance_component.add_vulnerability(damage_type, value, kind="percent")
        else:
            if not self.vulnerabilities:
                self.vulnerabilities = {}
            self.vulnerabilities[damage_type] = value
        self.save()

    def get_vulnerability(self, damage_type: str) -> float:
        if self.resistance_component:
            return self.resistance_component.get_total_vulnerability(damage_type)
        if not self.vulnerabilities:
            return 0.0
        return float(self.vulnerabilities.get(damage_type, 0.0))

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
            'is_bleeding': self.is_bleeding,
            'resistances': self.resistances,
            'vulnerabilities': self.vulnerabilities
        }
        return {**base_dict, **combat_dict} 