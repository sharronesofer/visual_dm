"""
Combat-Equipment Integration Service

This service bridges the equipment system with Visual DM's combat system,
applying equipment bonuses to combat calculations and handling equipment
degradation during combat.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import random

from .hybrid_equipment_service import HybridEquipmentService
from .character_equipment_integration import CharacterEquipmentIntegration
from backend.systems.equipment.models.equipment_models import EquipmentInstance

logger = logging.getLogger(__name__)

class CombatEquipmentIntegration:
    """
    Service for integrating equipment with combat mechanics.
    
    Handles:
    - Equipment stat bonuses for combat calculations
    - Equipment degradation during combat
    - Weapon and armor effectiveness
    - Critical hit equipment interactions
    """
    
    def __init__(self, session: Session):
        """Initialize the combat equipment integration service."""
        self.session = session
        self.equipment_service = HybridEquipmentService(session)
        self.character_equipment = CharacterEquipmentIntegration(session)
        
        logger.info("Initialized CombatEquipmentIntegration service")
    
    def get_combat_stats_for_character(self, character_id: str) -> Dict[str, Any]:
        """
        Calculate complete combat stats including equipment bonuses.
        
        Args:
            character_id: Character's unique identifier
            
        Returns:
            Dictionary with all combat-relevant stats
        """
        try:
            # Get equipment bonuses
            equipment_bonuses = self.character_equipment.apply_equipment_to_character_stats(character_id)
            
            # Get equipped weapon and armor details
            equipped_items = self.equipment_service.get_character_equipment(character_id, equipped_only=True)
            
            # Categorize equipment
            weapons = []
            armor_pieces = []
            shields = []
            accessories = []
            
            for equipment in equipped_items:
                if not equipment.is_functional():
                    continue  # Skip broken equipment
                    
                details = self.equipment_service.get_equipment_details(equipment.id)
                template = details.get('template')
                
                if template:
                    if template.item_type == 'weapon':
                        weapons.append({
                            'equipment': equipment,
                            'template': template,
                            'details': details
                        })
                    elif template.item_type == 'armor':
                        armor_pieces.append({
                            'equipment': equipment,
                            'template': template,
                            'details': details
                        })
                    elif template.item_type == 'shield':
                        shields.append({
                            'equipment': equipment,
                            'template': template,
                            'details': details
                        })
                    elif template.item_type == 'accessory':
                        accessories.append({
                            'equipment': equipment,
                            'template': template,
                            'details': details
                        })
            
            # Calculate derived combat stats
            primary_weapon = weapons[0] if weapons else None
            primary_armor = armor_pieces[0] if armor_pieces else None
            primary_shield = shields[0] if shields else None
            
            combat_stats = {
                # Base stats with equipment bonuses
                'armor_class': 10 + equipment_bonuses.get('armor_class', 0),
                'attack_bonus': equipment_bonuses.get('attack_bonus', 0),
                'damage_bonus': equipment_bonuses.get('damage_bonus', 0),
                'initiative_bonus': equipment_bonuses.get('initiative', 0),
                'speed': 30 + equipment_bonuses.get('speed', 0),
                
                # Weapon information
                'primary_weapon': self._get_weapon_stats(primary_weapon) if primary_weapon else None,
                'secondary_weapons': [self._get_weapon_stats(w) for w in weapons[1:]] if len(weapons) > 1 else [],
                
                # Armor information
                'armor': self._get_armor_stats(primary_armor) if primary_armor else None,
                'shield': self._get_shield_stats(primary_shield) if primary_shield else None,
                
                # Equipment condition summary
                'equipment_condition': self._get_equipment_condition_summary(equipped_items),
                
                # Equipment count by type
                'equipment_summary': {
                    'weapons': len(weapons),
                    'armor_pieces': len(armor_pieces),
                    'shields': len(shields),
                    'accessories': len(accessories),
                    'total_equipped': len(equipped_items)
                }
            }
            
            return combat_stats
            
        except Exception as e:
            logger.error(f"Failed to get combat stats for character {character_id}: {e}")
            return {}
    
    def calculate_attack_roll(self, attacker_id: str, target_id: str, 
                            weapon_slot: str = "main_hand") -> Dict[str, Any]:
        """
        Calculate attack roll with equipment bonuses.
        
        Args:
            attacker_id: Attacking character ID
            target_id: Target character ID
            weapon_slot: Equipment slot of weapon being used
            
        Returns:
            Dictionary with attack calculation results
        """
        try:
            # Get attacker's combat stats
            attacker_stats = self.get_combat_stats_for_character(attacker_id)
            target_stats = self.get_combat_stats_for_character(target_id)
            
            # Get weapon being used
            weapon_info = None
            if weapon_slot == "main_hand" and attacker_stats.get('primary_weapon'):
                weapon_info = attacker_stats['primary_weapon']
            elif weapon_slot == "off_hand":
                secondary_weapons = attacker_stats.get('secondary_weapons', [])
                weapon_info = secondary_weapons[0] if secondary_weapons else None
            
            # Base attack roll (d20)
            base_roll = random.randint(1, 20)
            
            # Calculate attack bonus
            attack_bonus = attacker_stats.get('attack_bonus', 0)
            
            # Add weapon-specific bonuses
            weapon_bonus = 0
            weapon_name = "Unarmed Strike"
            damage_dice = "1d4"
            damage_type = "bludgeoning"
            
            if weapon_info:
                weapon_bonus = weapon_info.get('attack_bonus', 0)
                weapon_name = weapon_info.get('name', 'Unknown Weapon')
                damage_dice = weapon_info.get('damage_dice', '1d6')
                damage_type = weapon_info.get('damage_type', 'slashing')
            
            total_attack = base_roll + attack_bonus + weapon_bonus
            
            # Get target's AC
            target_ac = target_stats.get('armor_class', 10)
            
            # Check hit/miss
            is_critical = base_roll == 20
            is_fumble = base_roll == 1
            is_hit = total_attack >= target_ac or is_critical
            
            result = {
                'attacker_id': attacker_id,
                'target_id': target_id,
                'weapon_slot': weapon_slot,
                'weapon_name': weapon_name,
                'base_roll': base_roll,
                'attack_bonus': attack_bonus,
                'weapon_bonus': weapon_bonus,
                'total_attack': total_attack,
                'target_ac': target_ac,
                'is_hit': is_hit,
                'is_critical': is_critical,
                'is_fumble': is_fumble,
                'damage_dice': damage_dice,
                'damage_type': damage_type
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate attack roll: {e}")
            return {'error': str(e)}
    
    def calculate_damage_roll(self, attack_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate damage based on attack result and equipment.
        
        Args:
            attack_result: Result from calculate_attack_roll
            
        Returns:
            Dictionary with damage calculation results
        """
        try:
            if not attack_result.get('is_hit'):
                return {
                    'damage': 0,
                    'damage_type': attack_result.get('damage_type', 'none'),
                    'message': "Attack missed - no damage dealt"
                }
            
            # Get attacker's stats for damage bonus
            attacker_stats = self.get_combat_stats_for_character(attack_result['attacker_id'])
            damage_bonus = attacker_stats.get('damage_bonus', 0)
            
            # Parse and roll damage dice
            damage_dice = attack_result.get('damage_dice', '1d4')
            base_damage = self._roll_dice(damage_dice)
            
            # Apply damage bonus
            total_damage = base_damage + damage_bonus
            
            # Critical hit doubles damage
            if attack_result.get('is_critical'):
                total_damage = base_damage * 2 + damage_bonus  # Double dice, not bonus
            
            # Minimum damage
            total_damage = max(1, total_damage)
            
            return {
                'base_damage': base_damage,
                'damage_bonus': damage_bonus,
                'total_damage': total_damage,
                'damage_type': attack_result.get('damage_type', 'slashing'),
                'is_critical': attack_result.get('is_critical', False),
                'damage_dice': damage_dice,
                'message': f"Deals {total_damage} {attack_result.get('damage_type', 'slashing')} damage"
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate damage: {e}")
            return {'error': str(e)}
    
    def apply_combat_action(self, attacker_id: str, target_id: str, 
                          action_type: str = "attack", 
                          weapon_slot: str = "main_hand") -> Dict[str, Any]:
        """
        Execute a complete combat action with equipment integration.
        
        Args:
            attacker_id: Attacking character ID
            target_id: Target character ID
            action_type: Type of action (attack, spell, etc.)
            weapon_slot: Equipment slot being used
            
        Returns:
            Complete combat action result
        """
        try:
            if action_type == "attack":
                # Calculate attack
                attack_result = self.calculate_attack_roll(attacker_id, target_id, weapon_slot)
                
                if attack_result.get('error'):
                    return attack_result
                
                # Calculate damage if hit
                damage_result = self.calculate_damage_roll(attack_result)
                
                # Apply equipment degradation
                equipment_effects = self._apply_combat_equipment_effects(
                    attacker_id, target_id, attack_result, damage_result
                )
                
                # Combine results
                return {
                    'action_type': action_type,
                    'attacker_id': attacker_id,
                    'target_id': target_id,
                    'attack': attack_result,
                    'damage': damage_result,
                    'equipment_effects': equipment_effects,
                    'success': True,
                    'message': self._generate_combat_message(attack_result, damage_result)
                }
            
            else:
                return {
                    'error': f"Action type '{action_type}' not yet implemented",
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Failed to apply combat action: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_weapon_stats(self, weapon_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract weapon stats for combat calculations."""
        equipment = weapon_info['equipment']
        template = weapon_info['template']
        details = weapon_info['details']
        
        current_stats = details.get('current_stats', {})
        
        return {
            'equipment_id': equipment.id,
            'name': equipment.custom_name or template.name,
            'damage_dice': template.abilities.get('damage', '1d6'),
            'damage_type': template.abilities.get('damage_type', 'slashing'),
            'attack_bonus': current_stats.get('attack_bonus', 0),
            'damage_bonus': current_stats.get('damage_bonus', 0),
            'critical_range': template.abilities.get('critical_range', 20),
            'durability': equipment.durability,
            'condition': details.get('condition_status', 'good'),
            'quality': template.quality_tier,
            'enchantments': len(equipment.applied_enchantments)
        }
    
    def _get_armor_stats(self, armor_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract armor stats for combat calculations."""
        equipment = armor_info['equipment']
        template = armor_info['template']
        details = armor_info['details']
        
        current_stats = details.get('current_stats', {})
        
        return {
            'equipment_id': equipment.id,
            'name': equipment.custom_name or template.name,
            'armor_class': current_stats.get('armor_class', 0),
            'damage_reduction': current_stats.get('damage_reduction', 0),
            'durability': equipment.durability,
            'condition': details.get('condition_status', 'good'),
            'quality': template.quality_tier,
            'coverage': template.abilities.get('coverage', 'partial'),
            'material': template.abilities.get('material', 'unknown')
        }
    
    def _get_shield_stats(self, shield_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract shield stats for combat calculations."""
        equipment = shield_info['equipment']
        template = shield_info['template']
        details = shield_info['details']
        
        current_stats = details.get('current_stats', {})
        
        return {
            'equipment_id': equipment.id,
            'name': equipment.custom_name or template.name,
            'armor_class': current_stats.get('armor_class', 1),
            'block_chance': template.abilities.get('block_chance', 0.1),
            'durability': equipment.durability,
            'condition': details.get('condition_status', 'good'),
            'quality': template.quality_tier
        }
    
    def _get_equipment_condition_summary(self, equipped_items: List[EquipmentInstance]) -> Dict[str, Any]:
        """Generate summary of equipment condition."""
        if not equipped_items:
            return {'average_durability': 100.0, 'items_needing_repair': 0}
        
        total_durability = sum(eq.durability for eq in equipped_items)
        average_durability = total_durability / len(equipped_items)
        
        items_needing_repair = sum(1 for eq in equipped_items if eq.durability < 75)
        broken_items = sum(1 for eq in equipped_items if not eq.is_functional())
        
        return {
            'average_durability': round(average_durability, 1),
            'items_needing_repair': items_needing_repair,
            'broken_items': broken_items,
            'total_items': len(equipped_items),
            'condition_penalty': average_durability < 50.0
        }
    
    def _roll_dice(self, dice_string: str) -> int:
        """Parse and roll dice string (e.g., '1d6', '2d8+3')."""
        try:
            if 'd' not in dice_string:
                return int(dice_string)
            
            # Parse dice notation
            parts = dice_string.split('d')
            num_dice = int(parts[0]) if parts[0] else 1
            
            if '+' in parts[1]:
                dice_size, modifier = parts[1].split('+')
                dice_size = int(dice_size)
                modifier = int(modifier)
            elif '-' in parts[1]:
                dice_size, modifier = parts[1].split('-')
                dice_size = int(dice_size)
                modifier = -int(modifier)
            else:
                dice_size = int(parts[1])
                modifier = 0
            
            # Roll dice
            total = sum(random.randint(1, dice_size) for _ in range(num_dice))
            return total + modifier
            
        except Exception:
            logger.warning(f"Failed to parse dice string '{dice_string}', using default 1d6")
            return random.randint(1, 6)
    
    def _apply_combat_equipment_effects(self, attacker_id: str, target_id: str,
                                      attack_result: Dict, damage_result: Dict) -> Dict[str, Any]:
        """Apply equipment degradation and effects from combat."""
        effects = {
            'attacker_equipment': [],
            'target_equipment': []
        }
        
        try:
            # Damage attacker's weapon
            if attack_result.get('is_hit'):
                weapon_slot = attack_result.get('weapon_slot', 'main_hand')
                attacker_weapons = self.equipment_service.get_character_equipment(
                    attacker_id, equipped_only=True
                )
                
                for weapon in attacker_weapons:
                    if weapon.equipment_slot == weapon_slot:
                        damage_amount = 2.0 if attack_result.get('is_critical') else 1.0
                        success = self.equipment_service.apply_combat_damage(
                            weapon.id, damage_amount
                        )
                        
                        if success:
                            effects['attacker_equipment'].append({
                                'equipment_id': weapon.id,
                                'equipment_name': weapon.custom_name,
                                'effect': 'durability_loss',
                                'amount': damage_amount
                            })
            
            # Damage target's armor if they took damage
            if damage_result.get('total_damage', 0) > 0:
                target_armor = self.equipment_service.get_character_equipment(
                    target_id, equipped_only=True
                )
                
                for armor in target_armor:
                    if armor.equipment_slot in ['chest', 'legs', 'head']:
                        damage_amount = damage_result['total_damage'] * 0.1  # 10% of damage taken
                        success = self.equipment_service.apply_combat_damage(
                            armor.id, damage_amount
                        )
                        
                        if success:
                            effects['target_equipment'].append({
                                'equipment_id': armor.id,
                                'equipment_name': armor.custom_name,
                                'effect': 'durability_loss',
                                'amount': damage_amount
                            })
            
        except Exception as e:
            logger.warning(f"Failed to apply equipment effects: {e}")
        
        return effects
    
    def _generate_combat_message(self, attack_result: Dict, damage_result: Dict) -> str:
        """Generate descriptive combat message."""
        weapon_name = attack_result.get('weapon_name', 'weapon')
        base_roll = attack_result.get('base_roll', 0)
        
        if attack_result.get('is_fumble'):
            return f"Critical fumble! (Rolled {base_roll}) The {weapon_name} attack fails catastrophically!"
        
        if not attack_result.get('is_hit'):
            return f"Miss! (Rolled {base_roll}) The {weapon_name} attack fails to connect."
        
        damage = damage_result.get('total_damage', 0)
        damage_type = damage_result.get('damage_type', 'damage')
        
        if attack_result.get('is_critical'):
            return f"Critical hit! (Rolled {base_roll}) The {weapon_name} strikes true for {damage} {damage_type} damage!"
        
        return f"Hit! (Rolled {base_roll}) The {weapon_name} deals {damage} {damage_type} damage." 