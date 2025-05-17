from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from app.core.enums import DamageType
from app.combat.damage_engine import AttackType

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    IMPORTANT = "important"
    CRITICAL = "critical"

class LogCategory(Enum):
    INITIATIVE = "initiative"
    ATTACK = "attack"
    DAMAGE = "damage"
    EFFECT = "effect"
    MOVEMENT = "movement"
    ENVIRONMENT = "environment"
    SYSTEM = "system"

@dataclass
class CombatLogEntry:
    timestamp: datetime
    category: LogCategory
    level: LogLevel
    message: str
    details: Dict
    round_number: int
    turn_number: int
    actor_id: Optional[str] = None
    target_id: Optional[str] = None

class CombatLogger:
    def __init__(self, combat_id: str, db):
        self.combat_id = combat_id
        self.db = db
        self.log_collection = db.collection('combat_logs')
        self.current_round = 1
        self.current_turn = 1
        self.statistics: Dict = self._initialize_statistics()

    def _initialize_statistics(self) -> Dict:
        """Initialize combat statistics tracking."""
        return {
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'critical_hits': 0,
            'misses': 0,
            'effects_applied': 0,
            'healing_done': 0,
            'rounds_elapsed': 0,
            'turns_elapsed': 0,
            'damage_by_type': {dtype.value: 0 for dtype in DamageType},
            'attacks_by_type': {atype.value: 0 for atype in AttackType},
            'participant_stats': {}
        }

    def log_initiative(self, actor_id: str, roll: int, modifiers: Dict[str, int], 
                      final_value: int) -> None:
        """Log an initiative roll."""
        self._create_log_entry(
            category=LogCategory.INITIATIVE,
            level=LogLevel.INFO,
            message=f"Initiative roll for {actor_id}",
            details={
                'roll': roll,
                'modifiers': modifiers,
                'final_value': final_value
            },
            actor_id=actor_id
        )

    def log_attack(self, attacker_id: str, defender_id: str, attack_type: AttackType,
                   roll: int, modifiers: Dict[str, int], success: bool, 
                   critical: bool = False) -> None:
        """Log an attack attempt."""
        self._create_log_entry(
            category=LogCategory.ATTACK,
            level=LogLevel.IMPORTANT,
            message=f"Attack from {attacker_id} against {defender_id}",
            details={
                'attack_type': attack_type.value,
                'roll': roll,
                'modifiers': modifiers,
                'success': success,
                'critical': critical
            },
            actor_id=attacker_id,
            target_id=defender_id
        )
        
        # Update statistics
        self.statistics['attacks_by_type'][attack_type.value] += 1
        if critical:
            self.statistics['critical_hits'] += 1
        elif not success:
            self.statistics['misses'] += 1

    def log_damage(self, attacker_id: str, defender_id: str, 
                   damage_result: 'DamageResult') -> None:
        """Log damage dealt in combat."""
        self._create_log_entry(
            category=LogCategory.DAMAGE,
            level=LogLevel.IMPORTANT,
            message=f"Damage dealt by {attacker_id} to {defender_id}",
            details={
                'raw_damage': damage_result.raw_damage,
                'final_damage': damage_result.final_damage,
                'damage_type': damage_result.damage_type.value,
                'critical': damage_result.critical,
                'absorbed_damage': damage_result.absorbed_damage,
                'damage_reduction': damage_result.damage_reduction,
                'hit_location': damage_result.hit_location
            },
            actor_id=attacker_id,
            target_id=defender_id
        )
        
        # Update statistics
        self.statistics['total_damage_dealt'] += damage_result.final_damage
        self.statistics['damage_by_type'][damage_result.damage_type.value] += damage_result.final_damage
        
        # Update participant statistics
        if attacker_id not in self.statistics['participant_stats']:
            self.statistics['participant_stats'][attacker_id] = {'damage_dealt': 0}
        if defender_id not in self.statistics['participant_stats']:
            self.statistics['participant_stats'][defender_id] = {'damage_taken': 0}
            
        self.statistics['participant_stats'][attacker_id]['damage_dealt'] += damage_result.final_damage
        self.statistics['participant_stats'][defender_id]['damage_taken'] += damage_result.final_damage

    def log_effect(self, source_id: str, target_id: str, effect: str, 
                   duration: int, is_applied: bool) -> None:
        """Log application or removal of status effects."""
        action = "applied to" if is_applied else "removed from"
        self._create_log_entry(
            category=LogCategory.EFFECT,
            level=LogLevel.INFO,
            message=f"Effect {effect} {action} {target_id}",
            details={
                'effect': effect,
                'duration': duration,
                'is_applied': is_applied
            },
            actor_id=source_id,
            target_id=target_id
        )
        
        if is_applied:
            self.statistics['effects_applied'] += 1

    def log_movement(self, actor_id: str, start_position: Dict[str, int],
                     end_position: Dict[str, int], movement_type: str) -> None:
        """Log character movement during combat."""
        self._create_log_entry(
            category=LogCategory.MOVEMENT,
            level=LogLevel.DEBUG,
            message=f"Movement by {actor_id}",
            details={
                'start_position': start_position,
                'end_position': end_position,
                'movement_type': movement_type
            },
            actor_id=actor_id
        )

    def log_environment_change(self, condition: str, affected_area: Dict,
                              duration: Optional[int] = None) -> None:
        """Log changes in battlefield conditions."""
        self._create_log_entry(
            category=LogCategory.ENVIRONMENT,
            level=LogLevel.INFO,
            message=f"Environmental condition change: {condition}",
            details={
                'condition': condition,
                'affected_area': affected_area,
                'duration': duration
            }
        )

    def start_round(self) -> None:
        """Start a new combat round."""
        self._create_log_entry(
            category=LogCategory.SYSTEM,
            level=LogLevel.IMPORTANT,
            message=f"Starting Round {self.current_round}",
            details={}
        )
        self.statistics['rounds_elapsed'] += 1

    def start_turn(self, actor_id: str) -> None:
        """Start a new turn for a character."""
        self._create_log_entry(
            category=LogCategory.SYSTEM,
            level=LogLevel.INFO,
            message=f"Starting Turn for {actor_id}",
            details={'actor_id': actor_id},
            actor_id=actor_id
        )
        self.statistics['turns_elapsed'] += 1

    def end_combat(self, winner_id: Optional[str] = None, 
                   reason: str = "normal") -> None:
        """Log the end of combat."""
        self._create_log_entry(
            category=LogCategory.SYSTEM,
            level=LogLevel.CRITICAL,
            message="Combat Ended",
            details={
                'winner_id': winner_id,
                'reason': reason,
                'final_statistics': self.statistics
            }
        )

    def get_combat_log(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve combat log entries with optional filtering."""
        query = self.log_collection.where('combat_id', '==', self.combat_id)
        
        if filters:
            if 'category' in filters:
                query = query.where('category', '==', filters['category'])
            if 'level' in filters:
                query = query.where('level', '==', filters['level'])
            if 'actor_id' in filters:
                query = query.where('actor_id', '==', filters['actor_id'])
            if 'round_number' in filters:
                query = query.where('round_number', '==', filters['round_number'])
                
        return [doc.to_dict() for doc in query.stream()]

    def get_statistics(self) -> Dict:
        """Get current combat statistics."""
        return self.statistics

    def _create_log_entry(self, category: LogCategory, level: LogLevel,
                         message: str, details: Dict,
                         actor_id: Optional[str] = None,
                         target_id: Optional[str] = None) -> None:
        """Create and store a new log entry."""
        entry = CombatLogEntry(
            timestamp=datetime.utcnow(),
            category=category,
            level=level,
            message=message,
            details=details,
            round_number=self.current_round,
            turn_number=self.current_turn,
            actor_id=actor_id,
            target_id=target_id
        )
        
        # Convert to dictionary for storage
        entry_dict = {
            'combat_id': self.combat_id,
            'timestamp': entry.timestamp,
            'category': entry.category.value,
            'level': entry.level.value,
            'message': entry.message,
            'details': entry.details,
            'round_number': entry.round_number,
            'turn_number': entry.turn_number,
            'actor_id': entry.actor_id,
            'target_id': entry.target_id
        }
        
        # Store in database
        self.log_collection.add(entry_dict) 