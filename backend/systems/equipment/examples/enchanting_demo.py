#!/usr/bin/env python3
"""
Enchanting System Integration Demo

This script demonstrates the complete enchanting system for Visual DM,
showcasing the learn-by-disenchanting workflow, enchantment application,
and integration between all components.

Run this script to see the enchanting system in action!
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4, UUID

# Add the equipment system to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.enchanting_service import EnchantingService
from services.equipment_quality import EquipmentQualityService  
from repositories.equipment_repository import EquipmentRepository
from repositories.enchanting_repository import EnchantingRepository
from models.enchanting import (
    register_enchantment, EnchantmentDefinition, EnchantmentRarity, 
    EnchantmentSchool, get_enchantment_definition
)

class EnchantingSystemDemo:
    """Demonstrates the complete enchanting system functionality."""
    
    def __init__(self):
        # Initialize services and repositories
        self.equipment_quality_service = EquipmentQualityService()
        self.equipment_repo = EquipmentRepository("demo_data/equipment")
        self.enchanting_repo = EnchantingRepository("demo_data/enchanting")
        self.enchanting_service = EnchantingService(self.equipment_quality_service)
        
        # Demo character
        self.character_id = UUID('12345678-1234-5678-9abc-123456789abc')
        self.character_name = "Lyra the Enchantress"
        
        print(f"🧙‍♀️ Welcome to the Visual DM Enchanting System Demo!")
        print(f"Playing as: {self.character_name}")
        print("=" * 60)
    
    def register_demo_enchantments(self):
        """Register some sample enchantments for the demo."""
        print("📚 Registering demo enchantments...")
        
        # Basic Fire Enchantment
        register_enchantment(EnchantmentDefinition(
            id="demo_flame_weapon",
            name="Flame Weapon",
            description="Weapon deals additional 1d6 fire damage",
            rarity=EnchantmentRarity.BASIC,
            school=EnchantmentSchool.ELEMENTAL,
            min_arcane_manipulation=2,
            base_cost=300,
            min_item_quality="basic",
            compatible_item_types={"weapon"},
            thematic_tags={"fire", "damage", "elemental"}
        ))
        
        # Military Protection Enchantment
        register_enchantment(EnchantmentDefinition(
            id="demo_mage_armor",
            name="Mage Armor",
            description="Provides +2 AC and spell resistance",
            rarity=EnchantmentRarity.MILITARY,
            school=EnchantmentSchool.PROTECTION,
            min_arcane_manipulation=5,
            base_cost=800,
            min_item_quality="military",
            compatible_item_types={"armor", "robes"},
            thematic_tags={"protection", "magic", "defense"}
        ))
        
        # Noble Utility Enchantment
        register_enchantment(EnchantmentDefinition(
            id="demo_teleport_boots",
            name="Boots of Teleportation",
            description="Allows short-range teleportation 3 times per day",
            rarity=EnchantmentRarity.NOBLE,
            school=EnchantmentSchool.UTILITY,
            min_arcane_manipulation=7,
            base_cost=2000,
            min_item_quality="noble",
            compatible_item_types={"boots"},
            thematic_tags={"teleportation", "movement", "utility"}
        ))
        
        print("✅ Demo enchantments registered!")
    
    def create_demo_equipment(self) -> dict:
        """Create sample equipment items for the demo."""
        print("🔨 Creating demo equipment...")
        
        # Create an enchanted sword to disenchant
        enchanted_sword_data = {
            "name": "Burning Blade of the Fire Lord",
            "description": "A magnificent sword wreathed in flames",
            "equipment_type": "weapon",
            "rarity": "rare",
            "quality": "military",
            "base_value": 5000,
            "enchantments": ["demo_flame_weapon"],  # Pre-enchanted for disenchanting
            "set_name": "Fire Lord's Arsenal"
        }
        
        enchanted_sword_id = self.equipment_repo.create_equipment(enchanted_sword_data)
        
        # Create a plain armor to enchant later
        plain_armor_data = {
            "name": "Apprentice Robes",
            "description": "Simple robes worn by magic apprentices",
            "equipment_type": "armor", 
            "rarity": "common",
            "quality": "military",
            "base_value": 1200,
            "enchantments": [],  # No enchantments yet
        }
        
        plain_armor_id = self.equipment_repo.create_equipment(plain_armor_data)
        
        # Create noble boots for advanced enchanting
        noble_boots_data = {
            "name": "Archmage's Traveling Boots",
            "description": "Finely crafted boots worn by powerful mages",
            "equipment_type": "boots",
            "rarity": "epic", 
            "quality": "noble",
            "base_value": 8000,
            "enchantments": ["demo_teleport_boots"],  # Pre-enchanted
        }
        
        noble_boots_id = self.equipment_repo.create_equipment(noble_boots_data)
        
        # Assign equipment to character
        self.equipment_repo.assign_equipment_to_character(enchanted_sword_id, str(self.character_id))
        self.equipment_repo.assign_equipment_to_character(plain_armor_id, str(self.character_id))
        self.equipment_repo.assign_equipment_to_character(noble_boots_id, str(self.character_id))
        
        equipment_items = {
            "enchanted_sword": {
                "id": enchanted_sword_id,
                "data": self.equipment_repo.get_equipment_by_id(enchanted_sword_id)
            },
            "plain_armor": {
                "id": plain_armor_id,
                "data": self.equipment_repo.get_equipment_by_id(plain_armor_id)
            },
            "noble_boots": {
                "id": noble_boots_id,
                "data": self.equipment_repo.get_equipment_by_id(noble_boots_id)
            }
        }
        
        print("✅ Demo equipment created!")
        return equipment_items
    
    def demonstrate_disenchanting(self, equipment_items: dict):
        """Demonstrate the disenchanting process."""
        print("\n🔥 === DISENCHANTING DEMONSTRATION ===")
        
        # Get character's enchanting profile
        profile = self.enchanting_service.get_character_profile(self.character_id)
        print(f"📊 Current enchantments known: {len(profile.learned_enchantments)}")
        
        # Attempt to disenchant the burning blade
        sword = equipment_items["enchanted_sword"]
        print(f"\n🗡️  Attempting to disenchant: {sword['data']['name']}")
        print(f"   Enchantments: {sword['data']['enchantments']}")
        
        # Perform disenchantment
        attempt = self.enchanting_service.attempt_disenchantment(
            character_id=self.character_id,
            item_id=UUID(sword['id']),
            item_data=sword['data'],
            arcane_manipulation_level=3,  # Moderate skill level
            character_level=8
        )
        
        print(f"   Result: {attempt.outcome.value}")
        print(f"   Item destroyed: {attempt.item_destroyed}")
        print(f"   Experience gained: {attempt.experience_gained}")
        
        if attempt.enchantment_learned:
            learned_enchantment = get_enchantment_definition(attempt.enchantment_learned)
            print(f"   🎉 Learned enchantment: {learned_enchantment.name}")
            print(f"   📖 Description: {learned_enchantment.description}")
        
        if attempt.additional_consequences:
            print(f"   ⚠️  Additional consequences: {', '.join(attempt.additional_consequences)}")
        
        # Record the attempt
        self.enchanting_repo.record_disenchantment_attempt(attempt)
        
        # Now try the noble boots (harder enchantment)
        boots = equipment_items["noble_boots"]
        print(f"\n👢 Attempting to disenchant: {boots['data']['name']}")
        print(f"   Enchantments: {boots['data']['enchantments']}")
        
        boots_attempt = self.enchanting_service.attempt_disenchantment(
            character_id=self.character_id,
            item_id=UUID(boots['id']),
            item_data=boots['data'],
            arcane_manipulation_level=3,  # Same skill, but harder enchantment
            character_level=8
        )
        
        print(f"   Result: {boots_attempt.outcome.value}")
        print(f"   Item destroyed: {boots_attempt.item_destroyed}")
        
        if boots_attempt.enchantment_learned:
            learned_enchantment = get_enchantment_definition(boots_attempt.enchantment_learned)
            print(f"   🎉 Learned enchantment: {learned_enchantment.name}")
        else:
            print(f"   😞 No enchantment learned this time")
        
        self.enchanting_repo.record_disenchantment_attempt(boots_attempt)
        
        # Show updated profile
        updated_profile = self.enchanting_service.get_character_profile(self.character_id)
        print(f"\n📊 Updated enchantments known: {len(updated_profile.learned_enchantments)}")
        for enchantment_id, learned_enchantment in updated_profile.learned_enchantments.items():
            enchantment_def = get_enchantment_definition(enchantment_id)
            print(f"   - {enchantment_def.name} (Mastery: {learned_enchantment.mastery_level})")
    
    def demonstrate_enchanting(self, equipment_items: dict):
        """Demonstrate applying learned enchantments to equipment."""
        print("\n✨ === ENCHANTMENT APPLICATION DEMONSTRATION ===")
        
        # Check what enchantments we can apply to the plain armor
        armor = equipment_items["plain_armor"]
        available_enchantments = self.enchanting_service.get_available_enchantments_for_item(
            character_id=self.character_id,
            item_data=armor['data']
        )
        
        print(f"🛡️  Target item: {armor['data']['name']}")
        print(f"   Available enchantments: {len(available_enchantments)}")
        
        for enchantment in available_enchantments:
            print(f"   - {enchantment['name']} (Cost: {enchantment['cost']} gold)")
        
        # Apply an enchantment if any are available
        if available_enchantments:
            chosen_enchantment = available_enchantments[0]
            print(f"\n🎯 Applying: {chosen_enchantment['name']}")
            
            application = self.enchanting_service.attempt_enchantment(
                character_id=self.character_id,
                item_id=UUID(armor['id']),
                item_data=armor['data'],
                enchantment_id=chosen_enchantment['enchantment_id'],
                gold_available=10000  # Plenty of gold for demo
            )
            
            print(f"   Result: {'Success' if application.success else 'Failed'}")
            print(f"   Cost paid: {application.cost_paid} gold")
            
            if application.success:
                print(f"   Power level: {application.final_power_level}%")
                
                # Apply the enchantment to the actual item
                self.equipment_repo.apply_enchantment_to_item(
                    armor['id'],
                    chosen_enchantment['enchantment_id'],
                    application.final_power_level
                )
                
                # Show updated item
                updated_armor = self.equipment_repo.get_equipment_by_id(armor['id'])
                print(f"   ✅ Item successfully enchanted!")
                print(f"   Applied enchantments: {len(updated_armor['applied_enchantments'])}")
            else:
                print(f"   ❌ Failed: {application.failure_reason}")
                if application.materials_lost:
                    print(f"   💸 Materials were lost in the failed attempt")
            
            # Record the application
            self.enchanting_repo.record_enchantment_application(application)
        else:
            print("   No enchantments available to apply (need to learn some first!)")
    
    def show_character_progression(self):
        """Show the character's enchanting progression."""
        print("\n📈 === CHARACTER ENCHANTING PROGRESSION ===")
        
        profile = self.enchanting_service.get_character_profile(self.character_id)
        stats = self.enchanting_repo.get_character_statistics(self.character_id)
        
        print(f"🧙‍♀️ {self.character_name}'s Enchanting Profile:")
        print(f"   Total items disenchanted: {stats['total_items_disenchanted']}")
        print(f"   Total enchantments learned: {stats['total_enchantments_learned']}")
        print(f"   Successful applications: {stats['successful_applications']}")
        print(f"   Failed applications: {stats['failed_applications']}")
        print(f"   Disenchantment success rate: {stats['disenchantment_success_rate']:.1f}%")
        print(f"   Application success rate: {stats['application_success_rate']:.1f}%")
        
        if stats['preferred_school']:
            print(f"   Preferred school: {stats['preferred_school']}")
        
        if stats['schools_learned']:
            print(f"   Schools mastered:")
            for school, count in stats['schools_learned'].items():
                print(f"     - {school.title()}: {count} enchantments")
        
        # Show recent activity
        disenchantment_history = self.enchanting_repo.get_disenchantment_history(self.character_id, 5)
        if disenchantment_history:
            print(f"\n🔥 Recent disenchantment attempts:")
            for attempt in disenchantment_history:
                timestamp = datetime.fromisoformat(attempt['timestamp']).strftime("%H:%M:%S")
                print(f"   [{timestamp}] {attempt['item_name']} - {attempt['outcome']}")
        
        application_history = self.enchanting_repo.get_application_history(self.character_id, 5)
        if application_history:
            print(f"\n✨ Recent enchantment applications:")
            for app in application_history:
                timestamp = datetime.fromisoformat(app['timestamp']).strftime("%H:%M:%S")
                status = "Success" if app['success'] else "Failed"
                print(f"   [{timestamp}] {app['enchantment_id']} - {status}")
    
    def show_equipment_overview(self):
        """Show the character's equipment status."""
        print("\n🎒 === EQUIPMENT OVERVIEW ===")
        
        equipment_list = self.equipment_repo.get_character_equipment(str(self.character_id))
        
        print(f"📦 {self.character_name}'s Equipment ({len(equipment_list)} items):")
        
        for equipment in equipment_list:
            print(f"\n🔹 {equipment['name']}")
            print(f"   Type: {equipment['equipment_type']} | Quality: {equipment['quality']} | Rarity: {equipment['rarity']}")
            print(f"   Durability: {equipment['durability']:.1f}% ({equipment['durability_status']})")
            print(f"   Value: {equipment['current_value']} gold")
            
            if equipment.get('applied_enchantments'):
                print(f"   🌟 Applied enchantments:")
                for ench in equipment['applied_enchantments']:
                    print(f"     - {ench['enchantment_name']} (Power: {ench['power_level']}%)")
            
            if equipment.get('revealed_abilities'):
                print(f"   ⚡ Revealed abilities: {len(equipment['revealed_abilities'])}")
            
            if equipment.get('hidden_ability_count', 0) > 0:
                print(f"   🔒 Hidden abilities: {equipment['hidden_ability_count']}")
    
    def run_demo(self):
        """Run the complete enchanting system demo."""
        try:
            # Setup
            self.register_demo_enchantments()
            equipment_items = self.create_demo_equipment()
            
            # Demonstrate the core features
            self.demonstrate_disenchanting(equipment_items)
            self.demonstrate_enchanting(equipment_items)
            
            # Show results
            self.show_character_progression()
            self.show_equipment_overview()
            
            print("\n🎉 === DEMO COMPLETE ===")
            print("The enchanting system successfully demonstrated:")
            print("✅ Learn-by-disenchanting mechanics")
            print("✅ Risk/reward progression system")
            print("✅ Enchantment application with mastery")
            print("✅ Equipment durability and quality integration")
            print("✅ Character progression tracking")
            print("✅ Data persistence and history")
            
            print(f"\n💾 Demo data saved to: demo_data/")
            print("You can inspect the generated JSON files to see the data structures!")
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Run the enchanting demo."""
    demo = EnchantingSystemDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 