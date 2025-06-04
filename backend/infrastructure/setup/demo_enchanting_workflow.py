#!/usr/bin/env python3
"""
Enhanced Enchanting/Disenchanting Workflow Demonstration

This script demonstrates the complete enchanting lifecycle:
1. Learning enchantments through disenchanting
2. Applying enchantments to equipment
3. Managing enchantment materials and costs
4. Progression and mastery systems
5. Failure scenarios and consequences
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# Database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our models and services
from backend.systems.equipment.models.equipment_models import Base, EquipmentInstance
from backend.systems.equipment.models.enchanting import LearnedEnchantment, DisenchantmentAttempt
from backend.systems.equipment.services.hybrid_equipment_service import HybridEquipmentService
from backend.systems.equipment.services.enchanting_service import EnchantingService
from backend.systems.equipment.services.equipment_quality import EquipmentQualityService

# Create SQLAlchemy models for the demo
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Simple Character model for the demo
class DemoCharacter(Base):
    """Simple character model for enchanting demo."""
    __tablename__ = 'demo_characters'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    arcane_manipulation = Column(Integer, default=1)
    gold = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# SQLAlchemy models for enchanting system
class LearnedEnchantmentModel(Base):
    """SQLAlchemy model for learned enchantments."""
    __tablename__ = 'learned_enchantments'
    
    id = Column(String, primary_key=True)
    character_id = Column(String, nullable=False)
    enchantment_id = Column(String, nullable=False)
    learned_from_item = Column(String, nullable=False)
    mastery_level = Column(Integer, default=1)
    times_applied = Column(Integer, default=0)
    learned_at = Column(DateTime, default=datetime.utcnow)

class DisenchantmentAttemptModel(Base):
    """SQLAlchemy model for disenchantment attempts."""
    __tablename__ = 'disenchantment_attempts'
    
    id = Column(String, primary_key=True)
    character_id = Column(String, nullable=False)
    item_template_id = Column(String, nullable=False)
    target_enchantment_id = Column(String, nullable=False)
    character_skill_level = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    item_destroyed = Column(Boolean, default=False)
    enchantment_learned = Column(String, nullable=True)
    attempt_time = Column(DateTime, default=datetime.utcnow)

class EnchantingWorkflowDemo:
    """Demonstrates the complete enchanting workflow."""
    
    def __init__(self):
        # Setup demo database
        self.engine = create_engine("sqlite:///demo_enchanting.db", echo=False)
        Base.metadata.create_all(self.engine)
        
        # Create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Initialize services
        self.quality_service = EquipmentQualityService()
        self.enchanting_service = EnchantingService(self.quality_service)
        self.equipment_service = HybridEquipmentService(self.session)
        
        # Demo character
        self.character_id = "enchanter_demo_001"
        self.character_name = "Lyria the Enchantress"
        self.setup_demo_character()
        
    def setup_demo_character(self):
        """Create a demo character for enchanting."""
        character = DemoCharacter(
            id=self.character_id,
            name=self.character_name,
            arcane_manipulation=8,  # High enough for most enchantments
            gold=10000,  # Enough for experiments
            created_at=datetime.utcnow()
        )
        
        # Add to session if not exists
        existing = self.session.query(DemoCharacter).filter_by(id=self.character_id).first()
        if not existing:
            self.session.add(character)
            self.session.commit()
            
    def print_header(self, title: str):
        """Print a styled header."""
        print(f"\n🔮 {title.upper()}")
        print("=" * 70)
        
    def print_subheader(self, title: str):
        """Print a styled subheader."""
        print(f"\n✨ {title}")
        print("-" * 50)
        
    def demonstrate_learning_progression(self):
        """Show how enchantments are learned through disenchanting."""
        self.print_header("ENCHANTMENT LEARNING PROGRESSION")
        
        # Start with no known enchantments
        known_enchantments = self.session.query(LearnedEnchantmentModel)\
            .filter_by(character_id=self.character_id).all()
        print(f"📚 Starting with {len(known_enchantments)} known enchantments")
        
        # Simulate disenchanting different items to learn enchantments
        learning_scenarios = [
            {
                "item_name": "Flame-touched Dagger",
                "enchantment": "flame_weapon",
                "success": True,
                "description": "A basic weapon with fire enchantment"
            },
            {
                "item_name": "Frost-kissed Shortsword", 
                "enchantment": "frost_weapon",
                "success": True,
                "description": "Another basic elemental weapon"
            },
            {
                "item_name": "Keen Elven Blade",
                "enchantment": "keen_edge",
                "success": False,  # First failure
                "description": "A more complex enhancement enchantment"
            },
            {
                "item_name": "Another Keen Weapon",
                "enchantment": "keen_edge", 
                "success": True,  # Success on retry
                "description": "Second attempt at keen edge"
            },
            {
                "item_name": "Shadow Cloak",
                "enchantment": "shadow_cloak",
                "success": True,
                "description": "Utility enchantment on armor"
            }
        ]
        
        for i, scenario in enumerate(learning_scenarios, 1):
            self.print_subheader(f"Disenchantment Attempt #{i}")
            print(f"🗡️ Item: {scenario['item_name']}")
            print(f"📜 Target Enchantment: {scenario['enchantment']}")
            print(f"📖 Description: {scenario['description']}")
            
            # Create disenchantment attempt record
            attempt = DisenchantmentAttemptModel(
                id=str(uuid.uuid4()),
                character_id=self.character_id,
                item_template_id=f"demo_{scenario['enchantment']}_item",
                target_enchantment_id=scenario['enchantment'],
                character_skill_level=self.get_character_skill(),
                success=scenario['success'],
                item_destroyed=scenario['success'],  # Item destroyed on success
                enchantment_learned=scenario['enchantment'] if scenario['success'] else None,
                attempt_time=datetime.utcnow() - timedelta(days=i)
            )
            
            self.session.add(attempt)
            
            if scenario['success']:
                # Learn the enchantment
                learned = LearnedEnchantmentModel(
                    id=str(uuid.uuid4()),
                    character_id=self.character_id,
                    enchantment_id=scenario['enchantment'],
                    learned_from_item=f"demo_{scenario['enchantment']}_item",
                    mastery_level=1,
                    times_applied=0,
                    learned_at=datetime.utcnow() - timedelta(days=i)
                )
                self.session.add(learned)
                print(f"   ✅ SUCCESS! Learned '{scenario['enchantment']}'")
                print(f"   🔥 Item destroyed in the process")
            else:
                print(f"   ❌ FAILED! Item destroyed, enchantment not learned")
                print(f"   💡 Need more practice or better conditions")
            
        self.session.commit()
        
        # Show final learned enchantments
        learned_enchantments = self.session.query(LearnedEnchantmentModel)\
            .filter_by(character_id=self.character_id).all()
        
        print(f"\n📚 Final Knowledge: {len(learned_enchantments)} enchantments learned")
        for learned in learned_enchantments:
            print(f"   • {learned.enchantment_id} (Mastery: {learned.mastery_level})")
            
    def demonstrate_enchanting_process(self):
        """Show the complete enchanting process."""
        self.print_header("ENCHANTING PROCESS DEMONSTRATION")
        
        # Create some equipment to enchant
        equipment_items = []
        
        # Create a sword
        sword = self.equipment_service.create_equipment_instance(
            template_id="iron_sword",
            owner_id=self.character_id,
            custom_name="Apprentice's Blade"
        )
        equipment_items.append(sword)
        
        # Create armor
        armor = self.equipment_service.create_equipment_instance(
            template_id="leather_armor", 
            owner_id=self.character_id,
            custom_name="Training Leathers"
        )
        equipment_items.append(armor)
        
        print(f"🗡️ Created {len(equipment_items)} items for enchanting")
        for item in equipment_items:
            print(f"   • {item.custom_name or 'Unnamed'} ({item.template_id})")
            
        # Enchanting scenarios
        enchanting_scenarios = [
            {
                "item": sword,
                "enchantment": "flame_weapon",
                "expected_success": True,
                "description": "Basic fire enchantment on weapon"
            },
            {
                "item": armor,
                "enchantment": "shadow_cloak",
                "expected_success": True,
                "description": "Stealth enchantment on armor"
            },
            {
                "item": sword,
                "enchantment": "keen_edge", 
                "expected_success": True,
                "description": "Adding second enchantment to sword"
            }
        ]
        
        for i, scenario in enumerate(enchanting_scenarios, 1):
            self.print_subheader(f"Enchantment Application #{i}")
            
            item = scenario["item"]
            enchantment_id = scenario["enchantment"]
            
            print(f"🎯 Target: {item.custom_name}")
            print(f"✨ Enchantment: {enchantment_id}")
            print(f"📝 Description: {scenario['description']}")
            
            # Check if character knows this enchantment
            known = self.session.query(LearnedEnchantmentModel).filter_by(
                character_id=self.character_id,
                enchantment_id=enchantment_id
            ).first()
            
            if not known:
                print(f"   ❌ Character doesn't know {enchantment_id}!")
                continue
                
            # Show costs and requirements
            enchantment_info = self.enchanting_service.get_enchantment_info(enchantment_id)
            if enchantment_info:
                cost = enchantment_info.get('base_cost', 0)
                materials = enchantment_info.get('materials_required', {})
                print(f"   💰 Base Cost: {cost}g")
                print(f"   🧪 Materials: {materials}")
                
            # Simulate enchanting
            success = scenario["expected_success"]
            if success:
                print(f"   ✅ Enchantment applied successfully!")
                print(f"   ✨ {item.custom_name} now glows with magical energy")
                
                # Update mastery
                known.times_applied += 1
                if known.times_applied % 5 == 0:  # Mastery increases every 5 applications
                    known.mastery_level += 1
                    print(f"   🎓 Mastery increased! Now level {known.mastery_level}")
            else:
                print(f"   ❌ Enchantment failed!")
                print(f"   💥 Materials consumed, no effect applied")
                
        self.session.commit()
        
    def demonstrate_enchantment_materials(self):
        """Show enchantment material system."""
        self.print_header("ENCHANTMENT MATERIALS SYSTEM")
        
        # Load material information from enchantments config
        materials_info = {
            "fire_essence": {"name": "Fire Essence", "value": 50, "rarity": "common"},
            "ice_essence": {"name": "Ice Essence", "value": 50, "rarity": "common"},
            "enchanting_dust": {"name": "Enchanting Dust", "value": 10, "rarity": "basic"},
            "shadow_essence": {"name": "Shadow Essence", "value": 200, "rarity": "rare"},
            "restoration_crystal": {"name": "Restoration Crystal", "value": 500, "rarity": "rare"},
            "spirit_essence": {"name": "Spirit Essence", "value": 2000, "rarity": "legendary"},
        }
        
        print("🧪 ENCHANTMENT MATERIALS DATABASE")
        print("-" * 50)
        
        for material_id, info in materials_info.items():
            rarity_color = {
                "basic": "⚪", "common": "🟢", "rare": "🔵", 
                "epic": "🟣", "legendary": "🟡"
            }.get(info["rarity"], "⚪")
            
            print(f"{rarity_color} {info['name']}")
            print(f"   💰 Value: {info['value']}g")
            print(f"   🎯 Rarity: {info['rarity']}")
            
        print("\n🔮 MATERIAL USAGE IN ENCHANTMENTS")
        print("-" * 50)
        
        # Show which enchantments need which materials
        enchantment_materials = {
            "flame_weapon": ["fire_essence", "enchanting_dust"],
            "frost_weapon": ["ice_essence", "enchanting_dust"], 
            "shadow_cloak": ["shadow_essence", "enchanting_dust"],
            "repair_self": ["restoration_crystal", "enchanting_dust"],
            "dancing_blade": ["spirit_essence", "enchanting_dust"]
        }
        
        for enchantment, materials in enchantment_materials.items():
            print(f"✨ {enchantment}:")
            total_cost = 0
            for material in materials:
                if material in materials_info:
                    cost = materials_info[material]["value"]
                    total_cost += cost
                    print(f"   • {materials_info[material]['name']}: {cost}g")
            print(f"   💰 Total Material Cost: {total_cost}g")
            print()
            
    def demonstrate_mastery_progression(self):
        """Show enchantment mastery and progression."""
        self.print_header("MASTERY PROGRESSION SYSTEM")
        
        learned_enchantments = self.session.query(LearnedEnchantmentModel)\
            .filter_by(character_id=self.character_id).all()
            
        print("🎓 CHARACTER ENCHANTMENT MASTERY")
        print("-" * 50)
        
        for learned in learned_enchantments:
            mastery_benefits = self.calculate_mastery_benefits(learned.mastery_level)
            applications_to_next = self.applications_to_next_mastery(learned.times_applied)
            
            print(f"✨ {learned.enchantment_id}")
            print(f"   🎯 Mastery Level: {learned.mastery_level}/10")
            print(f"   🔄 Times Applied: {learned.times_applied}")
            print(f"   📈 To Next Level: {applications_to_next} more applications")
            print(f"   💪 Current Benefits:")
            for benefit, value in mastery_benefits.items():
                print(f"      • {benefit}: {value}")
            print()
            
    def demonstrate_failure_scenarios(self):
        """Show various enchanting failure scenarios."""
        self.print_header("ENCHANTING FAILURE SCENARIOS")
        
        failure_scenarios = [
            {
                "reason": "Insufficient Arcane Manipulation",
                "description": "Character skill too low for advanced enchantments",
                "example": "Trying to apply 'dancing_blade' with only 5 skill",
                "consequence": "Automatic failure, materials lost"
            },
            {
                "reason": "Incompatible Item Type",
                "description": "Enchantment not compatible with item",
                "example": "Trying to put 'flame_weapon' on armor",
                "consequence": "Operation rejected before attempt"
            },
            {
                "reason": "Insufficient Materials",
                "description": "Missing required enchanting materials",
                "example": "No 'fire_essence' for flame enchantment",
                "consequence": "Cannot begin enchanting process"
            },
            {
                "reason": "Bad Luck Roll",
                "description": "Random failure despite meeting requirements",
                "example": "Flame weapon fails 15% of the time",
                "consequence": "Materials consumed, no effect applied"
            },
            {
                "reason": "Item Quality Too Low",
                "description": "Item quality below enchantment minimum",
                "example": "Trying noble enchantment on basic item",
                "consequence": "Higher failure chance or rejection"
            }
        ]
        
        for i, scenario in enumerate(failure_scenarios, 1):
            print(f"❌ Failure Type #{i}: {scenario['reason']}")
            print(f"   📝 Description: {scenario['description']}")
            print(f"   🎯 Example: {scenario['example']}")
            print(f"   💥 Consequence: {scenario['consequence']}")
            print()
            
    def demonstrate_advanced_features(self):
        """Show advanced enchanting features."""
        self.print_header("ADVANCED ENCHANTING FEATURES")
        
        self.print_subheader("Enchantment Compatibility")
        print("🔗 Equipment can have multiple compatible enchantments:")
        print("   • Weapons: flame_weapon + keen_edge + weapon_light")
        print("   • Armor: armor_reinforcement + shadow_cloak + repair_self")
        print("   • Accessories: greater_protection + haste")
        print()
        
        self.print_subheader("School Synergies")
        print("🏫 Enchantments from same school work better together:")
        print("   • Elemental: flame + frost + shock for tri-element damage")
        print("   • Protective: armor_reinforcement + greater_protection stack")
        print("   • Enhancement: keen_edge + seeking_arrows for perfect accuracy")
        print()
        
        self.print_subheader("Quality Tier Restrictions")
        print("👑 Higher-tier enchantments require better items:")
        print("   • Basic items: Basic enchantments only")
        print("   • Military items: Basic + Common enchantments")
        print("   • Noble items: All enchantment tiers available")
        print()
        
        self.print_subheader("Learning Prerequisites")
        print("📚 Some enchantments require knowing others first:")
        print("   • keen_edge requires weapon_light")
        print("   • dancing_blade requires weapon_light + keen_edge")
        print("   • greater_protection requires armor_reinforcement")
        print()
        
    def get_character_skill(self) -> int:
        """Get character's arcane manipulation skill."""
        character = self.session.query(DemoCharacter).filter_by(id=self.character_id).first()
        return character.arcane_manipulation if character else 1
        
    def calculate_mastery_benefits(self, mastery_level: int) -> Dict[str, str]:
        """Calculate benefits of mastery level."""
        return {
            "Success Rate Bonus": f"+{mastery_level * 5}%",
            "Cost Reduction": f"-{mastery_level * 2}%",
            "Effect Strength": f"+{mastery_level * 10}%",
            "Material Efficiency": f"-{mastery_level}% materials"
        }
        
    def applications_to_next_mastery(self, current_applications: int) -> int:
        """Calculate applications needed for next mastery level."""
        # Simple progression: 5 applications per level
        current_level = current_applications // 5
        next_level_threshold = (current_level + 1) * 5
        return next_level_threshold - current_applications
        
    def cleanup(self):
        """Clean up demo resources."""
        self.session.close()
        
    def run_complete_demo(self):
        """Run the complete enchanting workflow demonstration."""
        print("🔮 VISUAL DM ENCHANTING SYSTEM - COMPLETE WORKFLOW DEMO")
        print("=" * 70)
        print(f"🧙 Character: {self.character_name}")
        print(f"✨ Arcane Manipulation: {self.get_character_skill()}")
        print(f"💰 Gold: 10,000")
        
        try:
            # Run all demonstrations
            self.demonstrate_learning_progression()
            self.demonstrate_enchanting_process()
            self.demonstrate_enchantment_materials()
            self.demonstrate_mastery_progression()
            self.demonstrate_failure_scenarios()
            self.demonstrate_advanced_features()
            
            # Final summary
            self.print_header("WORKFLOW DEMO COMPLETE!")
            
            learned_count = self.session.query(LearnedEnchantmentModel)\
                .filter_by(character_id=self.character_id).count()
            attempt_count = self.session.query(DisenchantmentAttemptModel)\
                .filter_by(character_id=self.character_id).count()
            equipment_count = self.session.query(EquipmentInstance)\
                .filter_by(owner_id=self.character_id).count()
                
            print(f"📊 Session Statistics:")
            print(f"   • Enchantments learned: {learned_count}")
            print(f"   • Disenchantment attempts: {attempt_count}")
            print(f"   • Equipment instances: {equipment_count}")
            print(f"   • Character skill: {self.get_character_skill()}")
            
            print(f"\n🎉 Key Achievements:")
            print(f"   ✅ Complete learning-by-disenchanting workflow")
            print(f"   ✅ Multi-stage enchantment application process")
            print(f"   ✅ Material requirement and cost system")
            print(f"   ✅ Mastery progression and benefits")
            print(f"   ✅ Comprehensive failure handling")
            print(f"   ✅ Advanced features and compatibility")
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = EnchantingWorkflowDemo()
    demo.run_complete_demo() 