"""
Equipment repository for equipment system data persistence.

Handles storage and retrieval of:
- Equipment items and their properties
- Equipment durability and status tracking
- Equipment identification levels
- Equipment set assignments
- Equipment relationships with characters
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID, uuid4

from backend.systems.equipment.models.enchanting import get_enchantment_definition
from backend.infrastructure.services.equipment.equipment_quality import EquipmentQualityService

class EquipmentRepository:
    """Repository for equipment system data persistence."""
    
    def __init__(self, data_dir: str = "data/systems/equipment"):
        """Initialize repository with data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "items").mkdir(exist_ok=True)
        (self.data_dir / "characters").mkdir(exist_ok=True)
        (self.data_dir / "sets").mkdir(exist_ok=True)
        
        # Initialize equipment quality service
        self.quality_service = EquipmentQualityService()
    
    def _get_item_path(self, item_id: str) -> Path:
        """Get file path for equipment item."""
        return self.data_dir / "items" / f"{item_id}.json"
    
    def _get_character_equipment_path(self, character_id: str) -> Path:
        """Get file path for character's equipment list."""
        return self.data_dir / "characters" / f"{character_id}.json"
    
    def _get_sets_path(self) -> Path:
        """Get file path for equipment sets configuration."""
        return self.data_dir / "sets" / "equipment_sets.json"
    
    def create_equipment(self, equipment_data: Dict[str, Any]) -> str:
        """Create new equipment and return its ID."""
        # Generate unique ID
        equipment_id = str(uuid4())
        
        # Set default values
        equipment_data.update({
            'id': equipment_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'durability': 100.0,
            'durability_status': 'excellent',
            'identification_level': 0,
            'revealed_abilities': [],
            'applied_enchantments': [],
            'is_equipped': False,
            'equipped_by': None,
            'location': 'inventory'
        })
        
        # Calculate quality-based properties
        quality_info = self.quality_service.get_quality_info(equipment_data.get('quality', 'basic'))
        equipment_data.update({
            'max_durability_weeks': quality_info['durability_weeks'],
            'repair_cost_base': quality_info['repair_cost'],
            'value_multiplier': quality_info['value_multiplier']
        })
        
        # Calculate current value based on quality and condition
        base_value = equipment_data.get('base_value', 1000)
        equipment_data['current_value'] = int(base_value * quality_info['value_multiplier'])
        
        # Generate abilities based on rarity if not provided
        if 'abilities' not in equipment_data:
            equipment_data['abilities'] = self._generate_abilities_for_rarity(
                equipment_data.get('rarity', 'common'),
                equipment_data.get('equipment_type', 'weapon')
            )
        
        # Save to file
        item_path = self._get_item_path(equipment_id)
        with open(item_path, 'w') as f:
            json.dump(equipment_data, f, indent=2)
        
        return equipment_id
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict[str, Any]]:
        """Get equipment by ID."""
        item_path = self._get_item_path(equipment_id)
        
        if not item_path.exists():
            return None
        
        try:
            with open(item_path, 'r') as f:
                equipment_data = json.load(f)
            
            # Update durability based on time passage
            self._update_time_based_durability(equipment_data)
            
            # Add calculated fields
            equipment_data.update(self._calculate_derived_fields(equipment_data))
            
            return equipment_data
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Corrupted equipment data for {equipment_id}: {e}")
            return None
    
    def update_equipment(self, equipment_id: str, updates: Dict[str, Any]) -> bool:
        """Update equipment data."""
        equipment_data = self.get_equipment_by_id(equipment_id)
        if not equipment_data:
            return False
        
        # Apply updates
        equipment_data.update(updates)
        equipment_data['last_updated'] = datetime.now().isoformat()
        
        # Recalculate derived fields
        equipment_data.update(self._calculate_derived_fields(equipment_data))
        
        # Save updated data
        item_path = self._get_item_path(equipment_id)
        with open(item_path, 'w') as f:
            json.dump(equipment_data, f, indent=2)
        
        return True
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """Delete equipment."""
        item_path = self._get_item_path(equipment_id)
        
        if not item_path.exists():
            return False
        
        try:
            # Remove from character equipment lists
            self._remove_from_character_equipment(equipment_id)
            
            # Delete the item file
            item_path.unlink()
            return True
        
        except Exception as e:
            print(f"Error deleting equipment {equipment_id}: {e}")
            return False
    
    def find_equipment(self, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Find equipment matching filters."""
        all_equipment = []
        items_dir = self.data_dir / "items"
        
        # Scan all equipment files
        for item_file in items_dir.glob("*.json"):
            try:
                with open(item_file, 'r') as f:
                    equipment_data = json.load(f)
                
                # Apply filters
                if self._matches_filters(equipment_data, filters):
                    # Update time-based durability
                    self._update_time_based_durability(equipment_data)
                    equipment_data.update(self._calculate_derived_fields(equipment_data))
                    all_equipment.append(equipment_data)
            
            except (json.JSONDecodeError, KeyError):
                continue  # Skip corrupted files
        
        # Sort by creation date (newest first)
        all_equipment.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Apply pagination
        total_count = len(all_equipment)
        paginated_equipment = all_equipment[offset:offset + limit]
        
        return paginated_equipment, total_count
    
    def get_character_equipment(self, character_id: str, equipped_only: bool = False) -> List[Dict[str, Any]]:
        """Get all equipment for a character."""
        character_equipment_path = self._get_character_equipment_path(character_id)
        
        if not character_equipment_path.exists():
            return []
        
        try:
            with open(character_equipment_path, 'r') as f:
                character_data = json.load(f)
            
            equipment_list = []
            for equipment_id in character_data.get('equipment_ids', []):
                equipment = self.get_equipment_by_id(equipment_id)
                if equipment:
                    if not equipped_only or equipment.get('is_equipped', False):
                        equipment_list.append(equipment)
            
            return equipment_list
        
        except (json.JSONDecodeError, KeyError):
            return []
    
    def assign_equipment_to_character(self, equipment_id: str, character_id: str) -> bool:
        """Assign equipment to a character's inventory."""
        # Update equipment ownership
        if not self.update_equipment(equipment_id, {
            'owner_id': character_id,
            'location': 'inventory'
        }):
            return False
        
        # Update character's equipment list
        character_equipment_path = self._get_character_equipment_path(character_id)
        
        # Load existing character data
        character_data = {'equipment_ids': []}
        if character_equipment_path.exists():
            try:
                with open(character_equipment_path, 'r') as f:
                    character_data = json.load(f)
            except (json.JSONDecodeError, KeyError):
                character_data = {'equipment_ids': []}
        
        # Add equipment ID if not already present
        if equipment_id not in character_data['equipment_ids']:
            character_data['equipment_ids'].append(equipment_id)
        
        # Save updated character data
        with open(character_equipment_path, 'w') as f:
            json.dump(character_data, f, indent=2)
        
        return True
    
    def equip_item(self, equipment_id: str, character_id: str, slot: str) -> bool:
        """Equip an item to a character."""
        return self.update_equipment(equipment_id, {
            'is_equipped': True,
            'equipped_by': character_id,
            'equipment_slot': slot,
            'location': 'equipped'
        })
    
    def unequip_item(self, equipment_id: str) -> bool:
        """Unequip an item."""
        return self.update_equipment(equipment_id, {
            'is_equipped': False,
            'equipped_by': None,
            'equipment_slot': None,
            'location': 'inventory'
        })
    
    def apply_enchantment_to_item(self, equipment_id: str, enchantment_id: str, power_level: int = 100) -> bool:
        """Apply an enchantment to an item."""
        equipment = self.get_equipment_by_id(equipment_id)
        if not equipment:
            return False
        
        # Get enchantment definition
        enchantment_def = get_enchantment_definition(enchantment_id)
        if not enchantment_def:
            return False
        
        # Add enchantment to item
        applied_enchantments = equipment.get('applied_enchantments', [])
        applied_enchantments.append({
            'enchantment_id': enchantment_id,
            'enchantment_name': enchantment_def.name,
            'power_level': power_level,
            'applied_at': datetime.now().isoformat(),
            'school': enchantment_def.school.value,
            'rarity': enchantment_def.rarity.value
        })
        
        return self.update_equipment(equipment_id, {
            'applied_enchantments': applied_enchantments
        })
    
    def get_equipment_sets(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get equipment grouped by set for a character."""
        equipped_items = self.get_character_equipment(character_id, equipped_only=True)
        
        sets = {}
        for item in equipped_items:
            set_name = item.get('set_name')
            if set_name:
                if set_name not in sets:
                    sets[set_name] = []
                sets[set_name].append(item)
        
        return sets
    
    def _generate_abilities_for_rarity(self, rarity: str, equipment_type: str) -> List[Dict[str, Any]]:
        """Generate random abilities based on rarity."""
        ability_counts = {
            'common': [3, 4, 5],
            'rare': [5, 6, 7, 8, 9, 10],
            'epic': [10, 11, 12, 13, 14, 15],
            'legendary': [20, 21, 22, 23, 24, 25]
        }
        
        import random
        count = random.choice(ability_counts.get(rarity, [3, 4, 5]))
        
        # Generate placeholder abilities
        abilities = []
        for i in range(count):
            abilities.append({
                'id': f'ability_{rarity}_{equipment_type}_{i}',
                'name': f'{rarity.title()} {equipment_type.title()} Ability {i+1}',
                'description': f'A {rarity} tier ability for {equipment_type}',
                'level_required': min(i + 1, 25),
                'is_revealed': i == 0,  # First ability always revealed
                'effect_data': {
                    'bonus_type': random.choice(['damage', 'defense', 'utility']),
                    'bonus_value': random.randint(1, 10) * (i + 1)
                }
            })
        
        return abilities
    
    def _update_time_based_durability(self, equipment_data: Dict[str, Any]):
        """Update equipment durability based on time passage."""
        last_updated = equipment_data.get('last_updated')
        if not last_updated:
            return
        
        try:
            last_update_time = datetime.fromisoformat(last_updated)
            time_elapsed = datetime.now() - last_update_time
            hours_elapsed = time_elapsed.total_seconds() / 3600
            
            # Get quality-based durability loss rate
            quality = equipment_data.get('quality', 'basic')
            quality_info = self.quality_service.get_quality_info(quality)
            max_hours = quality_info['durability_weeks'] * 7 * 24
            
            # Calculate durability loss (linear degradation over time)
            durability_loss_per_hour = 100.0 / max_hours
            total_durability_loss = hours_elapsed * durability_loss_per_hour
            
            # Apply durability loss
            current_durability = equipment_data.get('durability', 100.0)
            new_durability = max(0.0, current_durability - total_durability_loss)
            
            equipment_data['durability'] = new_durability
            equipment_data['durability_status'] = self.quality_service.get_durability_status(new_durability)
            equipment_data['last_updated'] = datetime.now().isoformat()
        
        except (ValueError, TypeError):
            pass  # Skip if datetime parsing fails
    
    def _calculate_derived_fields(self, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived fields for equipment."""
        durability = equipment_data.get('durability', 100.0)
        base_value = equipment_data.get('base_value', 1000)
        quality_multiplier = equipment_data.get('value_multiplier', 1.0)
        
        # Calculate current value based on durability
        durability_factor = max(0.1, durability / 100.0)  # Minimum 10% value
        current_value = int(base_value * quality_multiplier * durability_factor)
        
        # Count revealed vs hidden abilities
        abilities = equipment_data.get('abilities', [])
        revealed_abilities = [a for a in abilities if a.get('is_revealed', False)]
        hidden_ability_count = len(abilities) - len(revealed_abilities)
        
        # Check if item can be repaired
        can_repair = durability < 100.0 and durability > 0.0
        
        # Calculate repair cost
        repair_cost = None
        if can_repair:
            quality = equipment_data.get('quality', 'basic')
            quality_info = self.quality_service.get_quality_info(quality)
            durability_loss = 100.0 - durability
            repair_cost = int(quality_info['repair_cost'] * (durability_loss / 100.0))
        
        return {
            'current_value': current_value,
            'revealed_abilities': revealed_abilities,
            'hidden_ability_count': hidden_ability_count,
            'can_repair': can_repair,
            'repair_cost': repair_cost,
            'is_broken': durability <= 0.0,
            'needs_repair': durability < 50.0
        }
    
    def _matches_filters(self, equipment_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if equipment matches the given filters."""
        for key, value in filters.items():
            if key == 'character_id':
                if equipment_data.get('owner_id') != value:
                    return False
            elif key == 'min_durability':
                if equipment_data.get('durability', 0) < value:
                    return False
            elif key == 'max_durability':
                if equipment_data.get('durability', 100) > value:
                    return False
            elif key in equipment_data:
                if equipment_data[key] != value:
                    return False
        
        return True
    
    def _remove_from_character_equipment(self, equipment_id: str):
        """Remove equipment from all character equipment lists."""
        characters_dir = self.data_dir / "characters"
        
        for character_file in characters_dir.glob("*.json"):
            try:
                with open(character_file, 'r') as f:
                    character_data = json.load(f)
                
                equipment_ids = character_data.get('equipment_ids', [])
                if equipment_id in equipment_ids:
                    equipment_ids.remove(equipment_id)
                    character_data['equipment_ids'] = equipment_ids
                    
                    with open(character_file, 'w') as f:
                        json.dump(character_data, f, indent=2)
            
            except (json.JSONDecodeError, KeyError):
                continue  # Skip corrupted files 