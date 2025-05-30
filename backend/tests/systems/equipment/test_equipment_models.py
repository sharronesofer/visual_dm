"""
Tests for Equipment models.
"""

import unittest
from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock

# Import models to test
from backend.systems.equipment.models import (
    Equipment,
    EquipmentSet,
    EquipmentDurabilityLog,
)


class TestEquipmentModel:
    """Test the Equipment model."""

    def test_equipment_init(self):
        """Test Equipment initialization with default values."""
        # Create equipment instance
        equipment = Equipment(character_id=1, slot="weapon", item_id=10)

        # Check values
        assert equipment.character_id == 1
        assert equipment.slot == "weapon"
        assert equipment.item_id == 10
        assert equipment.is_identified is True  # Default value
        assert equipment.current_durability == 100.0  # Default value
        assert equipment.max_durability == 100.0  # Default value
        assert equipment.is_broken is False  # Default value
        assert equipment.properties is None  # Default value

    def test_equipment_init_with_custom_values(self):
        """Test Equipment initialization with custom values."""
        # Create equipment instance with custom values
        equipment = Equipment(
            character_id=2,
            slot="armor",
            item_id=20,
            is_identified=False,
            current_durability=50.0,
            max_durability=100.0,
            is_broken=False,
            properties={"magical": True, "effects": ["fire_resistance"]},
        )

        # Check values
        assert equipment.character_id == 2
        assert equipment.slot == "armor"
        assert equipment.item_id == 20
        assert equipment.is_identified is False
        assert equipment.current_durability == 50.0
        assert equipment.max_durability == 100.0
        assert equipment.is_broken is False
        assert equipment.properties == {"magical": True, "effects": ["fire_resistance"]}

    def test_equipment_to_dict(self):
        """Test Equipment to_dict method returns correct dictionary."""
        # Create equipment instance with test data
        test_time = datetime(2023, 1, 1, 12, 0, 0)

        equipment = Equipment(
            id=1,
            character_id=1,
            slot="head",
            item_id=10,
            current_durability=80.0,
            max_durability=100.0,
            is_broken=False,
            is_identified=True,
            properties={"effect": "strength+1"},
        )
        equipment.created_at = test_time
        equipment.updated_at = test_time

        # Call to_dict
        result = equipment.to_dict()

        # Verify dictionary contents
        assert result["id"] == 1
        assert result["character_id"] == 1
        assert result["slot"] == "head"
        assert result["item_id"] == 10
        assert result["current_durability"] == 80.0
        assert result["max_durability"] == 100.0
        assert result["is_broken"] is False
        assert result["is_identified"] is True
        assert result["properties"] == {"effect": "strength+1"}
        assert result["durability_percentage"] == 80.0
        assert result["created_at"] == test_time.isoformat()
        assert result["updated_at"] == test_time.isoformat()

    def test_durability_percentage_calculation(self):
        """Test Equipment durability_percentage is correctly calculated."""
        # Test different durability percentage calculations
        test_cases = [
            (100.0, 100.0, 100.0),  # Full durability
            (75.0, 100.0, 75.0),  # 75% durability
            (0.0, 100.0, 0.0),  # Zero durability
            (150.0, 200.0, 75.0),  # Non-standard max durability
            (0.0, 0.0, 0.0),  # Edge case: both zero (would cause division by zero)
        ]

        for current, max_val, expected in test_cases:
            equipment = Equipment(
                character_id=1,
                slot="weapon",
                current_durability=current,
                max_durability=max_val,
            )
            result = equipment.to_dict()
            assert result["durability_percentage"] == expected

    def test_broken_status(self):
        """Test Equipment broken status reflects durability state."""
        # Create equipment with zero durability but not marked as broken
        equipment = Equipment(
            character_id=1,
            slot="weapon",
            current_durability=0.0,
            max_durability=100.0,
            is_broken=False,  # Starting with is_broken=False
        )

        # The model itself doesn't set is_broken based on durability
        # This should be handled by the service layer, so is_broken stays False
        assert equipment.is_broken is False

        # Now explicitly set is_broken to true
        equipment.is_broken = True
        assert equipment.is_broken is True

        # to_dict should reflect this value
        result = equipment.to_dict()
        assert result["is_broken"] is True


class TestEquipmentSetModel:
    """Test the EquipmentSet model."""

    def test_equipment_set_init(self):
        """Test EquipmentSet initialization."""
        # Test data
        set_bonuses = {
            "2": {"stat_bonus": {"strength": 1}},
            "4": {"stat_bonus": {"strength": 2, "dexterity": 1}},
        }
        item_ids = [101, 102, 103, 104]

        # Create equipment set
        equipment_set = EquipmentSet(
            name="Warrior Set",
            description="A set of warrior equipment",
            set_bonuses=set_bonuses,
            item_ids=item_ids,
        )

        # Check values
        assert equipment_set.name == "Warrior Set"
        assert equipment_set.description == "A set of warrior equipment"
        assert equipment_set.set_bonuses == set_bonuses
        assert equipment_set.item_ids == item_ids

    def test_equipment_set_init_with_complex_bonuses(self):
        """Test EquipmentSet initialization with complex bonuses."""
        # Test data with complex bonuses including stats and effects
        set_bonuses = {
            "2": {
                "stats": {"strength": 1},
                "effects": [
                    {
                        "name": "Fire Resistance",
                        "description": "Gain 10% fire resistance",
                    }
                ],
            },
            "4": {
                "stats": {"strength": 2, "dexterity": 1},
                "effects": [
                    {
                        "name": "Fire Resistance",
                        "description": "Gain 25% fire resistance",
                    },
                    {
                        "name": "Flame Aura",
                        "description": "Deal 5 fire damage to attackers",
                    },
                ],
            },
        }
        item_ids = [101, 102, 103, 104]

        # Create equipment set
        equipment_set = EquipmentSet(
            name="Flame Knight Set",
            description="A set of fire-enchanted armor",
            set_bonuses=set_bonuses,
            item_ids=item_ids,
        )

        # Check values
        assert equipment_set.name == "Flame Knight Set"
        assert equipment_set.description == "A set of fire-enchanted armor"
        assert equipment_set.set_bonuses == set_bonuses
        assert equipment_set.item_ids == item_ids

        # Check specific complex structure elements
        assert equipment_set.set_bonuses["2"]["stats"]["strength"] == 1
        assert equipment_set.set_bonuses["4"]["effects"][1]["name"] == "Flame Aura"

    def test_equipment_set_to_dict(self):
        """Test EquipmentSet to_dict method returns correct dictionary."""
        # Test data
        test_time = datetime(2023, 1, 1, 12, 0, 0)
        set_bonuses = {
            "2": {"stat_bonus": {"strength": 1}},
            "4": {"stat_bonus": {"strength": 2, "dexterity": 1}},
        }
        item_ids = [101, 102, 103, 104]

        # Create equipment set
        equipment_set = EquipmentSet(
            id=1,
            name="Warrior Set",
            description="A set of warrior equipment",
            set_bonuses=set_bonuses,
            item_ids=item_ids,
        )
        equipment_set.created_at = test_time
        equipment_set.updated_at = test_time

        # Call to_dict
        result = equipment_set.to_dict()

        # Verify dictionary contents
        assert result["id"] == 1
        assert result["name"] == "Warrior Set"
        assert result["description"] == "A set of warrior equipment"
        assert result["set_bonuses"] == set_bonuses
        assert result["item_ids"] == item_ids
        assert result["created_at"] == test_time.isoformat()
        assert result["updated_at"] == test_time.isoformat()

    def test_equipment_set_with_empty_values(self):
        """Test EquipmentSet with empty values."""
        # Create equipment set with minimal values
        equipment_set = EquipmentSet(
            name="Empty Set",
            set_bonuses={},  # Empty bonuses
            item_ids=[],  # Empty item list
        )

        # Verify empty values
        assert equipment_set.name == "Empty Set"
        assert equipment_set.description is None  # Default value
        assert equipment_set.set_bonuses == {}
        assert equipment_set.item_ids == []

        # to_dict should handle these empty values
        result = equipment_set.to_dict()
        assert result["set_bonuses"] == {}
        assert result["item_ids"] == []


class TestEquipmentDurabilityLogModel:
    """Test the EquipmentDurabilityLog model."""

    def test_durability_log_init(self):
        """Test EquipmentDurabilityLog initialization."""
        # Create durability log entry
        log_entry = EquipmentDurabilityLog(
            equipment_id=1,
            previous_durability=100.0,
            new_durability=90.0,
            change_amount=-10.0,
            change_reason="combat",
            event_details={"combat_type": "critical", "enemy": "goblin"},
        )

        # Check values
        assert log_entry.equipment_id == 1
        assert log_entry.previous_durability == 100.0
        assert log_entry.new_durability == 90.0
        assert log_entry.change_amount == -10.0
        assert log_entry.change_reason == "combat"
        assert log_entry.event_details == {"combat_type": "critical", "enemy": "goblin"}

    def test_durability_log_to_dict(self):
        """Test EquipmentDurabilityLog to_dict method returns correct dictionary."""
        # Test data
        test_time = datetime(2023, 1, 1, 12, 0, 0)

        # Create durability log entry
        log_entry = EquipmentDurabilityLog(
            id=1,
            equipment_id=1,
            previous_durability=100.0,
            new_durability=90.0,
            change_amount=-10.0,
            change_reason="combat",
            event_details={"combat_type": "critical", "enemy": "goblin"},
        )
        log_entry.timestamp = test_time

        # Call to_dict
        result = log_entry.to_dict()

        # Verify dictionary contents
        assert result["id"] == 1
        assert result["equipment_id"] == 1
        assert result["previous_durability"] == 100.0
        assert result["new_durability"] == 90.0
        assert result["change_amount"] == -10.0
        assert result["change_reason"] == "combat"
        assert result["event_details"] == {"combat_type": "critical", "enemy": "goblin"}
        assert result["timestamp"] == test_time.isoformat()

    def test_durability_log_repair_event(self):
        """Test EquipmentDurabilityLog with repair event."""
        # Create durability log entry for repair
        log_entry = EquipmentDurabilityLog(
            equipment_id=1,
            previous_durability=50.0,
            new_durability=100.0,
            change_amount=50.0,  # Positive value for repair
            change_reason="repair",
            event_details={"repair_type": "full", "cost": 100},
        )

        # Check values
        assert log_entry.equipment_id == 1
        assert log_entry.previous_durability == 50.0
        assert log_entry.new_durability == 100.0
        assert log_entry.change_amount == 50.0
        assert log_entry.change_reason == "repair"
        assert log_entry.event_details == {"repair_type": "full", "cost": 100}

    def test_durability_log_without_event_details(self):
        """Test EquipmentDurabilityLog without event details."""
        # Create durability log entry without event details
        log_entry = EquipmentDurabilityLog(
            equipment_id=1,
            previous_durability=100.0,
            new_durability=95.0,
            change_amount=-5.0,
            change_reason="wear",
            # No event_details provided
        )

        # Check values
        assert log_entry.equipment_id == 1
        assert log_entry.previous_durability == 100.0
        assert log_entry.new_durability == 95.0
        assert log_entry.change_amount == -5.0
        assert log_entry.change_reason == "wear"
        assert log_entry.event_details is None  # Should be None when not provided

        # to_dict should handle None value
        result = log_entry.to_dict()
        assert result["event_details"] is None
