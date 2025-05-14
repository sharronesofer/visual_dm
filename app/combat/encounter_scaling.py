from typing import List, Dict, Any
from enum import Enum
import random
import math
from app.core.rules.balance_constants import (
    MAX_LEVEL,
    BASE_AC,
    BASE_ATTACK_BONUS,
    BASE_HIT_DIE,
    CRITICAL_HIT_MULTIPLIER
)

class PartyRole(Enum):
    """Roles that characters can fill in a party."""
    TANK = "tank"
    DAMAGE = "damage"
    SUPPORT = "support"
    CONTROL = "control"

class EncounterDifficulty(Enum):
    """Difficulty levels for encounters."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"

class EncounterScaler:
    """
    Calculates encounter difficulty and dynamically adjusts encounters for balance.
    """
    def __init__(self):
        self.difficulty_multipliers = {
            EncounterDifficulty.EASY: 0.8,
            EncounterDifficulty.MEDIUM: 1.0,
            EncounterDifficulty.HARD: 1.2,
            EncounterDifficulty.DEADLY: 1.5
        }
        
        # Role-based enemy type preferences
        self.counter_roles = {
            PartyRole.TANK: [PartyRole.DAMAGE, PartyRole.CONTROL],
            PartyRole.DAMAGE: [PartyRole.TANK, PartyRole.SUPPORT],
            PartyRole.SUPPORT: [PartyRole.CONTROL, PartyRole.DAMAGE],
            PartyRole.CONTROL: [PartyRole.DAMAGE, PartyRole.SUPPORT]
        }

    def determine_party_roles(self, party: List[Dict[str, Any]]) -> Dict[PartyRole, int]:
        """
        Analyze party composition to determine role distribution.
        """
        roles = {role: 0 for role in PartyRole}
        
        for member in party:
            # Determine role based on stats and abilities
            hp_ratio = member.get('max_hp', 0) / (member.get('level', 1) * BASE_HIT_DIE)
            damage_ratio = member.get('damage_bonus', 0) / member.get('level', 1)
            support_abilities = len(member.get('support_abilities', []))
            control_abilities = len(member.get('control_abilities', []))
            
            # Score each role based on character attributes
            role_scores = {
                PartyRole.TANK: hp_ratio * 2 + member.get('armor_class', BASE_AC) / 15,
                PartyRole.DAMAGE: damage_ratio * 2 + member.get('attack_bonus', BASE_ATTACK_BONUS) / 10,
                PartyRole.SUPPORT: support_abilities / 3 + member.get('healing_bonus', 0) / 5,
                PartyRole.CONTROL: control_abilities / 3 + member.get('spell_dc', 10) / 15
            }
            
            # Assign primary role
            primary_role = max(role_scores.items(), key=lambda x: x[1])[0]
            roles[primary_role] += 1
            
        return roles

    def calculate_party_strength(self, party: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive party strength metrics.
        """
        if not party:
            return {"total": 0, "average_level": 0, "roles": {}}
            
        total_level = sum(member.get('level', 1) for member in party)
        avg_level = total_level / len(party)
        
        # Calculate role distribution
        roles = self.determine_party_roles(party)
        
        # Calculate offensive and defensive capabilities
        total_damage = sum(member.get('damage_bonus', 0) for member in party)
        total_hp = sum(member.get('max_hp', 0) for member in party)
        avg_ac = sum(member.get('armor_class', BASE_AC) for member in party) / len(party)
        
        return {
            "total": total_level,
            "average_level": avg_level,
            "roles": roles,
            "offensive_power": total_damage / len(party),
            "defensive_power": (total_hp / len(party)) * (avg_ac / BASE_AC)
        }

    def calculate_enemy_strength(self, enemies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive enemy strength metrics.
        """
        if not enemies:
            return {"total": 0, "average_level": 0, "roles": {}}
            
        total_level = sum(enemy.get('level', 1) for enemy in enemies)
        avg_level = total_level / len(enemies)
        
        # Calculate role distribution
        roles = self.determine_party_roles(enemies)  # Reuse party role logic for enemies
        
        # Calculate offensive and defensive capabilities
        total_damage = sum(enemy.get('damage_bonus', 0) for enemy in enemies)
        total_hp = sum(enemy.get('max_hp', 0) for enemy in enemies)
        avg_ac = sum(enemy.get('armor_class', BASE_AC) for enemy in enemies) / len(enemies)
        
        return {
            "total": total_level,
            "average_level": avg_level,
            "roles": roles,
            "offensive_power": total_damage / len(enemies),
            "defensive_power": (total_hp / len(enemies)) * (avg_ac / BASE_AC)
        }

    def recommend_adjustment(
        self,
        party: List[Dict[str, Any]],
        enemies: List[Dict[str, Any]],
        target_difficulty: EncounterDifficulty = EncounterDifficulty.MEDIUM
    ) -> Dict[str, Any]:
        """
        Recommend comprehensive encounter adjustments based on party composition and target difficulty.
        """
        party_metrics = self.calculate_party_strength(party)
        enemy_metrics = self.calculate_enemy_strength(enemies)
        
        # Calculate target metrics based on party strength and difficulty
        difficulty_mult = self.difficulty_multipliers[target_difficulty]
        target_enemy_power = party_metrics["offensive_power"] * difficulty_mult
        target_enemy_defense = party_metrics["defensive_power"] * difficulty_mult
        
        # Calculate needed adjustments
        power_diff = target_enemy_power - enemy_metrics["offensive_power"]
        defense_diff = target_enemy_defense - enemy_metrics["defensive_power"]
        
        # Determine role-based adjustments
        missing_counter_roles = []
        for role, count in party_metrics["roles"].items():
            if count > 0:
                # Check if we have enough enemies to counter this role
                counter_role_counts = sum(
                    enemy_metrics["roles"].get(counter_role, 0)
                    for counter_role in self.counter_roles[role]
                )
                if counter_role_counts < count:
                    missing_counter_roles.extend(self.counter_roles[role])
        
        # Build adjustment recommendations
        adjustments = {
            "add_enemies": [],
            "remove_enemies": 0,
            "modify_stats": {
                "hp": 1.0,
                "damage": 1.0,
                "armor_class": 1.0
            }
        }
        
        # Adjust enemy count
        if power_diff > 0 or defense_diff > 0:
            # Need more enemies
            num_new_enemies = math.ceil(max(power_diff, defense_diff) / 2)
            for _ in range(num_new_enemies):
                if missing_counter_roles:
                    role = random.choice(missing_counter_roles)
                    adjustments["add_enemies"].append({
                        "role": role,
                        "level": min(MAX_LEVEL, round(party_metrics["average_level"] * difficulty_mult))
                    })
        elif power_diff < -2 or defense_diff < -2:
            # Need fewer enemies
            adjustments["remove_enemies"] = math.ceil(abs(min(power_diff, defense_diff)) / 2)
            
        # Adjust enemy stats
        if len(enemies) > 0:
            hp_mult = max(0.5, min(2.0, target_enemy_defense / enemy_metrics["defensive_power"]))
            damage_mult = max(0.5, min(2.0, target_enemy_power / enemy_metrics["offensive_power"]))
            
            adjustments["modify_stats"] = {
                "hp": hp_mult,
                "damage": damage_mult,
                "armor_class": hp_mult ** 0.5  # Scale AC more conservatively
            }
            
        return adjustments

    def adjust_enemies(self, enemies: List[Dict[str, Any]], adjustment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply adjustments to the enemy list (add/remove/modify stats).
        """
        new_enemies = enemies.copy()
        
        # Remove enemies if needed
        if adjustment.get("remove_enemies", 0) > 0:
            remove_count = min(len(new_enemies) - 1, adjustment["remove_enemies"])
            new_enemies = new_enemies[:-remove_count] if remove_count > 0 else new_enemies
            
        # Add new enemies
        for enemy_template in adjustment.get("add_enemies", []):
            role = enemy_template["role"]
            level = enemy_template["level"]
            
            # Create enemy based on role
            new_enemy = {
                "name": f"Level {level} {role.value.title()}",
                "level": level,
                "role": role.value
            }
            
            # Adjust stats based on role
            if role == PartyRole.TANK:
                new_enemy.update({
                    "hp": level * BASE_HIT_DIE * 1.5,
                    "armor_class": BASE_AC + (level // 2),
                    "damage_bonus": level // 2
                })
            elif role == PartyRole.DAMAGE:
                new_enemy.update({
                    "hp": level * BASE_HIT_DIE * 0.8,
                    "armor_class": BASE_AC + (level // 4),
                    "damage_bonus": level
                })
            elif role == PartyRole.SUPPORT:
                new_enemy.update({
                    "hp": level * BASE_HIT_DIE,
                    "armor_class": BASE_AC + (level // 3),
                    "damage_bonus": level // 3,
                    "healing_bonus": level
                })
            elif role == PartyRole.CONTROL:
                new_enemy.update({
                    "hp": level * BASE_HIT_DIE * 0.9,
                    "armor_class": BASE_AC + (level // 3),
                    "damage_bonus": level // 2,
                    "spell_dc": 10 + (level // 2)
                })
                
            new_enemies.append(new_enemy)
            
        # Modify existing enemy stats
        if "modify_stats" in adjustment:
            stat_mods = adjustment["modify_stats"]
            for enemy in new_enemies:
                if "hp" in enemy:
                    enemy["hp"] = int(enemy["hp"] * stat_mods.get("hp", 1.0))
                if "damage_bonus" in enemy:
                    enemy["damage_bonus"] = int(enemy["damage_bonus"] * stat_mods.get("damage", 1.0))
                if "armor_class" in enemy:
                    enemy["armor_class"] = int(enemy["armor_class"] * stat_mods.get("armor_class", 1.0))
                    
        return new_enemies 