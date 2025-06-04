#!/usr/bin/env python3
"""
Equipment System Setup Script

This script sets up the Visual DM equipment system, creating necessary
directories, initializing sample data, and verifying the installation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

class EquipmentSystemSetup:
    """Setup manager for the equipment system."""
    
    def __init__(self, project_root: str = None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Auto-detect project root (3 levels up from this file)
            self.project_root = Path(__file__).parent.parent.parent.parent
        
        self.equipment_root = self.project_root / "backend" / "systems" / "equipment"
        self.data_root = self.project_root / "data"
        
        print(f"🏗️  Equipment System Setup")
        print(f"Project Root: {self.project_root}")
        print(f"Equipment Root: {self.equipment_root}")
        print("=" * 50)
    
    def create_directories(self):
        """Create necessary directories for the equipment system."""
        print("📁 Creating data directories...")
        
        directories = [
            self.data_root / "equipment" / "items",
            self.data_root / "equipment" / "characters",
            self.data_root / "equipment" / "sets",
            self.data_root / "enchanting" / "profiles",
            self.data_root / "enchanting" / "attempts",
            self.data_root / "enchanting" / "applications",
            self.equipment_root / "data"
        ]
        
        created_count = 0
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {directory}")
                created_count += 1
            else:
                print(f"   ⏭️  Exists: {directory}")
        
        print(f"📁 Directory setup complete ({created_count} created)")
        return True
    
    def install_sample_enchantments(self):
        """Install sample enchantments if they don't exist."""
        print("✨ Installing sample enchantments...")
        
        sample_file = self.equipment_root / "data" / "sample_enchantments.json"
        
        if sample_file.exists():
            print("   ⏭️  Sample enchantments already exist")
            return True
        
        sample_enchantments = {
            "enchantments": {
                "flame_weapon": {
                    "id": "flame_weapon",
                    "name": "Flame Weapon",
                    "description": "Weapon deals additional 1d6 fire damage on hit",
                    "school": "elemental",
                    "rarity": "basic",
                    "min_arcane_manipulation": 2,
                    "base_cost": 300,
                    "min_item_quality": "basic",
                    "compatible_item_types": ["weapon"],
                    "thematic_tags": ["fire", "damage", "elemental"],
                    "power_scaling": {
                        "base_damage": 3.5,
                        "damage_per_mastery": 0.7,
                        "max_mastery_bonus": 7.0
                    }
                },
                "armor_of_protection": {
                    "id": "armor_of_protection",
                    "name": "Armor of Protection",
                    "description": "Provides +2 AC and resistance to physical damage",
                    "school": "protection",
                    "rarity": "military",
                    "min_arcane_manipulation": 4,
                    "base_cost": 800,
                    "min_item_quality": "military",
                    "compatible_item_types": ["armor", "shield"],
                    "thematic_tags": ["protection", "defense", "physical"],
                    "power_scaling": {
                        "base_ac_bonus": 2,
                        "ac_per_mastery": 0.2,
                        "damage_resistance": 0.1
                    }
                },
                "boots_of_speed": {
                    "id": "boots_of_speed",
                    "name": "Boots of Speed",
                    "description": "Increases movement speed by 30 feet and grants advantage on Dexterity saves",
                    "school": "utility",
                    "rarity": "noble",
                    "min_arcane_manipulation": 6,
                    "base_cost": 1500,
                    "min_item_quality": "noble",
                    "compatible_item_types": ["boots"],
                    "thematic_tags": ["speed", "mobility", "dexterity"],
                    "power_scaling": {
                        "base_speed_bonus": 30,
                        "speed_per_mastery": 3,
                        "save_bonus": 0.1
                    }
                }
            }
        }
        
        try:
            with open(sample_file, 'w') as f:
                json.dump(sample_enchantments, f, indent=2)
            print(f"   ✅ Created sample enchantments: {sample_file}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create sample enchantments: {e}")
            return False
    
    def create_config_file(self):
        """Create equipment system configuration file."""
        print("⚙️  Creating configuration file...")
        
        config_file = self.equipment_root / "config.json"
        
        if config_file.exists():
            print("   ⏭️  Configuration file already exists")
            return True
        
        config = {
            "equipment_system": {
                "version": "1.0.0",
                "data_storage": "json",
                "quality_tiers": {
                    "basic": {
                        "durability_weeks": 1,
                        "repair_cost": 500,
                        "value_multiplier": 1.0
                    },
                    "military": {
                        "durability_weeks": 2,
                        "repair_cost": 750,
                        "value_multiplier": 3.0
                    },
                    "noble": {
                        "durability_weeks": 4,
                        "repair_cost": 1500,
                        "value_multiplier": 6.0
                    }
                },
                "enchanting": {
                    "min_gold_cost": 100,
                    "failure_rate_base": 0.15,
                    "mastery_progression_rate": 0.1,
                    "disenchant_success_base": 0.7
                },
                "rarity_ability_counts": {
                    "common": [3, 4, 5],
                    "rare": [5, 6, 7, 8, 9, 10],
                    "epic": [10, 11, 12, 13, 14, 15],
                    "legendary": [20, 21, 22, 23, 24, 25]
                }
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"   ✅ Created configuration: {config_file}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create configuration: {e}")
            return False
    
    def verify_installation(self):
        """Verify that the equipment system is properly installed."""
        print("🔍 Verifying installation...")
        
        checks = [
            ("Equipment models", self._check_models),
            ("Equipment services", self._check_services),
            ("Equipment repositories", self._check_repositories),
            ("Equipment routers", self._check_routers),
            ("Sample data", self._check_sample_data),
            ("Demo script", self._check_demo_script)
        ]
        
        passed = 0
        for check_name, check_func in checks:
            try:
                if check_func():
                    print(f"   ✅ {check_name}")
                    passed += 1
                else:
                    print(f"   ❌ {check_name}")
            except Exception as e:
                print(f"   ❌ {check_name}: {e}")
        
        success_rate = (passed / len(checks)) * 100
        print(f"\n📊 Verification Results: {passed}/{len(checks)} checks passed ({success_rate:.1f}%)")
        
        return passed == len(checks)
    
    def _check_models(self):
        """Check that equipment models are importable."""
        try:
            sys.path.append(str(self.equipment_root.parent.parent))
            from backend.systems.equipment.models.enchanting import EnchantmentDefinition
            return True
        except ImportError:
            return False
    
    def _check_services(self):
        """Check that equipment services are importable."""
        try:
            from backend.systems.equipment.services.enchanting_service import EnchantingService
            from backend.systems.equipment.services.equipment_quality import EquipmentQualityService
            return True
        except ImportError:
            return False
    
    def _check_repositories(self):
        """Check that repositories are importable."""
        try:
            from backend.systems.equipment.repositories.equipment_repository import EquipmentRepository
            from backend.systems.equipment.repositories.enchanting_repository import EnchantingRepository
            return True
        except ImportError:
            return False
    
    def _check_routers(self):
        """Check that routers are importable."""
        try:
            from backend.systems.equipment.routers.enchanting_router import router
            return True
        except ImportError:
            return False
    
    def _check_sample_data(self):
        """Check that sample data exists."""
        sample_file = self.equipment_root / "data" / "sample_enchantments.json"
        return sample_file.exists()
    
    def _check_demo_script(self):
        """Check that demo script exists."""
        demo_file = self.equipment_root / "examples" / "enchanting_demo.py"
        return demo_file.exists()
    
    def create_quick_start_guide(self):
        """Create a quick start guide for the equipment system."""
        print("📖 Creating quick start guide...")
        
        guide_file = self.equipment_root / "QUICK_START.md"
        
        guide_content = """# Equipment System Quick Start Guide

## 🚀 Getting Started

### 1. Run the Setup (Already Done!)
```bash
python backend/systems/equipment/setup_equipment_system.py
```

### 2. Start the Backend Server
```bash
cd backend
python -m uvicorn main:app --reload
```

### 3. Test the Equipment System
```bash
# Run integration tests
python backend/systems/equipment/test_integration.py

# Run the demo script
python backend/systems/equipment/examples/enchanting_demo.py
```

### 4. Access the API
- Equipment API: http://localhost:8000/equipment/
- Health Check: http://localhost:8000/equipment/health
- API Docs: http://localhost:8000/docs

## 🎮 Key Features

### Equipment Quality System
- **Basic**: 1 week durability, 1x value multiplier
- **Military**: 2 weeks durability, 3x value multiplier  
- **Noble**: 4 weeks durability, 6x value multiplier

### Learn-by-Disenchanting
1. Acquire enchanted items
2. Attempt to disenchant (risk destroying the item)
3. Learn enchantments on success
4. Apply learned enchantments to other items

### API Examples

```python
import requests

# Create equipment
response = requests.post("http://localhost:8000/equipment/", json={
    "name": "Flame Sword",
    "equipment_type": "weapon",
    "quality": "military",
    "rarity": "rare",
    "base_value": 2000
})

# Disenchant item to learn enchantments
response = requests.post("http://localhost:8000/equipment/enchanting/disenchant", json={
    "character_id": "uuid-here",
    "item_id": "uuid-here",
    "item_data": {"name": "Enchanted Sword", "quality": "military", "enchantments": ["flame_weapon"]},
    "arcane_manipulation_level": 5,
    "character_level": 10
})
```

## 📚 Documentation

- Full System Docs: `backend/systems/equipment/README.md`
- Equipment Description: `backend/systems/equipment/equipment_DESCRIPTION.md`
- Integration Status: `backend/systems/equipment/INTEGRATION_STATUS.md`

## 🎯 Next Steps

1. Integrate with your character system for ability checks
2. Connect to your economy system for gold transactions
3. Add equipment to your inventory management
4. Create custom enchantments for your world

Happy enchanting! 🪄
"""
        
        try:
            with open(guide_file, 'w') as f:
                f.write(guide_content)
            print(f"   ✅ Created quick start guide: {guide_file}")
            return True
        except Exception as e:
            print(f"   ❌ Failed to create guide: {e}")
            return False
    
    def run_setup(self):
        """Run the complete setup process."""
        print("🛠️  Starting Equipment System Setup\n")
        
        steps = [
            ("Creating directories", self.create_directories),
            ("Installing sample enchantments", self.install_sample_enchantments),
            ("Creating configuration", self.create_config_file),
            ("Creating quick start guide", self.create_quick_start_guide),
            ("Verifying installation", self.verify_installation)
        ]
        
        completed = 0
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if step_func():
                    completed += 1
                    print(f"✅ {step_name} completed")
                else:
                    print(f"❌ {step_name} failed")
            except Exception as e:
                print(f"❌ {step_name} failed: {e}")
        
        print(f"\n🎉 Setup Complete!")
        print(f"   {completed}/{len(steps)} steps completed successfully")
        
        if completed == len(steps):
            print("\n✅ Equipment system is ready to use!")
            print("\n📖 Next steps:")
            print("   1. Start the backend server: cd backend && python -m uvicorn main:app --reload")
            print("   2. Run integration tests: python backend/systems/equipment/test_integration.py")
            print("   3. Try the demo: python backend/systems/equipment/examples/enchanting_demo.py")
            print("   4. Read the quick start guide: backend/systems/equipment/QUICK_START.md")
        else:
            print("\n⚠️  Some setup steps failed. Check the output above for details.")
        
        return completed == len(steps)


def main():
    """Main setup function."""
    setup = EquipmentSystemSetup()
    success = setup.run_setup()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 