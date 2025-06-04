class TestCharacterConfigurationLoading:
    """Test JSON configuration loading and validation"""
    
    def test_load_skills_configuration(self, character_service):
        """Test loading skills.json configuration"""
        # Test that skills configuration loads properly
        config = character_service._load_json_config('skills.json')
        assert config is not None
        assert 'skills' in config
        
        # Verify structure matches expected format
        skills = config['skills']
        for skill_name, skill_data in skills.items():
            assert isinstance(skill_name, str)
            assert 'ability' in skill_data
            assert 'description' in skill_data
            assert skill_data['ability'] in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    
    def test_load_personality_traits_configuration(self, character_service):
        """Test loading personality_traits.json configuration"""
        config = character_service._load_json_config('personality_traits.json')
        assert config is not None
        assert 'personality_traits' in config
        
        # Verify trait structure
        traits = config['personality_traits']
        for trait_name, trait_data in traits.items():
            assert isinstance(trait_name, str)
            assert 'description' in trait_data
            assert 'behavioral_indicators' in trait_data
            assert isinstance(trait_data['behavioral_indicators'], list)
    
    def test_load_validation_rules_configuration(self, character_service):
        """Test loading validation_rules.json configuration"""
        config = character_service._load_json_config('validation_rules.json')
        assert config is not None
        
        # Verify validation rules structure
        assert 'stats' in config
        assert 'skills' in config
        assert 'personality' in config
        assert 'character_creation' in config
        
        # Test stats validation rules
        stats_rules = config['stats']
        assert 'min_value' in stats_rules
        assert 'max_value' in stats_rules
        assert 'default_value' in stats_rules
        assert stats_rules['min_value'] <= stats_rules['default_value'] <= stats_rules['max_value']
    
    def test_load_progression_rules_configuration(self, character_service):
        """Test loading progression_rules.json configuration"""
        config = character_service._load_json_config('progression_rules.json')
        assert config is not None
        
        # Verify progression rules structure
        assert 'experience_thresholds' in config
        assert 'ability_score_improvements' in config
        
        # Test experience thresholds are properly ordered
        thresholds = config['experience_thresholds']
        previous_xp = 0
        for level, xp_required in thresholds.items():
            level_num = int(level)
            assert level_num >= 1 and level_num <= 20
            assert xp_required >= previous_xp
            previous_xp = xp_required
    
    def test_load_equipment_integration_configuration(self, character_service):
        """Test loading equipment_integration.json configuration"""
        config = character_service._load_json_config('equipment_integration.json')
        assert config is not None
        
        # Verify equipment integration structure
        assert 'equipment_slots' in config
        assert 'stat_bonuses' in config
        assert 'proficiency_requirements' in config
        
        # Test equipment slots
        slots = config['equipment_slots']
        expected_slots = ['weapon', 'armor', 'shield', 'accessory']
        for slot in expected_slots:
            assert slot in slots
            assert 'max_items' in slots[slot]
            assert isinstance(slots[slot]['max_items'], int)
    
    def test_configuration_file_not_found_handling(self, character_service):
        """Test handling of missing configuration files"""
        config = character_service._load_json_config('nonexistent.json')
        assert config == {}
    
    def test_invalid_json_handling(self, character_service, tmp_path):
        """Test handling of malformed JSON files"""
        # Create a malformed JSON file
        invalid_json_file = tmp_path / "invalid.json"
        invalid_json_file.write_text('{"invalid": json}')  # Missing quotes around 'json'
        
        # Mock the file path to point to our invalid file
        import unittest.mock
        with unittest.mock.patch('backend.systems.character.services.character_service.os.path.join') as mock_join:
            mock_join.return_value = str(invalid_json_file)
            config = character_service._load_json_config('invalid.json')
            assert config == {}
    
    def test_configuration_validation_against_code_usage(self, character_service):
        """Test that JSON configurations match actual code usage patterns"""
        # Load skills config and verify it matches what the code expects
        skills_config = character_service._load_json_config('skills.json')
        
        # Test character creation with skills from config
        character_data = {
            'name': 'Test Character',
            'character_type': 'pc',
            'stats': {'STR': 2, 'DEX': 1, 'CON': 3, 'INT': 0, 'WIS': 1, 'CHA': -1},
            'skills': {}
        }
        
        # Add skills from configuration
        for skill_name in skills_config['skills'].keys():
            character_data['skills'][skill_name] = {
                'proficient': True,
                'expertise': False,
                'bonus': 0
            }
        
        # Verify character creation works with all configured skills
        character = character_service.create_character(character_data)
        assert character is not None
        
        # Verify all skills from config are properly handled
        for skill_name in skills_config['skills'].keys():
            assert skill_name in character.skills 