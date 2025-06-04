#!/usr/bin/env python3
"""
Hybrid Equipment System Demonstration

This script demonstrates the complete hybrid template+instance pattern
for equipment management in Visual DM. Shows how JSON templates work
with SQLAlchemy database instances.

Key Features Demonstrated:
- Template loading from JSON
- Equipment instance creation
- Quality tier effects
- Enchantment system integration
- Time-based degradation
- Equipment operations (equip/unequip/repair)
- Comprehensive equipment details
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend to the Python path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Set up environment to avoid database issues
os.environ.setdefault('DATABASE_URL', 'sqlite:///demo_equipment.db')

# Now import our hybrid system
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from systems.equipment.models.equipment_models import Base, EquipmentInstance, AppliedEnchantment, MaintenanceRecord
from systems.equipment.services.hybrid_equipment_service import HybridEquipmentService
from systems.equipment.services.template_service import EquipmentTemplateService

# Create a minimal Character table for demo purposes
class Character(Base):
    """Minimal character table for demo foreign key constraints."""
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def setup_demo_database():
    """Set up an in-memory SQLite database for the demo."""
    print("🔧 Setting up demo database...")
    
    # Create in-memory SQLite database
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # Create a demo character
    demo_character = Character(id="demo_character_001", name="Demo Hero")
    session.add(demo_character)
    session.commit()
    
    print("   ✅ Demo database ready")
    return session

def demo_template_loading():
    """Demonstrate template loading from JSON files."""
    print("\n📖 TEMPLATE LOADING DEMONSTRATION")
    print("=" * 60)
    
    # Create template service
    templates = EquipmentTemplateService()
    success = templates.load_all_templates()
    
    print(f"Template loading successful: {success}")
    
    # Show loaded templates
    equipment_templates = templates.list_equipment_templates()
    enchantment_templates = templates.list_enchantment_templates()
    
    print(f"📦 Loaded {len(equipment_templates)} equipment templates:")
    for template in equipment_templates[:3]:  # Show first 3
        print(f"   • {template.name} ({template.item_type}, {template.quality_tier})")
        print(f"     Value: {template.base_value}g, Level: {template.restrictions.get('min_level', 1)}")
    
    print(f"\n✨ Loaded {len(enchantment_templates)} enchantment templates:")
    for template in enchantment_templates[:3]:  # Show first 3
        print(f"   • {template.name} ({template.school}, {template.rarity})")
        print(f"     Cost: {template.base_cost}g, Min Level: {template.min_arcane_manipulation}")
    
    # Show quality tiers
    print(f"\n🏅 Quality Tiers:")
    for tier_name in ["basic", "military", "noble"]:
        tier = templates.get_quality_tier(tier_name)
        if tier:
            print(f"   • {tier_name.title()}: {tier.durability_weeks} weeks, {tier.value_multiplier}x value")
    
    return templates

def demo_instance_creation(service: HybridEquipmentService):
    """Demonstrate creating equipment instances from templates."""
    print("\n🔨 EQUIPMENT INSTANCE CREATION")
    print("=" * 60)
    
    # Character ID for demo
    character_id = "demo_character_001"
    
    # Create different equipment instances
    equipment_instances = []
    
    # Create an iron sword (basic quality)
    print("Creating Iron Sword (basic quality)...")
    iron_sword = service.create_equipment_instance(
        template_id="iron_sword",
        owner_id=character_id,
        custom_name="Bob's Trusty Blade"
    )
    if iron_sword:
        equipment_instances.append(iron_sword)
        print(f"   ✅ Created: {iron_sword.custom_name or 'Iron Sword'} (ID: {iron_sword.id[:8]}...)")
    
    # Create dragonscale armor (noble quality)
    print("Creating Dragonscale Armor (noble quality)...")
    dragon_armor = service.create_equipment_instance(
        template_id="dragonscale_armor",
        owner_id=character_id
    )
    if dragon_armor:
        equipment_instances.append(dragon_armor)
        print(f"   ✅ Created: Dragonscale Armor (ID: {dragon_armor.id[:8]}...)")
    
    # Create elven bow with quality override
    print("Creating Elven Bow (upgraded to noble quality)...")
    elven_bow = service.create_equipment_instance(
        template_id="elven_bow",
        owner_id=character_id,
        quality_override="noble",
        custom_name="Moonwhisper"
    )
    if elven_bow:
        equipment_instances.append(elven_bow)
        print(f"   ✅ Created: {elven_bow.custom_name} (ID: {elven_bow.id[:8]}...)")
    
    print(f"\n📦 Total equipment instances created: {len(equipment_instances)}")
    return equipment_instances

def demo_equipment_details(service: HybridEquipmentService, instances):
    """Demonstrate getting comprehensive equipment details."""
    print("\n🔍 EQUIPMENT DETAILS DEMONSTRATION")
    print("=" * 60)
    
    for instance in instances[:2]:  # Show details for first 2 items
        details = service.get_equipment_details(instance.id)
        if not details:
            continue
        
        template = details["template"]
        quality_config = details["quality_config"]
        
        print(f"\n📋 {template.name}")
        print(f"   Template ID: {template.id}")
        print(f"   Quality: {quality_config.tier if quality_config else 'Unknown'}")
        print(f"   Condition: {details['condition_status']} ({instance.durability:.1f}%)")
        print(f"   Value: {instance.current_value}g")
        print(f"   Location: {instance.location}")
        
        print(f"   Base Stats:")
        for stat, value in template.stat_modifiers.items():
            adjusted_value = details["current_stats"].get(stat, value)
            penalty_indicator = " (reduced)" if adjusted_value < value else ""
            print(f"     • {stat}: {adjusted_value}{penalty_indicator}")
        
        print(f"   Abilities ({len(template.abilities)}):")
        for ability in template.abilities:
            print(f"     • {ability['name']}: {ability['description']}")
        
        print(f"   Compatible Enchantments: {len(template.compatible_enchantments)}")
        for school in template.compatible_enchantments[:3]:
            print(f"     • {school}")

def demo_equipment_operations(service: HybridEquipmentService, instances):
    """Demonstrate equipment operations like equipping and repairing."""
    print("\n⚔️ EQUIPMENT OPERATIONS DEMONSTRATION")
    print("=" * 60)
    
    if len(instances) < 2:
        print("❌ Not enough equipment instances for operations demo")
        return
    
    sword = instances[0]
    armor = instances[1] if len(instances) > 1 else None
    
    # Equip the sword
    print(f"🗡️ Equipping {sword.custom_name or 'Iron Sword'}...")
    success = service.equip_item(sword.id, "main_hand")
    print(f"   {'✅' if success else '❌'} Equipping {'successful' if success else 'failed'}")
    
    # Equip the armor
    if armor:
        print(f"🛡️ Equipping {armor.template_id.replace('_', ' ').title()}...")
        success = service.equip_item(armor.id, "chest")
        print(f"   {'✅' if success else '❌'} Equipping {'successful' if success else 'failed'}")
    
    # Simulate some damage
    print(f"\n💥 Applying combat damage to sword...")
    damage_applied = service.apply_combat_damage(sword.id, 15.0)
    if damage_applied:
        updated_sword = service.get_equipment_instance(sword.id)
        print(f"   ⚔️ Sword durability: {updated_sword.durability:.1f}% (was 100%)")
    
    # Repair the sword
    print(f"\n🔧 Repairing the damaged sword...")
    repair_result = service.repair_equipment(sword.id, "demo_blacksmith")
    if repair_result["success"]:
        print(f"   ✅ Repair successful!")
        print(f"   💰 Cost: {repair_result['gold_cost']}g")
        print(f"   🔨 Durability: {repair_result['durability_before']:.1f}% → {repair_result['durability_after']:.1f}%")
        print(f"   📊 New condition: {repair_result['new_condition']}")
    else:
        print(f"   ❌ Repair failed: {repair_result.get('error', 'Unknown error')}")

def demo_time_degradation(service: HybridEquipmentService, instances):
    """Demonstrate time-based equipment degradation."""
    print("\n⏰ TIME DEGRADATION DEMONSTRATION")
    print("=" * 60)
    
    if not instances:
        print("❌ No equipment instances for degradation demo")
        return
    
    # Show initial durability
    print("Initial equipment durability:")
    for instance in instances:
        template = service.templates.get_equipment_template(instance.template_id)
        print(f"   • {template.name}: {instance.durability:.1f}%")
    
    # Simulate time passage by manually updating timestamps
    print(f"\n⏳ Simulating 6 hours of time passage...")
    for instance in instances:
        # Manually set last_updated to simulate time passage
        instance.last_updated = datetime.utcnow() - timedelta(hours=6)
    service.db.commit()
    
    # Process degradation
    character_id = instances[0].owner_id
    degradation_result = service.process_time_degradation(character_id)
    
    print(f"   📊 Degradation processed: {degradation_result['equipment_processed']} items")
    print(f"   📉 Items degraded: {degradation_result['equipment_degraded']} items")
    
    # Show updated durability
    print("\nEquipment durability after time passage:")
    for instance in instances:
        updated_instance = service.get_equipment_instance(instance.id)
        template = service.templates.get_equipment_template(instance.template_id)
        change = instance.durability - updated_instance.durability
        change_indicator = f" (-{change:.1f})" if change > 0 else " (no change)"
        print(f"   • {template.name}: {updated_instance.durability:.1f}%{change_indicator}")

def demo_template_queries(service: HybridEquipmentService):
    """Demonstrate template querying capabilities."""
    print("\n🔍 TEMPLATE QUERY DEMONSTRATION")
    print("=" * 60)
    
    # Query by type
    weapons = service.list_available_equipment_templates(item_type="weapon")
    print(f"🗡️ Available weapons: {len(weapons)}")
    for weapon in weapons[:3]:
        print(f"   • {weapon.name} ({weapon.quality_tier}, Level {weapon.restrictions.get('min_level', 1)})")
    
    # Query by quality
    noble_equipment = service.list_available_equipment_templates(quality_tier="noble")
    print(f"\n👑 Noble quality equipment: {len(noble_equipment)}")
    for item in noble_equipment:
        print(f"   • {item.name} ({item.item_type})")
    
    # Query by level restriction
    low_level = service.list_available_equipment_templates(max_level=5)
    print(f"\n🆕 Equipment for levels 1-5: {len(low_level)}")
    for item in low_level[:3]:
        print(f"   • {item.name} (Level {item.restrictions.get('min_level', 1)})")
    
    # Get template info
    print(f"\n📖 Detailed template information:")
    template_info = service.get_equipment_template_info("dragonscale_armor")
    if template_info:
        template = template_info["template"]
        print(f"   📋 {template.name}")
        print(f"   💰 Calculated value: {template_info['calculated_value']}g")
        print(f"   ✨ Compatible enchantments: {len(template_info['compatible_enchantments'])}")
        print(f"   🔨 Can be crafted: {template_info['can_be_crafted']}")

def demo_hybrid_integration(service: HybridEquipmentService, instances):
    """Demonstrate the hybrid pattern benefits."""
    print("\n🔗 HYBRID PATTERN BENEFITS DEMONSTRATION")
    print("=" * 60)
    
    print("Template + Instance Integration:")
    
    if instances:
        instance = instances[0]
        details = service.get_equipment_details(instance.id)
        
        if details:
            template = details["template"]
            print(f"\n📖 Template Data (JSON):")
            print(f"   • Name: {template.name}")
            print(f"   • Base Value: {template.base_value}g")
            print(f"   • Material: {template.material}")
            print(f"   • Thematic Tags: {template.thematic_tags}")
            
            print(f"\n💾 Instance Data (Database):")
            print(f"   • Unique ID: {instance.id}")
            print(f"   • Current Durability: {instance.durability:.1f}%")
            print(f"   • Current Value: {instance.current_value}g")
            print(f"   • Owner: {instance.owner_id}")
            print(f"   • Custom Name: {instance.custom_name or 'None'}")
            print(f"   • Last Updated: {instance.last_updated}")
            
            print(f"\n🤝 Hybrid Computed Values:")
            print(f"   • Condition Status: {details['condition_status']}")
            print(f"   • Condition Penalty: {details['condition_penalty']:.1%}")
            print(f"   • Estimated Repair Cost: {details['estimated_repair_cost']}g")
            print(f"   • Can Be Enchanted: {details['can_be_enchanted']}")
    
    print(f"\n✨ Pattern Benefits:")
    print(f"   🎨 Easy Balancing: Modify JSON templates without code changes")
    print(f"   📊 Rich Instance State: Track condition, history, customizations")
    print(f"   🚀 Performance: Database queries for instances, cached templates")
    print(f"   🔧 Flexibility: Override template properties per instance")
    print(f"   📱 Scalability: Templates shared, instances unique per character")

def demo_configuration_flexibility():
    """Demonstrate the configuration flexibility of the hybrid approach."""
    print("\n⚙️ CONFIGURATION FLEXIBILITY DEMONSTRATION")
    print("=" * 60)
    
    # Show how templates can be easily modified
    print("JSON Template Configuration Benefits:")
    print("\n📁 Template Files:")
    template_dir = Path(__file__).parent / "data"
    json_files = list(template_dir.glob("*.json"))
    
    for json_file in json_files:
        size_kb = json_file.stat().st_size / 1024
        print(f"   • {json_file.name}: {size_kb:.1f} KB")
    
    # Load and show a sample of the quality configuration
    quality_file = template_dir / "quality_tiers.json"
    if quality_file.exists():
        with open(quality_file, 'r') as f:
            quality_data = json.load(f)
        
        print(f"\n🏅 Sample Quality Configuration:")
        for tier_name, tier_data in list(quality_data.get("quality_tiers", {}).items())[:2]:
            print(f"   • {tier_name.title()}:")
            print(f"     - Durability: {tier_data.get('durability_weeks')} weeks")
            print(f"     - Repair Cost: {tier_data.get('repair_cost')}g")
            print(f"     - Value Multiplier: {tier_data.get('value_multiplier')}x")
    
    print(f"\n🎮 Game Designer Benefits:")
    print(f"   • Modify balance without programming knowledge")
    print(f"   • A/B test different configurations")
    print(f"   • Hot-reload changes during development") 
    print(f"   • Environment-specific configurations")
    print(f"   • Community modding support")

def main():
    """Run the complete hybrid system demonstration."""
    print("🎮 VISUAL DM EQUIPMENT SYSTEM - HYBRID PATTERN DEMO")
    print("=" * 70)
    print("Demonstrating Template (JSON) + Instance (Database) Architecture")
    print("=" * 70)
    
    try:
        # Set up the demo environment
        db_session = setup_demo_database()
        
        # Initialize the hybrid service
        print("\n🚀 Initializing hybrid equipment service...")
        service = HybridEquipmentService(db_session)
        print("   ✅ Hybrid service ready")
        
        # Run demonstrations
        templates = demo_template_loading()
        instances = demo_instance_creation(service)
        demo_equipment_details(service, instances)
        demo_equipment_operations(service, instances)
        demo_time_degradation(service, instances)
        demo_template_queries(service)
        demo_hybrid_integration(service, instances)
        demo_configuration_flexibility()
        
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 70)
        print("Key Achievements:")
        print("✅ Templates loaded from JSON configuration")
        print("✅ Equipment instances created in database")
        print("✅ Hybrid pattern seamlessly integrated")
        print("✅ Equipment operations (equip/repair/damage) functional")
        print("✅ Time-based degradation system working")
        print("✅ Template querying and instance management")
        print("✅ Configuration flexibility demonstrated")
        
        # Show summary stats
        character_equipment = service.get_character_equipment("demo_character_001")
        equipped_count = len([eq for eq in character_equipment if eq.is_equipped])
        
        print(f"\n📊 Demo Session Summary:")
        print(f"   • Templates loaded: {len(service.templates.list_equipment_templates())}")
        print(f"   • Equipment instances: {len(character_equipment)}")
        print(f"   • Items equipped: {equipped_count}")
        print(f"   • Database records: {len(character_equipment)} equipment + maintenance logs")
        
        print(f"\n🔥 Why This Hybrid Approach Rocks:")
        print(f"   🎨 Game designers can balance equipment via JSON")
        print(f"   📊 Rich character-specific equipment tracking")
        print(f"   🚀 Performance: Templates cached, instances queried efficiently")
        print(f"   🔧 Easy maintenance: Separate concerns cleanly")
        print(f"   📱 Scalable: Templates shared across millions of players")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db_session' in locals():
            db_session.close()

if __name__ == "__main__":
    main() 