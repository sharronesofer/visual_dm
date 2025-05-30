"""
Tests for backend.systems.shared.rules

Comprehensive tests for balance constants and data loading utilities.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Import the module being tested
try: pass
    from backend.systems.shared.rules import (
        BalanceConstants,
        balance_constants,
        load_data,
        save_data,
        load_game_rules,
        get_class_data,
        get_race_data,
        calculate_xp_for_level,
        calculate_ability_modifier,
    )
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.shared.rules: {e}", allow_module_level=True)


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    import backend.systems.shared.rules
    assert backend.systems.shared.rules is not None


class TestBalanceConstants: pass
    """Test class for BalanceConstants"""
    
    def test_default_constants(self): pass
        """Test that default constants are properly defined."""
        assert BalanceConstants.BASE_XP == 1000
        assert BalanceConstants.XP_SCALING_FACTOR == 1.5
        assert BalanceConstants.MAX_LEVEL == 20
        assert BalanceConstants.STARTING_GOLD == 100
        assert BalanceConstants.MIN_ABILITY_SCORE == 1
        assert BalanceConstants.MAX_ABILITY_SCORE == 30
        
    def test_get_constant_existing(self): pass
        """Test getting an existing constant."""
        result = BalanceConstants.get_constant('BASE_XP')
        assert result == 1000
        
    def test_get_constant_nonexistent_with_default(self): pass
        """Test getting a nonexistent constant with default value."""
        result = BalanceConstants.get_constant('NONEXISTENT_CONSTANT', 42)
        assert result == 42
        
    def test_get_constant_nonexistent_without_default(self): pass
        """Test getting a nonexistent constant without default value."""
        result = BalanceConstants.get_constant('NONEXISTENT_CONSTANT')
        assert result is None
        
    def test_set_constant(self): pass
        """Test setting a constant value."""
        original_value = BalanceConstants.BASE_XP
        try: pass
            BalanceConstants.set_constant('BASE_XP', 2000)
            assert BalanceConstants.BASE_XP == 2000
        finally: pass
            # Restore original value
            BalanceConstants.set_constant('BASE_XP', original_value)
            
    def test_set_new_constant(self): pass
        """Test setting a new constant."""
        BalanceConstants.set_constant('NEW_CONSTANT', 123)
        assert BalanceConstants.NEW_CONSTANT == 123
        # Clean up
        delattr(BalanceConstants, 'NEW_CONSTANT')
        
    def test_load_from_file_success(self): pass
        """Test successfully loading constants from file."""
        test_data = {
            'BASE_XP': 1500,
            'MAX_LEVEL': 25,
            'NEW_CONSTANT': 999
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
            json.dump(test_data, f)
            temp_file = f.name
            
        try: pass
            original_base_xp = BalanceConstants.BASE_XP
            original_max_level = BalanceConstants.MAX_LEVEL
            
            with patch('backend.systems.shared.rules.logger') as mock_logger: pass
                BalanceConstants.load_from_file(temp_file)
                
                # Check that existing constants were updated
                assert BalanceConstants.BASE_XP == 1500
                assert BalanceConstants.MAX_LEVEL == 25
                
                # Check that debug messages were logged for existing constants
                mock_logger.debug.assert_any_call("Updated balance constant BASE_XP = 1500")
                mock_logger.debug.assert_any_call("Updated balance constant MAX_LEVEL = 25")
                
                # Check that warning was logged for unknown constant
                mock_logger.warning.assert_called_with("Unknown balance constant: NEW_CONSTANT")
                
        finally: pass
            # Restore original values
            BalanceConstants.BASE_XP = original_base_xp
            BalanceConstants.MAX_LEVEL = original_max_level
            os.unlink(temp_file)
            
    def test_load_from_file_not_found(self): pass
        """Test loading from nonexistent file."""
        with patch('backend.systems.shared.rules.logger') as mock_logger: pass
            BalanceConstants.load_from_file('nonexistent_file.json')
            mock_logger.warning.assert_called_with("Balance constants file not found: nonexistent_file.json")
            
    def test_load_from_file_json_error(self): pass
        """Test loading from file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
            f.write("invalid json content")
            temp_file = f.name
            
        try: pass
            with patch('backend.systems.shared.rules.logger') as mock_logger: pass
                BalanceConstants.load_from_file(temp_file)
                # Should log an error
                assert mock_logger.error.called
                error_call = mock_logger.error.call_args[0][0]
                assert "Error loading balance constants" in error_call
        finally: pass
            os.unlink(temp_file)
            
    def test_save_to_file_success(self): pass
        """Test successfully saving constants to file."""
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_file = Path(temp_dir) / 'test_constants.json'
            
            with patch('backend.systems.shared.rules.logger') as mock_logger: pass
                BalanceConstants.save_to_file(temp_file)
                
                # Check that file was created
                assert temp_file.exists()
                
                # Check that success message was logged
                mock_logger.info.assert_called_with(f"Saved balance constants to {temp_file}")
                
                # Check file contents
                with open(temp_file, 'r') as f: pass
                    data = json.load(f)
                    
                # Should contain uppercase constants
                assert 'BASE_XP' in data
                assert 'MAX_LEVEL' in data
                assert data['BASE_XP'] == BalanceConstants.BASE_XP
                
    def test_save_to_file_error(self): pass
        """Test saving to file with permission error."""
        invalid_path = '/invalid/path/constants.json'
        
        with patch('backend.systems.shared.rules.logger') as mock_logger: pass
            BalanceConstants.save_to_file(invalid_path)
            # Should log an error
            assert mock_logger.error.called
            error_call = mock_logger.error.call_args[0][0]
            assert "Error saving balance constants" in error_call


class TestDataLoadingUtilities: pass
    """Test class for data loading utilities"""
    
    def test_load_data_json_success(self): pass
        """Test successfully loading JSON data."""
        test_data = {'key1': 'value1', 'key2': 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
            json.dump(test_data, f)
            temp_file = f.name
            
        try: pass
            result = load_data(temp_file, 'json')
            assert result == test_data
        finally: pass
            os.unlink(temp_file)
            
    def test_load_data_json_file_not_found(self): pass
        """Test loading JSON data from nonexistent file."""
        with pytest.raises(FileNotFoundError): pass
            load_data('nonexistent_file.json', 'json')
            
    def test_load_data_yaml_supported(self): pass
        """Test loading YAML data (supported format)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f: pass
            f.write("key: value")
            temp_file = f.name
            
        try: pass
            # YAML is actually supported in the implementation
            result = load_data(temp_file, 'yaml')
            assert result == {'key': 'value'}
        except ImportError: pass
            # If PyYAML is not installed, skip this test
            pytest.skip("PyYAML not available")
        finally: pass
            os.unlink(temp_file)
            
    def test_load_data_invalid_json(self): pass
        """Test loading invalid JSON data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
            f.write("invalid json")
            temp_file = f.name
            
        try: pass
            with pytest.raises(json.JSONDecodeError): pass
                load_data(temp_file, 'json')
        finally: pass
            os.unlink(temp_file)
            
    def test_save_data_json_success(self): pass
        """Test successfully saving JSON data."""
        test_data = {'key1': 'value1', 'key2': 42}
        
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_file = Path(temp_dir) / 'test_data.json'
            
            save_data(test_data, temp_file, 'json')
            
            # Check that file was created and contains correct data
            assert temp_file.exists()
            with open(temp_file, 'r') as f: pass
                loaded_data = json.load(f)
            assert loaded_data == test_data
            
    def test_save_data_yaml_supported(self): pass
        """Test saving YAML data (supported format)."""
        test_data = {'key': 'value'}
        
        with tempfile.TemporaryDirectory() as temp_dir: pass
            temp_file = Path(temp_dir) / 'test_data.yaml'
            
            try: pass
                # YAML is actually supported in the implementation
                save_data(test_data, temp_file, 'yaml')
                assert temp_file.exists()
            except ImportError: pass
                # If PyYAML is not installed, skip this test
                pytest.skip("PyYAML not available")
                
    def test_save_data_permission_error(self): pass
        """Test saving data with permission error."""
        test_data = {'key': 'value'}
        invalid_path = '/invalid/path/data.json'
        
        # The implementation catches all exceptions and logs them
        with patch('backend.systems.shared.rules.logger') as mock_logger: pass
            with pytest.raises(OSError): pass
                save_data(test_data, invalid_path, 'json')
            # Should log an error
            assert mock_logger.error.called


class TestGameRulesLoading: pass
    """Test class for game rules loading functions"""
    
    @patch('backend.systems.shared.rules.load_data')
    def test_load_game_rules_success(self, mock_load_data): pass
        """Test successfully loading game rules."""
        mock_data = {'rule1': 'value1', 'rule2': 'value2'}
        mock_load_data.return_value = mock_data
        
        result = load_game_rules('test_rules')
        
        # Check that load_data was called with correct path (string, not Path)
        mock_load_data.assert_called_with('data/rules/test_rules.json')
        assert result == mock_data
        
    @patch('backend.systems.shared.rules.load_data')
    def test_load_game_rules_file_not_found(self, mock_load_data): pass
        """Test loading game rules when file not found."""
        mock_load_data.side_effect = FileNotFoundError("File not found")
        
        with patch('backend.systems.shared.rules.logger') as mock_logger: pass
            result = load_game_rules('nonexistent_rules')
            
            assert result == {}
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "Rules file not found for" in warning_call
            
    @patch('backend.systems.shared.rules.load_data')
    def test_load_game_rules_other_error(self, mock_load_data): pass
        """Test loading game rules with other error."""
        mock_load_data.side_effect = ValueError("Invalid data")
        
        with patch('backend.systems.shared.rules.logger') as mock_logger: pass
            # The implementation doesn't catch other exceptions, they propagate
            with pytest.raises(ValueError): pass
                load_game_rules('invalid_rules')


class TestClassAndRaceData: pass
    """Test class for class and race data functions"""
    
    @patch('backend.systems.shared.rules.load_game_rules')
    def test_get_class_data_success(self, mock_load_rules): pass
        """Test successfully getting class data."""
        mock_classes_data = {
            'wizard': {'hit_die': 6, 'spellcasting': 'intelligence'},
            'fighter': {'hit_die': 10, 'spellcasting': None}
        }
        mock_load_rules.return_value = mock_classes_data
        
        result = get_class_data('wizard')
        
        mock_load_rules.assert_called_once_with('classes')
        assert result == {'hit_die': 6, 'spellcasting': 'intelligence'}
        
    @patch('backend.systems.shared.rules.load_game_rules')
    def test_get_class_data_not_found(self, mock_load_rules): pass
        """Test getting class data for nonexistent class."""
        mock_classes_data = {'wizard': {'hit_die': 6}}
        mock_load_rules.return_value = mock_classes_data
        
        result = get_class_data('nonexistent_class')
        
        assert result == {}
        
    @patch('backend.systems.shared.rules.load_game_rules')
    def test_get_race_data_success(self, mock_load_rules): pass
        """Test successfully getting race data."""
        mock_races_data = {
            'elf': {'ability_bonus': {'dexterity': 2}, 'size': 'medium'},
            'dwarf': {'ability_bonus': {'constitution': 2}, 'size': 'medium'}
        }
        mock_load_rules.return_value = mock_races_data
        
        result = get_race_data('elf')
        
        mock_load_rules.assert_called_once_with('races')
        assert result == {'ability_bonus': {'dexterity': 2}, 'size': 'medium'}
        
    @patch('backend.systems.shared.rules.load_game_rules')
    def test_get_race_data_not_found(self, mock_load_rules): pass
        """Test getting race data for nonexistent race."""
        mock_races_data = {'elf': {'ability_bonus': {'dexterity': 2}}}
        mock_load_rules.return_value = mock_races_data
        
        result = get_race_data('nonexistent_race')
        
        assert result == {}


class TestCalculationFunctions: pass
    """Test class for calculation functions"""
    
    def test_calculate_xp_for_level_valid_levels(self): pass
        """Test XP calculation for valid levels."""
        # Level 1 should be 0 XP
        assert calculate_xp_for_level(1) == 0
        
        # Level 2 should be BASE_XP * (2-1)^SCALING_FACTOR = BASE_XP * 1^1.5 = BASE_XP
        assert calculate_xp_for_level(2) == BalanceConstants.BASE_XP
        
        # Level 3 should be BASE_XP * (3-1)^SCALING_FACTOR = BASE_XP * 2^1.5
        expected_level_3 = int(BalanceConstants.BASE_XP * (2 ** BalanceConstants.XP_SCALING_FACTOR))
        assert calculate_xp_for_level(3) == expected_level_3
        
    def test_calculate_xp_for_level_invalid_levels(self): pass
        """Test XP calculation for invalid levels."""
        # Level 0 or negative should return 0
        assert calculate_xp_for_level(0) == 0
        assert calculate_xp_for_level(-1) == 0
        
        # Level above max should still calculate (no capping in implementation)
        level_21_xp = calculate_xp_for_level(BalanceConstants.MAX_LEVEL + 1)
        level_20_xp = calculate_xp_for_level(BalanceConstants.MAX_LEVEL)
        assert level_21_xp > level_20_xp
        
    def test_calculate_ability_modifier_standard_scores(self): pass
        """Test ability modifier calculation for standard scores."""
        # Score 10-11 should have modifier 0
        assert calculate_ability_modifier(10) == 0
        assert calculate_ability_modifier(11) == 0
        
        # Score 12-13 should have modifier +1
        assert calculate_ability_modifier(12) == 1
        assert calculate_ability_modifier(13) == 1
        
        # Score 8-9 should have modifier -1
        assert calculate_ability_modifier(8) == -1
        assert calculate_ability_modifier(9) == -1
        
        # Score 20 should have modifier +5
        assert calculate_ability_modifier(20) == 5
        
        # Score 1 should have modifier -5
        assert calculate_ability_modifier(1) == -5
        
    def test_calculate_ability_modifier_extreme_scores(self): pass
        """Test ability modifier calculation for extreme scores."""
        # Very high score
        assert calculate_ability_modifier(30) == 10
        
        # Very low score (below minimum)
        assert calculate_ability_modifier(0) == -5


class TestGlobalInstance: pass
    """Test class for global balance_constants instance"""
    
    def test_global_instance_exists(self): pass
        """Test that global balance_constants instance exists."""
        assert balance_constants is not None
        assert isinstance(balance_constants, BalanceConstants)
        
    def test_global_instance_has_constants(self): pass
        """Test that global instance has expected constants."""
        assert balance_constants.BASE_XP == 1000
        assert balance_constants.MAX_LEVEL == 20
        assert hasattr(balance_constants, 'CLASS_SPELLCASTING_ABILITY')
