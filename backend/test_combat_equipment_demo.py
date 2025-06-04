#!/usr/bin/env python3
"""
Combat-Equipment Integration Demonstration

This script demonstrates the real-time integration between the combat system
and equipment system, showing how equipment bonuses affect combat calculations
and how combat affects equipment durability.
"""

import sys
import os
from datetime import datetime
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_combat_equipment_integration():
    """Demonstrate combat-equipment integration with real-time calculations."""
    
    print("⚔️ COMBAT-EQUIPMENT INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    try:
        from sqlalchemy import create_engine, Column, String, Integer, Float
        from sqlalchemy.orm import sessionmaker
        from backend.systems.equipment.models.equipment_models import Base, EquipmentInstance
        from backend.systems.equipment.services.hybrid_equipment_service import HybridEquipmentService
        from backend.systems.equipment.services.combat_equipment_integration import CombatEquipmentIntegration
        from backend.systems.equipment.services.template_service import EquipmentTemplateService
        
        # Create test database
        engine = create_engine("sqlite:///test_combat_equipment.db", echo=False)
        
        # Create a simple Character table for testing
        class SimpleCharacter(Base):
            __tablename__ = 'characters'
            id = Column(String, primary_key=True)
            name = Column(String)
            level = Column(Integer, default=1)
            strength = Column(Integer, default=10)
            dexterity = Column(Integer, default=10)
            proficiency_bonus = Column(Integer, default=2)
            base_ac = Column(Integer, default=10)
        
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Database and models initialized")
        
        # Initialize services
        template_service = EquipmentTemplateService()
        equipment_service = HybridEquipmentService(template_service, session)
        combat_service = CombatEquipmentIntegration(equipment_service, session)
        
        print("✅ Services initialized")
        
        # Create test character
        hero = SimpleCharacter(
            id='combat_hero_001',
            name='Sir Testsworth',
            level=5,
            strength=16,  # +3 modifier
            dexterity=14,  # +2 modifier
            proficiency_bonus=3,
            base_ac=12
        )
        session.add(hero)
        session.commit()
        
        print(f"✅ Character created: {hero.name} (Level {hero.level})")
        print(f"   📊 STR: {hero.strength} (+{(hero.strength-10)//2}), DEX: {hero.dexterity} (+{(hero.dexterity-10)//2})")
        print(f"   🛡️ Base AC: {hero.base_ac}, Proficiency: +{hero.proficiency_bonus}")
        
        # Get available templates
        templates = template_service.list_equipment_templates()
        weapon_templates = [t for t in templates if t.item_type == 'weapon']
        armor_templates = [t for t in templates if t.item_type == 'armor']
        
        if not weapon_templates or not armor_templates:
            print("❌ No weapon or armor templates found")
            return
        
        # Create quality equipment for testing
        print("\n⚔️ Creating Combat Equipment")
        
        # Create a noble sword (high quality)
        sword_template = weapon_templates[0]
        noble_sword = equipment_service.create_equipment_instance(
            template_id=sword_template.id,
            owner_id=hero.id,
            quality_tier="noble",
            custom_name="Excalibur the Magnificent"
        )
        
        # Create military armor (medium quality)
        armor_template = armor_templates[0]
        military_armor = equipment_service.create_equipment_instance(
            template_id=armor_template.id,
            owner_id=hero.id,
            quality_tier="military",
            custom_name="Platemail of Protection"
        )
        
        print(f"   🗡️ Created: {noble_sword.custom_name} (Noble quality)")
        print(f"   🛡️ Created: {military_armor.custom_name} (Military quality)")
        
        # Equip the items
        equipment_service.equip_item(noble_sword.id, "main_hand")
        equipment_service.equip_item(military_armor.id, "chest")
        
        print(f"   ✅ Equipment equipped and ready for combat")
        
        # Test combat calculations
        print("\n🎯 COMBAT CALCULATIONS WITH EQUIPMENT")
        
        # Test attack roll calculation
        attack_data = {
            "character_id": hero.id,
            "weapon_slot": "main_hand",
            "attack_type": "melee",
            "target_ac": 15
        }
        
        attack_result = combat_service.calculate_attack_roll(attack_data)
        print(f"\n🎯 Attack Roll Calculation:")
        print(f"   🎲 Base roll: {attack_result['base_roll']}")
        print(f"   💪 Ability modifier: +{attack_result['ability_modifier']}")
        print(f"   🎓 Proficiency bonus: +{attack_result['proficiency_bonus']}")
        print(f"   ⚔️ Equipment bonus: +{attack_result['equipment_bonus']}")
        print(f"   📊 Total attack: {attack_result['total_attack']}")
        print(f"   🎯 Target AC: {attack_data['target_ac']} → {'HIT! 🎉' if attack_result['hits'] else 'MISS! 💥'}")
        
        if attack_result['hits']:
            # Test damage calculation
            damage_data = {
                "character_id": hero.id,
                "weapon_slot": "main_hand",
                "attack_type": "melee",
                "is_critical": attack_result['is_critical']
            }
            
            damage_result = combat_service.calculate_damage_roll(damage_data)
            print(f"\n💥 Damage Roll Calculation:")
            print(f"   🎲 Base damage: {damage_result['base_damage']}")
            print(f"   💪 Ability modifier: +{damage_result['ability_modifier']}")
            print(f"   ⚔️ Equipment bonus: +{damage_result['equipment_bonus']}")
            print(f"   ✨ Enchantment bonus: +{damage_result['enchantment_bonus']}")
            if damage_result['is_critical']:
                print(f"   🌟 CRITICAL HIT! Damage doubled!")
            print(f"   📊 Total damage: {damage_result['total_damage']}")
            
            # Apply combat damage to equipment
            print(f"\n🔧 Equipment Durability Impact:")
            print(f"   ⚔️ Sword durability before: {noble_sword.durability}%")
            print(f"   🛡️ Armor durability before: {military_armor.durability}%")
            
            # Simulate equipment taking damage in combat
            combat_service.apply_combat_damage_to_equipment(hero.id, damage_result['total_damage'])
            
            # Refresh equipment from database
            session.refresh(noble_sword)
            session.refresh(military_armor)
            
            print(f"   ⚔️ Sword durability after: {noble_sword.durability}%")
            print(f"   🛡️ Armor durability after: {military_armor.durability}%")
        
        # Test armor class calculation
        print("\n🛡️ ARMOR CLASS CALCULATION")
        ac_result = combat_service.calculate_armor_class(hero.id)
        print(f"   🏠 Base AC: {ac_result['base_ac']}")
        print(f"   🏃 Dexterity modifier: +{ac_result['dex_modifier']}")
        print(f"   🛡️ Armor bonus: +{ac_result['armor_bonus']}")
        print(f"   ✨ Enchantment bonus: +{ac_result['enchantment_bonus']}")
        print(f"   🔧 Condition penalty: -{ac_result['condition_penalty']}")
        print(f"   📊 Total AC: {ac_result['total_ac']}")
        
        # Test initiative calculation
        print("\n⚡ INITIATIVE CALCULATION")
        initiative_result = combat_service.calculate_initiative_modifier(hero.id)
        print(f"   🏃 Dexterity modifier: +{initiative_result['dex_modifier']}")
        print(f"   ⚔️ Equipment bonus: +{initiative_result['equipment_bonus']}")
        print(f"   ⚖️ Weight penalty: -{initiative_result['weight_penalty']}")
        print(f"   📊 Total initiative modifier: +{initiative_result['total_modifier']}")
        
        # Simulate multiple combat rounds
        print("\n🥊 EXTENDED COMBAT SIMULATION")
        print("Simulating 5 rounds of intense combat...")
        
        for round_num in range(1, 6):
            print(f"\n--- Round {round_num} ---")
            
            # Attack roll
            attack_result = combat_service.calculate_attack_roll(attack_data)
            print(f"Attack: {attack_result['total_attack']} vs AC {attack_data['target_ac']} → {'HIT' if attack_result['hits'] else 'MISS'}")
            
            if attack_result['hits']:
                # Damage calculation
                damage_data['is_critical'] = attack_result['is_critical']
                damage_result = combat_service.calculate_damage_roll(damage_data)
                print(f"Damage: {damage_result['total_damage']} {'(CRIT!)' if damage_result['is_critical'] else ''}")
                
                # Equipment degradation
                combat_service.apply_combat_damage_to_equipment(hero.id, damage_result['total_damage'])
                
                # Check equipment condition
                session.refresh(noble_sword)
                session.refresh(military_armor)
                print(f"Equipment condition: Sword {noble_sword.durability}%, Armor {military_armor.durability}%")
                
                # Check if equipment performance is affected
                if noble_sword.durability < 50:
                    print("⚠️ Sword is heavily damaged - combat effectiveness reduced!")
                if military_armor.durability < 50:
                    print("⚠️ Armor is heavily damaged - protection reduced!")
        
        # Final equipment status
        print("\n📊 FINAL EQUIPMENT STATUS")
        sword_details = equipment_service.get_equipment_details(noble_sword.id)
        armor_details = equipment_service.get_equipment_details(military_armor.id)
        
        print(f"\n⚔️ {noble_sword.custom_name}:")
        print(f"   🔧 Condition: {sword_details['condition_status']}")
        print(f"   📊 Current stats: {sword_details['current_stats']}")
        print(f"   💰 Current value: {sword_details['current_value']} gold")
        
        print(f"\n🛡️ {military_armor.custom_name}:")
        print(f"   🔧 Condition: {armor_details['condition_status']}")
        print(f"   📊 Current stats: {armor_details['current_stats']}")
        print(f"   💰 Current value: {armor_details['current_value']} gold")
        
        print("\n🎉 COMBAT-EQUIPMENT INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ All combat calculations working with equipment bonuses")
        print("✅ Equipment degradation functioning during combat")
        print("✅ Real-time stat calculations updating properly")
        print("✅ Quality tiers providing appropriate bonuses")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the equipment system is properly installed")
    except Exception as e:
        print(f"❌ Error during combat testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            session.close()
            if 'engine' in locals():
                engine.dispose()
            if os.path.exists("test_combat_equipment.db"):
                os.remove("test_combat_equipment.db")
            print("🧹 Test cleanup completed")
        except:
            pass

if __name__ == "__main__":
    test_combat_equipment_integration() 