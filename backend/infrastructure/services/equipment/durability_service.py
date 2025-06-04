"""
Durability Service

Centralized service for all equipment durability management including
time-based degradation, combat damage, environmental wear, and repair calculations.
This service consolidates previously scattered durability logic.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import random
import json
import os
from pathlib import Path

from backend.systems.equipment.models.equipment_quality import (
    EquipmentQuality, QualityConfig, get_quality_stats
)

logger = logging.getLogger(__name__)

class DurabilityService:
    """Centralized service for managing all aspects of equipment durability"""
    
    # Durability status thresholds
    DURABILITY_THRESHOLDS = {
        "perfect": 100.0,
        "excellent": 90.0,
        "good": 75.0,
        "worn": 50.0,
        "damaged": 25.0,
        "very_damaged": 10.0,
        "broken": 0.0
    }

    # Stat penalty multipliers by condition
    STAT_PENALTY_MULTIPLIERS = {
        "perfect": 0.0,      # No penalty
        "excellent": 0.0,    # No penalty
        "good": 0.0,         # No penalty
        "worn": 0.1,         # 10% stat reduction
        "damaged": 0.25,     # 25% stat reduction
        "very_damaged": 0.5, # 50% stat reduction
        "broken": 1.0        # 100% penalty (unusable)
    }

    # Combat damage base rates by equipment type
    COMBAT_DAMAGE_BASE = {
        "weapon": 0.5,      # Weapons take damage on hit
        "armor": 0.2,       # Armor takes damage when hit
        "shield": 0.3,      # Shields take damage when blocking
        "accessory": 0.1    # Accessories take minimal damage
    }

    # Environmental wear factors
    ENVIRONMENTAL_FACTORS = {
        "normal": 1.0,
        "humid": 1.2,
        "dry": 0.8,
        "extreme_cold": 1.5,
        "extreme_heat": 1.3
    }
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logger
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from JSON file"""
        config_path = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "repair" / "repair_config.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.ENVIRONMENTAL_FACTORS = config.get("environmental_factors", {
                    "normal": 1.0,
                    "humid": 1.2,
                    "dry": 0.8,
                    "extreme_cold": 1.5,
                    "extreme_heat": 1.3
                })
                self.integration_triggers = config.get("integration_triggers", {})
        except FileNotFoundError:
            # Fallback to hardcoded values if config file not found
            self.ENVIRONMENTAL_FACTORS = {
                "normal": 1.0,
                "humid": 1.2,
                "dry": 0.8,
                "extreme_cold": 1.5,
                "extreme_heat": 1.3
            }
            self.integration_triggers = {}
    
    # ==========================================
    # TIME-BASED DEGRADATION
    # ==========================================
    
    def calculate_time_degradation(
        self, 
        equipment_id: str,
        quality: EquipmentQuality,
        last_update: datetime,
        usage_intensity: float = 1.0,
        environment: str = "normal"
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate comprehensive time-based durability degradation.
        
        Args:
            equipment_id: ID of the equipment
            quality: Quality level of the equipment
            last_update: When durability was last calculated
            usage_intensity: Multiplier for usage (1.0 = normal, 2.0 = heavy use)
            environment: Environmental conditions affecting wear
            
        Returns:
            Tuple of (decay_amount, degradation_details)
        """
        now = datetime.utcnow()
        time_diff = now - last_update
        
        # Get daily decay rate for this quality
        daily_decay_rate = QualityConfig.calculate_decay_rate(quality)
        
        # Calculate base decay based on time passed
        days_passed = time_diff.total_seconds() / (24 * 3600)
        base_decay = daily_decay_rate * days_passed
        
        # Apply usage intensity modifier
        usage_decay = base_decay * usage_intensity
        
        # Apply environmental modifier
        env_factor = self.ENVIRONMENTAL_FACTORS.get(environment, 1.0)
        environmental_decay = usage_decay * env_factor
        
        # Add some randomness to make degradation feel more natural
        randomness_factor = random.uniform(0.8, 1.2)
        total_decay = environmental_decay * randomness_factor
        
        # Cap at 100% decay
        final_decay = min(total_decay, 100.0)
        
        degradation_details = {
            "time_passed_days": round(days_passed, 2),
            "base_decay_rate": daily_decay_rate,
            "usage_intensity": usage_intensity,
            "environment": environment,
            "environmental_factor": env_factor,
            "randomness_factor": randomness_factor,
            "total_decay": round(final_decay, 2)
        }
        
        self.logger.debug(
            f"Equipment {equipment_id}: {days_passed:.2f} days passed, "
            f"total decay: {final_decay:.2f}% (base: {base_decay:.2f}, "
            f"usage: {usage_intensity}, env: {env_factor})"
        )
        
        return final_decay, degradation_details

    # ==========================================
    # COMBAT DEGRADATION
    # ==========================================
    
    def calculate_combat_degradation(
        self, 
        equipment_type: str,
        combat_intensity: float = 1.0,
        is_critical: bool = False,
        damage_taken: float = 0.0,
        blocks_made: int = 0
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate durability damage from combat usage.
        
        Args:
            equipment_type: Type of equipment (weapon, armor, shield, accessory)
            combat_intensity: Multiplier for combat intensity (1.0 is normal)
            is_critical: Whether this was a critical hit (more damage)
            damage_taken: Amount of damage taken (for armor)
            blocks_made: Number of blocks made (for shields)
            
        Returns:
            Tuple of (damage_amount, combat_details)
        """
        base_damage = self.COMBAT_DAMAGE_BASE.get(equipment_type, 0.2)
        
        # Add randomness for realistic variation
        damage = base_damage * random.uniform(0.8, 1.2)
        
        # Apply combat intensity
        damage *= combat_intensity
        
        # Apply critical hit bonus for weapons
        if is_critical and equipment_type == "weapon":
            damage *= 2.0
        
        # Additional damage for armor based on damage taken
        if equipment_type == "armor" and damage_taken > 0:
            armor_stress = damage_taken * 0.05  # 5% of damage taken
            damage += armor_stress
        
        # Additional damage for shields based on blocks
        if equipment_type == "shield" and blocks_made > 0:
            shield_stress = blocks_made * 0.2  # 0.2 durability per block
            damage += shield_stress
        
        combat_details = {
            "equipment_type": equipment_type,
            "base_damage": base_damage,
            "combat_intensity": combat_intensity,
            "is_critical": is_critical,
            "damage_taken": damage_taken,
            "blocks_made": blocks_made,
            "total_damage": round(damage, 2)
        }
        
        return round(damage, 2), combat_details

    # ==========================================
    # ENVIRONMENTAL DEGRADATION
    # ==========================================
    
    def calculate_environmental_degradation(
        self,
        equipment_type: str,
        environment: str,
        exposure_hours: float = 1.0,
        equipment_material: str = "metal"
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate durability damage from environmental exposure.
        
        Args:
            equipment_type: Type of equipment
            environment: Environmental conditions
            exposure_hours: Hours of exposure
            equipment_material: Material composition
            
        Returns:
            Tuple of (damage_amount, environment_details)
        """
        # Base environmental damage rates
        base_rates = {
            "weapon": 0.02,
            "armor": 0.015,
            "shield": 0.01,
            "accessory": 0.005
        }
        
        # Material resistance factors
        material_resistance = {
            "metal": 1.0,
            "leather": 1.3,
            "cloth": 1.5,
            "wood": 1.2,
            "magical": 0.7,
            "adamantine": 0.3,
            "mithril": 0.4
        }
        
        base_rate = base_rates.get(equipment_type, 0.01)
        env_factor = self.ENVIRONMENTAL_FACTORS.get(environment, 1.0)
        material_factor = material_resistance.get(equipment_material, 1.0)
        
        # Calculate environmental damage
        damage = base_rate * env_factor * material_factor * exposure_hours
        
        environment_details = {
            "equipment_type": equipment_type,
            "environment": environment,
            "exposure_hours": exposure_hours,
            "equipment_material": equipment_material,
            "base_rate": base_rate,
            "environment_factor": env_factor,
            "material_factor": material_factor,
            "total_damage": round(damage, 2)
        }
        
        return round(damage, 2), environment_details

    # ==========================================
    # CONDITION STATUS & PENALTIES
    # ==========================================
    
    def get_durability_status(self, durability: float) -> str:
        """Get durability status string based on percentage."""
        for status, threshold in self.DURABILITY_THRESHOLDS.items():
            if durability >= threshold:
                return status
        return "broken"
    
    def get_condition_effects(self, durability: float) -> Dict[str, Any]:
        """
        Get comprehensive condition effects and penalties.
        
        Args:
            durability: Current durability percentage (0-100)
            
        Returns:
            Dictionary with complete condition information
        """
        status = self.get_durability_status(durability)
        penalty_multiplier = self.STAT_PENALTY_MULTIPLIERS.get(status, 0.0)
        
        # Determine condition descriptions
        descriptions = {
            "perfect": "Equipment is in perfect condition",
            "excellent": "Equipment is in excellent condition",
            "good": "Equipment is in good condition",
            "worn": "Equipment shows wear but functions normally",
            "damaged": "Equipment is damaged and less effective",
            "very_damaged": "Equipment is heavily damaged",
            "broken": "Equipment is broken and cannot be used"
        }
        
        # Determine repair urgency
        repair_urgency = "none"
        if durability < 10:
            repair_urgency = "critical"
        elif durability < 25:
            repair_urgency = "urgent"
        elif durability < 50:
            repair_urgency = "recommended"
        elif durability < 75:
            repair_urgency = "minor"
        
        # Calculate repair difficulty modifier
        repair_difficulty_modifier = 0.0
        if durability < 10:
            repair_difficulty_modifier = -0.2  # Very damaged items are harder to repair
        elif durability < 25:
            repair_difficulty_modifier = -0.1  # Damaged items are slightly harder
        
        return {
            "status": status,
            "stat_penalty_multiplier": penalty_multiplier,
            "description": descriptions.get(status, "Unknown condition"),
            "durability": round(durability, 1),
            "needs_repair": durability < 75.0,
            "is_broken": durability < 10.0,
            "can_be_equipped": durability >= 10.0,
            "repair_urgency": repair_urgency,
            "repair_difficulty_modifier": repair_difficulty_modifier,
            "effectiveness_percentage": round((1.0 - penalty_multiplier) * 100, 1)
        }

    def apply_condition_penalties(
        self, 
        base_stats: Dict[str, Any],
        durability: float
    ) -> Dict[str, Any]:
        """
        Apply durability-based penalties to equipment stats.
        
        Args:
            base_stats: Base equipment statistics
            durability: Current durability percentage
            
        Returns:
            Adjusted stats with condition penalties applied
        """
        if not base_stats:
            return {}
        
        # Make a copy to avoid modifying the original
        adjusted_stats = base_stats.copy()
        
        # Broken items provide no benefits
        if durability < 10.0:
            for stat in adjusted_stats:
                if isinstance(adjusted_stats[stat], (int, float)):
                    adjusted_stats[stat] = 0
            return adjusted_stats
        
        # Apply stat penalties based on condition
        status = self.get_durability_status(durability)
        penalty = self.STAT_PENALTY_MULTIPLIERS.get(status, 0.0)
        
        if penalty > 0:
            for stat in adjusted_stats:
                if isinstance(adjusted_stats[stat], (int, float)) and adjusted_stats[stat] > 0:
                    adjusted_stats[stat] = round(adjusted_stats[stat] * (1 - penalty), 2)
        
        return adjusted_stats

    # ==========================================
    # REPAIR CALCULATIONS
    # ==========================================
    
    def calculate_repair_cost(
        self, 
        equipment_id: str,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality,
        base_item_value: float
    ) -> Dict[str, Any]:
        """
        Calculate the cost to repair equipment.
        
        Args:
            equipment_id: ID of the equipment
            current_durability: Current durability percentage
            target_durability: Desired durability percentage
            quality: Quality level of the equipment
            base_item_value: Base value of the item
            
        Returns:
            Dictionary with repair cost details
        """
        if target_durability <= current_durability:
            return {
                "repair_cost": 0,
                "repair_percentage": 0,
                "quality": quality.value,
                "can_repair": False,
                "reason": "Item doesn't need repair"
            }
        
        repair_percentage = (target_durability - current_durability) / 100.0
        
        # Calculate base repair cost using quality config
        total_repair_cost = QualityConfig.get_repair_cost(quality, base_item_value)
        
        # Scale by repair percentage (partial repairs cost proportionally)
        actual_cost = total_repair_cost * repair_percentage
        
        # Add damage severity multiplier
        damage_severity = (100.0 - current_durability) / 100.0
        if damage_severity > 0.9:  # Very damaged (90%+ damage)
            severity_multiplier = 1.5
        elif damage_severity > 0.7:  # Heavily damaged (70%+ damage)
            severity_multiplier = 1.25
        else:
            severity_multiplier = 1.0
        
        final_cost = actual_cost * severity_multiplier
        
        return {
            "repair_cost": round(final_cost, 2),
            "repair_percentage": round(repair_percentage * 100, 1),
            "quality": quality.value,
            "damage_severity": round(damage_severity * 100, 1),
            "severity_multiplier": severity_multiplier,
            "base_repair_cost": round(total_repair_cost, 2),
            "can_repair": True,
            "reason": "Repair cost calculated successfully"
        }

    # ==========================================
    # INTEGRATED DEGRADATION PROCESSING
    # ==========================================
    
    def process_comprehensive_degradation(
        self,
        equipment_id: str,
        current_durability: float,
        quality: EquipmentQuality,
        last_update: datetime,
        degradation_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process all forms of degradation in a single operation.
        
        Args:
            equipment_id: Equipment identifier
            current_durability: Current durability percentage
            quality: Equipment quality level
            last_update: Last degradation calculation time
            degradation_factors: Dictionary containing:
                - usage_intensity: float
                - environment: str
                - combat_events: List[Dict]
                - environmental_exposure: Dict
                
        Returns:
            Comprehensive degradation result
        """
        total_degradation = 0.0
        degradation_breakdown = {}
        
        # Time-based degradation
        time_decay, time_details = self.calculate_time_degradation(
            equipment_id=equipment_id,
            quality=quality,
            last_update=last_update,
            usage_intensity=degradation_factors.get('usage_intensity', 1.0),
            environment=degradation_factors.get('environment', 'normal')
        )
        total_degradation += time_decay
        degradation_breakdown['time_based'] = time_details
        
        # Combat degradation
        combat_events = degradation_factors.get('combat_events', [])
        combat_degradation = 0.0
        for event in combat_events:
            damage, combat_details = self.calculate_combat_degradation(
                equipment_type=event.get('equipment_type', 'weapon'),
                combat_intensity=event.get('intensity', 1.0),
                is_critical=event.get('is_critical', False),
                damage_taken=event.get('damage_taken', 0.0),
                blocks_made=event.get('blocks_made', 0)
            )
            combat_degradation += damage
        
        total_degradation += combat_degradation
        degradation_breakdown['combat'] = {
            'total_events': len(combat_events),
            'total_damage': combat_degradation
        }
        
        # Environmental degradation
        env_exposure = degradation_factors.get('environmental_exposure', {})
        if env_exposure:
            env_damage, env_details = self.calculate_environmental_degradation(
                equipment_type=env_exposure.get('equipment_type', 'weapon'),
                environment=env_exposure.get('environment', 'normal'),
                exposure_hours=env_exposure.get('hours', 0.0),
                equipment_material=env_exposure.get('material', 'metal')
            )
            total_degradation += env_damage
            degradation_breakdown['environmental'] = env_details
        
        # Calculate new durability
        new_durability = max(0.0, current_durability - total_degradation)
        
        # Get condition effects
        old_condition = self.get_condition_effects(current_durability)
        new_condition = self.get_condition_effects(new_durability)
        
        return {
            "equipment_id": equipment_id,
            "previous_durability": current_durability,
            "new_durability": new_durability,
            "total_degradation": round(total_degradation, 2),
            "degradation_breakdown": degradation_breakdown,
            "previous_condition": old_condition,
            "new_condition": new_condition,
            "condition_changed": old_condition['status'] != new_condition['status'],
            "became_broken": new_durability < 10.0 and current_durability >= 10.0,
            "needs_immediate_attention": new_condition['repair_urgency'] in ['critical', 'urgent']
        }

    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def validate_equipment_condition(
        self,
        durability: float,
        action: str = "equip"
    ) -> Tuple[bool, str]:
        """
        Validate if equipment condition allows a specific action.
        
        Args:
            durability: Current durability percentage
            action: Action to validate ('equip', 'use', 'enhance')
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if action == "equip":
            if durability < 10.0:
                return False, "Cannot equip broken equipment"
            return True, "Equipment can be equipped"
        
        elif action == "use":
            if durability <= 0.0:
                return False, "Equipment is completely broken"
            elif durability < 5.0:
                return False, "Equipment is too damaged to use safely"
            return True, "Equipment can be used"
        
        elif action == "enhance":
            if durability < 50.0:
                return False, "Equipment must be in good condition to enhance"
            return True, "Equipment can be enhanced"
        
        return True, "Action permitted"
    
    def estimate_repair_time(
        self,
        current_durability: float,
        target_durability: float,
        quality: EquipmentQuality,
        repairer_skill: int = 50
    ) -> Dict[str, Any]:
        """
        Estimate time required for equipment repair.
        
        Args:
            current_durability: Current condition
            target_durability: Desired condition
            quality: Equipment quality
            repairer_skill: Skill level of repairer (0-100)
            
        Returns:
            Time estimation details
        """
        repair_percentage = (target_durability - current_durability) / 100.0
        
        # Base time in hours
        base_time_hours = repair_percentage * 4.0  # 4 hours for full repair
        
        # Quality modifier
        quality_multipliers = {
            EquipmentQuality.BASIC: 1.0,
            EquipmentQuality.MILITARY: 1.5,
            EquipmentQuality.MASTERCRAFT: 2.5
        }
        
        quality_time = base_time_hours * quality_multipliers.get(quality, 1.0)
        
        # Skill modifier (higher skill = faster repair)
        skill_modifier = max(0.5, (100 - repairer_skill) / 100.0 + 0.5)
        
        final_time_hours = quality_time * skill_modifier
        
        return {
            "base_time_hours": round(base_time_hours, 2),
            "quality_modifier": quality_multipliers.get(quality, 1.0),
            "skill_modifier": round(skill_modifier, 2),
            "final_time_hours": round(final_time_hours, 2),
            "final_time_days": round(final_time_hours / 24, 2)
        }

    def apply_weapon_attack_damage(self, equipment_id: str, attack_type: str, is_critical: bool = False, is_attacker: bool = True) -> Dict[str, Any]:
        """
        Apply durability damage based on weapon attacks (given or received)
        
        Args:
            equipment_id: ID of the equipment to damage
            attack_type: Type of attack ('melee', 'ranged', etc.)
            is_critical: Whether the attack was critical
            is_attacker: True if giving attack, False if receiving
            
        Returns:
            Dict with damage applied and new durability status
        """
        try:
            # Get integration trigger configuration
            trigger_key = "weapon_attack_given" if is_attacker else "weapon_attack_received"
            trigger_config = self.integration_triggers.get(trigger_key, {})
            
            if not trigger_config.get("enabled", False):
                return {"success": False, "reason": "Integration trigger disabled"}
            
            # Calculate damage based on configuration
            base_damage = trigger_config.get("durability_loss_base", 1.0)
            critical_multiplier = trigger_config.get("critical_multiplier", 1.0)
            
            damage_amount = base_damage
            if is_critical:
                damage_amount *= critical_multiplier
            
            # Apply the damage
            result = self.apply_durability_damage(equipment_id, damage_amount, "weapon_attack")
            result["attack_type"] = attack_type
            result["is_critical"] = is_critical
            result["is_attacker"] = is_attacker
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying weapon attack damage: {e}")
            return {"success": False, "error": str(e)} 