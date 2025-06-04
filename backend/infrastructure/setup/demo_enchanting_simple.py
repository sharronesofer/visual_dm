#!/usr/bin/env python3
"""
Simplified Enchanting/Disenchanting Workflow Demonstration

This script demonstrates the complete enchanting lifecycle in a simplified way:
1. Learning enchantments through disenchanting
2. Applying enchantments to equipment
3. Managing enchantment materials and costs
4. Progression and mastery systems
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class EnchantingWorkflowDemo:
    """Demonstrates the complete enchanting workflow."""
    
    def __init__(self):
        # Load enchantment data
        self.load_enchantment_data()
        
        # Character data
        self.character = {
            "id": "enchanter_demo_001",
            "name": "Lyria the Enchantress",
            "arcane_manipulation": 8,
            "gold": 10000,
            "learned_enchantments": {},
            "disenchantment_attempts": [],
            "equipment_instances": []
        }
        
    def load_enchantment_data(self):
        """Load enchantment configuration from JSON files."""
        enchantments_file = os.path.join(os.path.dirname(__file__), "data", "sample_enchantments.json")
        
        try:
            with open(enchantments_file, 'r') as f:
                self.enchantment_data = json.load(f)
        except FileNotFoundError:
            # Fallback data if file doesn't exist
            self.enchantment_data = {
                "enchantments": {
                    "flame_weapon": {
                        "name": "Flame Weapon",
                        "school": "elemental", 
                        "rarity": "basic",
                        "base_cost": 500,
                        "materials_required": {"fire_essence": 2, "enchanting_dust": 1}
                    },
                    "frost_weapon": {
                        "name": "Frost Weapon",
                        "school": "elemental",
                        "rarity": "basic", 
                        "base_cost": 500,
                        "materials_required": {"ice_essence": 2, "enchanting_dust": 1}
                    },
                    "keen_edge": {
                        "name": "Keen Edge",
                        "school": "enhancement",
                        "rarity": "common",
                        "base_cost": 800,
                        "materials_required": {"precision_gem": 1, "enchanting_dust": 2}
                    }
                }
            }
        
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
        
        print(f"📚 Starting with {len(self.character['learned_enchantments'])} known enchantments")
        
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
            }
        ]
        
        for i, scenario in enumerate(learning_scenarios, 1):
            self.print_subheader(f"Disenchantment Attempt #{i}")
            print(f"🗡️ Item: {scenario['item_name']}")
            print(f"📜 Target Enchantment: {scenario['enchantment']}")
            print(f"📖 Description: {scenario['description']}")
            
            # Record the attempt
            attempt = {
                "item_name": scenario['item_name'],
                "enchantment": scenario['enchantment'],
                "success": scenario['success'],
                "timestamp": datetime.utcnow() - timedelta(days=i)
            }
            self.character['disenchantment_attempts'].append(attempt)
            
            if scenario['success']:
                # Learn the enchantment
                self.character['learned_enchantments'][scenario['enchantment']] = {
                    "mastery_level": 1,
                    "times_applied": 0,
                    "learned_from": scenario['item_name'],
                    "learned_at": datetime.utcnow() - timedelta(days=i)
                }
                print(f"   ✅ SUCCESS! Learned '{scenario['enchantment']}'")
                print(f"   🔥 Item destroyed in the process")
            else:
                print(f"   ❌ FAILED! Item destroyed, enchantment not learned")
                print(f"   💡 Need more practice or better conditions")
            
        # Show final learned enchantments
        print(f"\n📚 Final Knowledge: {len(self.character['learned_enchantments'])} enchantments learned")
        for enchant_id, data in self.character['learned_enchantments'].items():
            print(f"   • {enchant_id} (Mastery: {data['mastery_level']})")
            
    def demonstrate_enchanting_process(self):
        """Show the complete enchanting process."""
        self.print_header("ENCHANTING PROCESS DEMONSTRATION")
        
        # Create some equipment to enchant
        equipment_items = [
            {
                "id": "sword_001",
                "name": "Apprentice's Blade",
                "template_id": "iron_sword",
                "enchantments": []
            },
            {
                "id": "armor_001", 
                "name": "Training Leathers",
                "template_id": "leather_armor",
                "enchantments": []
            }
        ]
        
        self.character['equipment_instances'].extend(equipment_items)
        
        print(f"🗡️ Created {len(equipment_items)} items for enchanting")
        for item in equipment_items:
            print(f"   • {item['name']} ({item['template_id']})")
            
        # Enchanting scenarios
        enchanting_scenarios = [
            {
                "item": equipment_items[0],  # sword
                "enchantment": "flame_weapon",
                "expected_success": True,
                "description": "Basic fire enchantment on weapon"
            },
            {
                "item": equipment_items[0],  # sword again
                "enchantment": "keen_edge", 
                "expected_success": True,
                "description": "Adding second enchantment to sword"
            }
        ]
        
        for i, scenario in enumerate(enchanting_scenarios, 1):
            self.print_subheader(f"Enchantment Application #{i}")
            
            item = scenario["item"]
            enchantment_id = scenario["enchantment"]
            
            print(f"🎯 Target: {item['name']}")
            print(f"✨ Enchantment: {enchantment_id}")
            print(f"📝 Description: {scenario['description']}")
            
            # Check if character knows this enchantment
            if enchantment_id not in self.character['learned_enchantments']:
                print(f"   ❌ Character doesn't know {enchantment_id}!")
                continue
                
            # Show costs and requirements
            enchantment_info = self.enchantment_data['enchantments'].get(enchantment_id, {})
            cost = enchantment_info.get('base_cost', 0)
            materials = enchantment_info.get('materials_required', {})
            print(f"   💰 Base Cost: {cost}g")
            print(f"   🧪 Materials: {materials}")
            
            # Simulate enchanting
            success = scenario["expected_success"]
            if success:
                item['enchantments'].append(enchantment_id)
                print(f"   ✅ Enchantment applied successfully!")
                print(f"   ✨ {item['name']} now glows with magical energy")
                
                # Update mastery
                learned = self.character['learned_enchantments'][enchantment_id]
                learned['times_applied'] += 1
                if learned['times_applied'] % 5 == 0:  # Mastery increases every 5 applications
                    learned['mastery_level'] += 1
                    print(f"   🎓 Mastery increased! Now level {learned['mastery_level']}")
            else:
                print(f"   ❌ Enchantment failed!")
                print(f"   💥 Materials consumed, no effect applied")
                
    def demonstrate_enchantment_materials(self):
        """Show enchantment material system."""
        self.print_header("ENCHANTMENT MATERIALS SYSTEM")
        
        # Material information
        materials_info = {
            "fire_essence": {"name": "Fire Essence", "value": 50, "rarity": "common"},
            "ice_essence": {"name": "Ice Essence", "value": 50, "rarity": "common"},
            "enchanting_dust": {"name": "Enchanting Dust", "value": 10, "rarity": "basic"},
            "precision_gem": {"name": "Precision Gem", "value": 100, "rarity": "uncommon"},
            "shadow_essence": {"name": "Shadow Essence", "value": 200, "rarity": "rare"},
            "restoration_crystal": {"name": "Restoration Crystal", "value": 500, "rarity": "rare"},
        }
        
        print("🧪 ENCHANTMENT MATERIALS DATABASE")
        print("-" * 50)
        
        for material_id, info in materials_info.items():
            rarity_color = {
                "basic": "⚪", "common": "🟢", "uncommon": "🟨", "rare": "🔵", 
                "epic": "🟣", "legendary": "🟡"
            }.get(info["rarity"], "⚪")
            
            print(f"{rarity_color} {info['name']}")
            print(f"   💰 Value: {info['value']}g")
            print(f"   🎯 Rarity: {info['rarity']}")
            
        print("\n🔮 MATERIAL USAGE IN ENCHANTMENTS")
        print("-" * 50)
        
        # Show material costs for known enchantments
        for enchant_id in self.character['learned_enchantments'].keys():
            enchantment = self.enchantment_data['enchantments'].get(enchant_id, {})
            materials = enchantment.get('materials_required', {})
            
            print(f"✨ {enchant_id}:")
            total_cost = 0
            for material, quantity in materials.items():
                if material in materials_info:
                    cost = materials_info[material]["value"] * quantity
                    total_cost += cost
                    print(f"   • {quantity}x {materials_info[material]['name']}: {cost}g")
            print(f"   💰 Total Material Cost: {total_cost}g")
            print()
            
    def demonstrate_mastery_progression(self):
        """Show enchantment mastery and progression."""
        self.print_header("MASTERY PROGRESSION SYSTEM")
        
        print("🎓 CHARACTER ENCHANTMENT MASTERY")
        print("-" * 50)
        
        for enchant_id, learned in self.character['learned_enchantments'].items():
            mastery_benefits = self.calculate_mastery_benefits(learned['mastery_level'])
            applications_to_next = self.applications_to_next_mastery(learned['times_applied'])
            
            print(f"✨ {enchant_id}")
            print(f"   🎯 Mastery Level: {learned['mastery_level']}/10")
            print(f"   🔄 Times Applied: {learned['times_applied']}")
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
                "example": "Trying to apply epic enchantment with only 5 skill",
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
                "example": "Basic enchantments fail 15% of the time",
                "consequence": "Materials consumed, no effect applied"
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
        
        self.print_subheader("Multiple Enchantments")
        print("🔗 Equipment can have multiple compatible enchantments:")
        
        # Show our enchanted sword
        for item in self.character['equipment_instances']:
            if item['enchantments']:
                print(f"   🗡️ {item['name']}:")
                for enchant in item['enchantments']:
                    enchant_info = self.enchantment_data['enchantments'].get(enchant, {})
                    print(f"      • {enchant_info.get('name', enchant)} ({enchant_info.get('school', 'unknown')})")
        print()
        
        self.print_subheader("School Classifications")
        print("🏫 Enchantments organized by magical schools:")
        schools = {}
        for enchant_id, enchant in self.enchantment_data['enchantments'].items():
            school = enchant.get('school', 'unknown')
            if school not in schools:
                schools[school] = []
            schools[school].append(enchant_id)
            
        for school, enchantments in schools.items():
            print(f"   • {school.title()}: {', '.join(enchantments)}")
        print()
        
        self.print_subheader("Rarity Progression")
        print("👑 Enchantments become more powerful with rarity:")
        rarities = {}
        for enchant_id, enchant in self.enchantment_data['enchantments'].items():
            rarity = enchant.get('rarity', 'unknown')
            if rarity not in rarities:
                rarities[rarity] = []
            rarities[rarity].append(enchant_id)
            
        for rarity, enchantments in rarities.items():
            print(f"   • {rarity.title()}: {', '.join(enchantments)}")
        
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
        
    def run_complete_demo(self):
        """Run the complete enchanting workflow demonstration."""
        print("🔮 VISUAL DM ENCHANTING SYSTEM - WORKFLOW DEMONSTRATION")
        print("=" * 70)
        print(f"🧙 Character: {self.character['name']}")
        print(f"✨ Arcane Manipulation: {self.character['arcane_manipulation']}")
        print(f"💰 Gold: {self.character['gold']:,}")
        
        # Run all demonstrations
        self.demonstrate_learning_progression()
        self.demonstrate_enchanting_process()
        self.demonstrate_enchantment_materials()
        self.demonstrate_mastery_progression()
        self.demonstrate_failure_scenarios()
        self.demonstrate_advanced_features()
        
        # Final summary
        self.print_header("WORKFLOW DEMO COMPLETE!")
        
        print(f"📊 Session Statistics:")
        print(f"   • Enchantments learned: {len(self.character['learned_enchantments'])}")
        print(f"   • Disenchantment attempts: {len(self.character['disenchantment_attempts'])}")
        print(f"   • Equipment instances: {len(self.character['equipment_instances'])}")
        print(f"   • Character skill: {self.character['arcane_manipulation']}")
        
        print(f"\n🎉 Key Achievements:")
        print(f"   ✅ Complete learning-by-disenchanting workflow")
        print(f"   ✅ Multi-stage enchantment application process")
        print(f"   ✅ Material requirement and cost system")
        print(f"   ✅ Mastery progression and benefits")
        print(f"   ✅ Comprehensive failure handling")
        print(f"   ✅ Advanced features and compatibility")

if __name__ == "__main__":
    demo = EnchantingWorkflowDemo()
    demo.run_complete_demo() 