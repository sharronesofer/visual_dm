"""
Enchanting service for Visual DM equipment system.

Implements the core business logic for the learn-by-disenchanting system,
including risk calculations, success probability, and integration with
character abilities and the economy system.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Protocol
from uuid import UUID

from ..models.enchanting import (
    EnchantmentDefinition, LearnedEnchantment, DisenchantmentAttempt,
    EnchantmentApplication, CharacterEnchantingProfile, 
    DisenchantmentOutcome, EnchantmentRarity, EnchantmentSchool,
    get_enchantment_definition, get_enchantments_by_rarity
)
from ..events import equipment_event_publisher, EquipmentEventType


# Protocol for equipment quality service dependency injection
class EquipmentQualityServiceProtocol(Protocol):
    """Protocol for equipment quality service to avoid circular imports"""
    
    def get_quality_stats(self, quality: str) -> Dict[str, any]:
        """Get quality statistics for equipment"""
        ...


class EnchantingService:
    """Service for managing the enchanting and disenchanting system."""
    
    def __init__(self, equipment_quality_service: Optional[EquipmentQualityServiceProtocol] = None):
        self.equipment_quality_service = equipment_quality_service
        self.character_profiles: Dict[UUID, CharacterEnchantingProfile] = {}
    
    def get_character_profile(self, character_id: UUID) -> CharacterEnchantingProfile:
        """Get or create a character's enchanting profile."""
        if character_id not in self.character_profiles:
            self.character_profiles[character_id] = CharacterEnchantingProfile(
                character_id=character_id
            )
        return self.character_profiles[character_id]
    
    def attempt_disenchantment(self, character_id: UUID, item_id: UUID, 
                             item_data: dict, arcane_manipulation_level: int,
                             character_level: int, target_enchantment: str = None) -> DisenchantmentAttempt:
        """
        Attempt to disenchant an item to learn its enchantments.
        
        Args:
            character_id: ID of character attempting disenchantment
            item_id: ID of item being disenchanted
            item_data: Complete item data including enchantments
            arcane_manipulation_level: Character's Arcane Manipulation ability level
            character_level: Character's overall level
            target_enchantment: Specific enchantment to try to learn (optional)
        
        Returns:
            DisenchantmentAttempt record with results
        """
        profile = self.get_character_profile(character_id)
        
        # Create attempt record
        attempt = DisenchantmentAttempt(
            character_id=character_id,
            item_id=item_id,
            item_name=item_data.get('name', 'Unknown Item'),
            item_quality=item_data.get('quality', 'basic'),
            item_enchantments=item_data.get('enchantments', []),
            arcane_manipulation_level=arcane_manipulation_level,
            character_level=character_level,
            target_enchantment=target_enchantment
        )
        
        # Validate prerequisites
        if arcane_manipulation_level < 1:
            attempt.outcome = DisenchantmentOutcome.FAILURE_SAFE
            attempt.additional_consequences.append("Requires Arcane Manipulation ability")
            return attempt
        
        if not attempt.item_enchantments:
            attempt.outcome = DisenchantmentOutcome.FAILURE_SAFE
            attempt.additional_consequences.append("Item has no enchantments to learn")
            return attempt
        
        # Select enchantment to learn
        if target_enchantment and target_enchantment in attempt.item_enchantments:
            enchantment_to_learn = target_enchantment
        else:
            # Random selection from available enchantments
            learnable_enchantments = [
                e for e in attempt.item_enchantments 
                if e not in profile.learned_enchantments
            ]
            if not learnable_enchantments:
                # All enchantments already known
                attempt.outcome = DisenchantmentOutcome.SUCCESS_KNOWN
                attempt.item_destroyed = True
                self._apply_disenchantment_experience(profile, attempt)
                return attempt
            
            enchantment_to_learn = random.choice(learnable_enchantments)
        
        # Get enchantment definition for difficulty calculation
        enchantment_def = get_enchantment_definition(enchantment_to_learn)
        if not enchantment_def:
            attempt.outcome = DisenchantmentOutcome.FAILURE_SAFE
            attempt.additional_consequences.append(f"Unknown enchantment: {enchantment_to_learn}")
            return attempt
        
        # Calculate success probability
        success_rate = profile.get_learning_success_rate(
            enchantment_def.rarity,
            attempt.item_quality,
            arcane_manipulation_level
        )
        
        # Apply risk factors
        risk_factors = self._calculate_risk_factors(attempt, enchantment_def)
        
        # Determine outcome
        roll = random.random()
        if roll <= success_rate:
            # Success - learn the enchantment
            learned_enchantment = LearnedEnchantment(
                character_id=character_id,
                enchantment_id=enchantment_to_learn,
                learned_at=datetime.now(),
                learned_from_item=attempt.item_name
            )
            profile.learned_enchantments[enchantment_to_learn] = learned_enchantment
            
            attempt.outcome = DisenchantmentOutcome.SUCCESS_LEARNED
            attempt.enchantment_learned = enchantment_to_learn
            attempt.item_destroyed = True
            
            # Publish success event
            equipment_event_publisher.publish_event(
                EquipmentEventType.DISENCHANTMENT_COMPLETED,
                {
                    'character_id': str(character_id),
                    'item_id': str(item_id),
                    'enchantment_learned': enchantment_to_learn,
                    'success': True
                }
            )
            
        elif roll <= success_rate + risk_factors['partial_success_chance']:
            # Partial success - learn a weaker version
            attempt.outcome = DisenchantmentOutcome.PARTIAL_SUCCESS
            attempt.item_destroyed = True
            # TODO: Implement weaker version learning
            
        elif roll <= success_rate + risk_factors['safe_failure_chance']:
            # Safe failure - item preserved
            attempt.outcome = DisenchantmentOutcome.FAILURE_SAFE
            attempt.item_destroyed = False
            
        elif roll <= success_rate + risk_factors['destructive_failure_chance']:
            # Destructive failure - item destroyed
            attempt.outcome = DisenchantmentOutcome.FAILURE_DESTROYED
            attempt.item_destroyed = True
            
        else:
            # Critical failure - item destroyed with consequences
            attempt.outcome = DisenchantmentOutcome.CRITICAL_FAILURE
            attempt.item_destroyed = True
            attempt.additional_consequences.extend(
                self._generate_critical_failure_consequences(enchantment_def.rarity)
            )
        
        # Apply experience and tracking
        self._apply_disenchantment_experience(profile, attempt)
        
        # Publish completion event
        equipment_event_publisher.publish_event(
            EquipmentEventType.DISENCHANTMENT_COMPLETED if attempt.outcome.value.startswith('success') else EquipmentEventType.DISENCHANTMENT_FAILED,
            {
                'character_id': str(character_id),
                'item_id': str(item_id),
                'outcome': attempt.outcome.value,
                'item_destroyed': attempt.item_destroyed,
                'enchantment_learned': attempt.enchantment_learned
            }
        )
        
        return attempt
    
    def attempt_enchantment(self, character_id: UUID, item_id: UUID,
                          item_data: dict, enchantment_id: str,
                          gold_available: int) -> EnchantmentApplication:
        """
        Attempt to apply an enchantment to an item.
        
        Args:
            character_id: Character applying the enchantment
            item_id: Item to enchant
            item_data: Current item data
            enchantment_id: Enchantment to apply
            gold_available: Gold the character has available
        
        Returns:
            EnchantmentApplication record with results
        """
        profile = self.get_character_profile(character_id)
        
        # Validate enchantment is learned
        if enchantment_id not in profile.learned_enchantments:
            return EnchantmentApplication(
                character_id=character_id,
                item_id=item_id,
                enchantment_id=enchantment_id,
                cost_paid=0,
                success=False,
                failure_reason="Enchantment not learned"
            )
        
        learned_enchantment = profile.learned_enchantments[enchantment_id]
        enchantment_def = get_enchantment_definition(enchantment_id)
        
        # Check compatibility
        can_apply, reason = learned_enchantment.can_apply_to_item(
            item_data.get('quality', 'basic'),
            item_data.get('type', 'unknown'),
            item_data.get('enchantments', [])
        )
        
        if not can_apply:
            return EnchantmentApplication(
                character_id=character_id,
                item_id=item_id,
                enchantment_id=enchantment_id,
                cost_paid=0,
                success=False,
                failure_reason=reason
            )
        
        # Calculate cost
        base_cost = enchantment_def.base_cost
        mastery_discount = (learned_enchantment.mastery_level - 1) * 0.1
        final_cost = int(base_cost * (1 - mastery_discount))
        
        if gold_available < final_cost:
            return EnchantmentApplication(
                character_id=character_id,
                item_id=item_id,
                enchantment_id=enchantment_id,
                cost_paid=0,
                success=False,
                failure_reason=f"Insufficient gold (need {final_cost}, have {gold_available})"
            )
        
        # Calculate success rate
        base_success_rate = 0.8  # 80% base success rate for applying learned enchantments
        mastery_bonus = learned_enchantment.mastery_level * 0.05
        quality_penalty = self._get_application_quality_penalty(item_data.get('quality', 'basic'))
        
        success_rate = base_success_rate + mastery_bonus - quality_penalty
        success_rate = max(0.1, min(0.98, success_rate))  # Clamp between 10% and 98%
        
        # Attempt application
        application = EnchantmentApplication(
            character_id=character_id,
            item_id=item_id,
            enchantment_id=enchantment_id,
            cost_paid=final_cost,
            success=random.random() <= success_rate
        )
        
        if application.success:
            # Calculate power level based on mastery and randomness
            base_power = 75 + (learned_enchantment.mastery_level * 5)
            power_variance = random.randint(-15, 15)
            application.final_power_level = max(50, min(100, base_power + power_variance))
            
            # Update mastery progress
            learned_enchantment.times_applied += 1
            if learned_enchantment.times_applied % 5 == 0:  # Mastery increases every 5 applications
                learned_enchantment.mastery_level = min(5, learned_enchantment.mastery_level + 1)
                application.mastery_increased = True
            
            # Track profile statistics
            profile.successful_applications += 1
            
            # Publish success event
            equipment_event_publisher.publish_event(
                EquipmentEventType.ENCHANTMENT_APPLIED,
                {
                    'character_id': str(character_id),
                    'item_id': str(item_id),
                    'enchantment_id': enchantment_id,
                    'power_level': application.final_power_level,
                    'cost': final_cost,
                    'success': True
                }
            )
        else:
            # Application failed
            application.failure_reason = "Enchantment application failed during casting"
            
            # 50% chance to lose materials on failure
            if random.random() <= 0.5:
                application.materials_lost = True
            
            profile.failed_applications += 1
            
            # Publish failure event
            equipment_event_publisher.publish_event(
                EquipmentEventType.ENCHANTMENT_FAILED,
                {
                    'character_id': str(character_id),
                    'item_id': str(item_id),
                    'enchantment_id': enchantment_id,
                    'cost': final_cost,
                    'materials_lost': application.materials_lost,
                    'failure_reason': application.failure_reason
                }
            )
        
        return application
    
    def get_available_enchantments_for_item(self, character_id: UUID, 
                                          item_data: dict) -> List[Dict]:
        """Get list of enchantments this character can apply to the given item."""
        profile = self.get_character_profile(character_id)
        available = []
        
        for enchantment_id, learned_enchantment in profile.learned_enchantments.items():
            can_apply, reason = learned_enchantment.can_apply_to_item(
                item_data.get('quality', 'basic'),
                item_data.get('type', 'unknown'),
                item_data.get('enchantments', [])
            )
            
            if can_apply:
                enchantment_def = get_enchantment_definition(enchantment_id)
                cost = self._calculate_application_cost(learned_enchantment, enchantment_def)
                
                available.append({
                    'enchantment_id': enchantment_id,
                    'name': enchantment_def.name,
                    'description': enchantment_def.description,
                    'school': enchantment_def.school.value,
                    'rarity': enchantment_def.rarity.value,
                    'cost': cost,
                    'mastery_level': learned_enchantment.mastery_level,
                    'times_applied': learned_enchantment.times_applied
                })
        
        return available
    
    def get_learnable_enchantments_from_item(self, character_id: UUID,
                                           item_data: dict) -> List[Dict]:
        """Get list of enchantments that can be learned from disenchanting this item."""
        profile = self.get_character_profile(character_id)
        learnable = []
        
        for enchantment_id in item_data.get('enchantments', []):
            if enchantment_id not in profile.learned_enchantments:
                enchantment_def = get_enchantment_definition(enchantment_id)
                if enchantment_def:
                    success_rate = profile.get_learning_success_rate(
                        enchantment_def.rarity,
                        item_data.get('quality', 'basic'),
                        # TODO: Get actual arcane manipulation level from character
                        3  # Placeholder
                    )
                    
                    learnable.append({
                        'enchantment_id': enchantment_id,
                        'name': enchantment_def.name,
                        'description': enchantment_def.description,
                        'school': enchantment_def.school.value,
                        'rarity': enchantment_def.rarity.value,
                        'success_rate': round(success_rate * 100, 1),
                        'min_arcane_manipulation': enchantment_def.min_arcane_manipulation
                    })
        
        return learnable
    
    def _calculate_risk_factors(self, attempt: DisenchantmentAttempt, 
                              enchantment_def: EnchantmentDefinition) -> Dict[str, float]:
        """Calculate risk factors for disenchantment based on attempt parameters."""
        # Base risk by rarity
        rarity_risks = {
            EnchantmentRarity.BASIC: {'partial': 0.15, 'safe': 0.6, 'destructive': 0.9},
            EnchantmentRarity.MILITARY: {'partial': 0.12, 'safe': 0.4, 'destructive': 0.8},
            EnchantmentRarity.NOBLE: {'partial': 0.08, 'safe': 0.25, 'destructive': 0.7},
            EnchantmentRarity.LEGENDARY: {'partial': 0.05, 'safe': 0.15, 'destructive': 0.6}
        }
        
        base_risks = rarity_risks[enchantment_def.rarity]
        
        # Adjust based on character level and ability
        skill_modifier = attempt.arcane_manipulation_level * 0.02
        
        return {
            'partial_success_chance': base_risks['partial'] + skill_modifier,
            'safe_failure_chance': base_risks['safe'] + skill_modifier,
            'destructive_failure_chance': base_risks['destructive'] - skill_modifier
        }
    
    def _generate_critical_failure_consequences(self, rarity: EnchantmentRarity) -> List[str]:
        """Generate consequences for critical failures based on enchantment rarity."""
        consequences = []
        
        if rarity in [EnchantmentRarity.NOBLE, EnchantmentRarity.LEGENDARY]:
            consequences.extend([
                "Magical backlash causes 1d6 damage",
                "Nearby magical items may be affected",
                "Temporary -2 penalty to Arcane Manipulation checks for 24 hours"
            ])
        
        if rarity == EnchantmentRarity.LEGENDARY:
            consequences.extend([
                "Magical resonance detected by nearby mages",
                "50% chance to destroy one random item in inventory"
            ])
        
        return consequences
    
    def _apply_disenchantment_experience(self, profile: CharacterEnchantingProfile,
                                      attempt: DisenchantmentAttempt):
        """Apply experience and progression from a disenchantment attempt."""
        profile.total_items_disenchanted += 1
        
        # Calculate experience based on outcome and rarity
        base_exp = {
            EnchantmentRarity.BASIC: 10,
            EnchantmentRarity.MILITARY: 25,
            EnchantmentRarity.NOBLE: 50,
            EnchantmentRarity.LEGENDARY: 100
        }
        
        enchantment_def = get_enchantment_definition(attempt.enchantment_learned or 
                                                   attempt.item_enchantments[0])
        if enchantment_def:
            exp_gain = base_exp.get(enchantment_def.rarity, 10)
            
            # Bonus for successful learning
            if attempt.outcome == DisenchantmentOutcome.SUCCESS_LEARNED:
                exp_gain *= 2
            
            attempt.experience_gained = exp_gain
    
    def _calculate_application_cost(self, learned_enchantment: LearnedEnchantment,
                                  enchantment_def: EnchantmentDefinition) -> int:
        """Calculate the cost to apply an enchantment based on mastery."""
        base_cost = enchantment_def.base_cost
        mastery_discount = (learned_enchantment.mastery_level - 1) * 0.1
        return int(base_cost * (1 - mastery_discount))
    
    def _get_application_quality_penalty(self, item_quality: str) -> float:
        """Get penalty for applying enchantments to lower quality items."""
        penalties = {
            'basic': 0.2,      # 20% penalty
            'military': 0.1,   # 10% penalty
            'noble': 0.0,      # No penalty
            'legendary': -0.1  # 10% bonus
        }
        return penalties.get(item_quality, 0.15) 