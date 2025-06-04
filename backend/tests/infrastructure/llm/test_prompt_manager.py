"""
Comprehensive Test Suite for Prompt Management System

Tests cover all aspects of the centralized prompt management system including:
- Template registration and discovery
- Prompt generation with quality control
- Performance metrics and caching
- Error handling and fallback scenarios
- Integration with model manager

Ensures ≥90% test coverage as required by Task 71.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from backend.infrastructure.llm.services.prompt_manager import (
    PromptManager, PromptTemplate, TemplateCategory, get_prompt_manager, register_template_from_dict
)
from backend.infrastructure.llm.services.model_manager import ModelType


class TestPromptTemplate:
    """Test suite for PromptTemplate data structure"""
    
    def test_prompt_template_creation(self):
        """Test basic template creation with required fields"""
        template = PromptTemplate(
            name="test_template",
            system_prompt="You are a test assistant.",
            user_prompt_template="Test prompt with {variable}",
            description="Test template for unit tests"
        )
        
        assert template.name == "test_template"
        assert template.system_prompt == "You are a test assistant."
        assert template.user_prompt_template == "Test prompt with {variable}"
        assert template.description == "Test template for unit tests"
        assert template.version == "1.0"  # Default value
        assert template.category == "utility"  # Default value
        assert template.created_at is not None
        assert template.updated_at is not None
    
    def test_prompt_template_with_all_fields(self):
        """Test template creation with all optional fields"""
        template = PromptTemplate(
            name="comprehensive_template",
            system_prompt="System prompt",
            user_prompt_template="User prompt with {var1} and {var2}",
            description="Comprehensive test template",
            version="2.1",
            category="test",
            tags=["test", "comprehensive"],
            model="gpt-4",
            batch_eligible=True,
            author="test_author",
            required_variables=["var1", "var2"],
            optional_variables=["var3"],
            context_requirements={"min_context": 100}
        )
        
        assert template.version == "2.1"
        assert template.category == "test"
        assert template.tags == ["test", "comprehensive"]
        assert template.model == "gpt-4"
        assert template.batch_eligible is True
        assert template.author == "test_author"
        assert template.required_variables == ["var1", "var2"]
        assert template.optional_variables == ["var3"]
        assert template.context_requirements == {"min_context": 100}
    
    def test_validate_variables_success(self):
        """Test successful variable validation"""
        template = PromptTemplate(
            name="test",
            system_prompt="System",
            user_prompt_template="Template with {required_var}",
            description="Test",
            required_variables=["required_var"],
            optional_variables=["optional_var"]
        )
        
        variables = {"required_var": "value", "optional_var": "optional_value"}
        valid, missing = template.validate_variables(variables)
        
        assert valid is True
        assert missing == []
    
    def test_validate_variables_missing_required(self):
        """Test variable validation with missing required variables"""
        template = PromptTemplate(
            name="test",
            system_prompt="System",
            user_prompt_template="Template with {required_var}",
            description="Test",
            required_variables=["required_var", "another_required"],
            optional_variables=["optional_var"]
        )
        
        variables = {"optional_var": "optional_value"}
        valid, missing = template.validate_variables(variables)
        
        assert valid is False
        assert set(missing) == {"required_var", "another_required"}
    
    def test_format_prompt_success(self):
        """Test successful prompt formatting"""
        template = PromptTemplate(
            name="test",
            system_prompt="You are a {role}.",
            user_prompt_template="Please {action} the {object}.",
            description="Test",
            required_variables=["role", "action", "object"]
        )
        
        variables = {"role": "assistant", "action": "analyze", "object": "data"}
        system_prompt, user_prompt = template.format_prompt(variables)
        
        assert system_prompt == "You are a assistant."
        assert user_prompt == "Please analyze the data."
    
    def test_format_prompt_missing_variables(self):
        """Test prompt formatting with missing variables"""
        template = PromptTemplate(
            name="test",
            system_prompt="System",
            user_prompt_template="Template with {missing_var}",
            description="Test",
            required_variables=["missing_var"]
        )
        
        variables = {}
        
        with pytest.raises(ValueError, match="Missing required variables"):
            template.format_prompt(variables)
    
    def test_format_prompt_template_error(self):
        """Test prompt formatting with template formatting error"""
        template = PromptTemplate(
            name="test",
            system_prompt="System",
            user_prompt_template="Template with {undefined_var}",
            description="Test",
            required_variables=[]  # No required variables, but template uses undefined_var
        )
        
        variables = {}
        
        with pytest.raises(ValueError, match="Template variable not provided"):
            template.format_prompt(variables)
    
    def test_update_metrics(self):
        """Test metrics updating functionality"""
        template = PromptTemplate(
            name="test",
            system_prompt="System",
            user_prompt_template="Template",
            description="Test"
        )
        
        # Initial state
        assert template.usage_count == 0
        assert template.success_rate == 1.0
        assert template.avg_response_time == 0.0
        
        # First successful use
        template.update_metrics(1.5, True)
        assert template.usage_count == 1
        assert template.success_rate == 1.0
        assert template.avg_response_time == 1.5
        
        # Second use with failure
        template.update_metrics(2.0, False)
        assert template.usage_count == 2
        assert template.success_rate == 0.5  # 1 success out of 2 attempts
        assert template.avg_response_time == 1.75  # (1.5 + 2.0) / 2
        
        # Third successful use
        template.update_metrics(1.0, True)
        assert template.usage_count == 3
        assert template.success_rate == 2.0/3.0  # 2 successes out of 3 attempts
        assert template.avg_response_time == (1.5 + 2.0 + 1.0) / 3


class TestPromptManager:
    """Test suite for PromptManager functionality"""
    
    @pytest.fixture
    async def prompt_manager(self):
        """Create a fresh PromptManager instance for testing"""
        manager = PromptManager()
        
        # Mock the model manager to avoid external dependencies
        mock_model_manager = AsyncMock()
        mock_model_manager.generate_response = AsyncMock(return_value={
            "response": "Generated response",
            "tokens_used": 50,
            "cost_usd": 0.001,
            "model_used": "test-model"
        })
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        return manager
    
    @pytest.fixture
    def sample_template(self):
        """Create a sample template for testing"""
        return PromptTemplate(
            name="sample_template",
            system_prompt="You are a helpful assistant.",
            user_prompt_template="Please help with {task}.",
            description="Sample template for testing",
            category="test",
            tags=["sample", "test"],
            required_variables=["task"]
        )
    
    async def test_initialization(self):
        """Test PromptManager initialization"""
        manager = PromptManager()
        
        # Mock dependencies
        mock_model_manager = AsyncMock()
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        assert manager.model_manager is not None
        assert len(manager.templates) > 0  # Should have core templates
        assert "system_dm_persona" in manager.templates
        assert "npc_dialogue_basic" in manager.templates
        assert "location_description" in manager.templates
        assert "quest_hook_generation" in manager.templates
    
    async def test_register_template(self, prompt_manager, sample_template):
        """Test template registration"""
        success = prompt_manager.register_template(sample_template)
        
        assert success is True
        assert sample_template.name in prompt_manager.templates
        assert prompt_manager.templates[sample_template.name] == sample_template
        
        # Check indexing
        assert sample_template.name in prompt_manager.category_index["test"]
        assert sample_template.name in prompt_manager.tag_index["sample"]
        assert sample_template.name in prompt_manager.tag_index["test"]
    
    async def test_register_template_error_handling(self, prompt_manager):
        """Test template registration error handling"""
        # Create a template that will cause an error during registration
        invalid_template = Mock()
        invalid_template.name = "invalid"
        invalid_template.category = "test"
        invalid_template.tags = ["test"]
        
        # Mock the template to raise an exception when accessed
        type(invalid_template).name = Mock(side_effect=Exception("Test error"))
        
        success = prompt_manager.register_template(invalid_template)
        assert success is False
    
    async def test_get_template(self, prompt_manager, sample_template):
        """Test template retrieval"""
        prompt_manager.register_template(sample_template)
        
        retrieved = prompt_manager.get_template("sample_template")
        assert retrieved == sample_template
        
        # Test non-existent template
        not_found = prompt_manager.get_template("non_existent")
        assert not_found is None
    
    async def test_find_templates_by_category(self, prompt_manager, sample_template):
        """Test finding templates by category"""
        prompt_manager.register_template(sample_template)
        
        # Find by category
        test_templates = prompt_manager.find_templates(category="test")
        assert len(test_templates) == 1
        assert test_templates[0] == sample_template
        
        # Find by non-existent category
        empty_results = prompt_manager.find_templates(category="non_existent")
        assert len(empty_results) == 0
    
    async def test_find_templates_by_tags(self, prompt_manager, sample_template):
        """Test finding templates by tags"""
        prompt_manager.register_template(sample_template)
        
        # Find by single tag
        sample_templates = prompt_manager.find_templates(tags=["sample"])
        assert len(sample_templates) == 1
        assert sample_templates[0] == sample_template
        
        # Find by multiple tags (AND operation)
        both_tags = prompt_manager.find_templates(tags=["sample", "test"])
        assert len(both_tags) == 1
        assert both_tags[0] == sample_template
        
        # Find by non-existent tag
        empty_results = prompt_manager.find_templates(tags=["non_existent"])
        assert len(empty_results) == 0
    
    async def test_find_templates_by_model_type(self, prompt_manager):
        """Test finding templates by model type"""
        # Create templates with different models
        template1 = PromptTemplate(
            name="gpt4_template",
            system_prompt="System",
            user_prompt_template="Template",
            description="GPT-4 template",
            model="gpt-4"
        )
        
        template2 = PromptTemplate(
            name="claude_template",
            system_prompt="System",
            user_prompt_template="Template",
            description="Claude template",
            model="claude-3"
        )
        
        prompt_manager.register_template(template1)
        prompt_manager.register_template(template2)
        
        # Find by model type
        gpt4_templates = prompt_manager.find_templates(model_type="gpt-4")
        assert len(gpt4_templates) == 1
        assert gpt4_templates[0] == template1
        
        claude_templates = prompt_manager.find_templates(model_type="claude-3")
        assert len(claude_templates) == 1
        assert claude_templates[0] == template2
    
    async def test_generate_success(self, prompt_manager, sample_template):
        """Test successful content generation"""
        prompt_manager.register_template(sample_template)
        
        variables = {"task": "write a test"}
        result = await prompt_manager.generate(
            template_name="sample_template",
            variables=variables
        )
        
        assert "response" in result
        assert result["response"] == "Generated response"
        assert "template" in result
        assert result["template"]["name"] == "sample_template"
        assert result["generation_time"] > 0
        assert result["cached"] is False
        
        # Check that template metrics were updated
        assert sample_template.usage_count == 1
    
    async def test_generate_template_not_found(self, prompt_manager):
        """Test generation with non-existent template"""
        with pytest.raises(ValueError, match="Template not found"):
            await prompt_manager.generate(
                template_name="non_existent",
                variables={}
            )
    
    async def test_generate_missing_variables(self, prompt_manager, sample_template):
        """Test generation with missing required variables"""
        prompt_manager.register_template(sample_template)
        
        with pytest.raises(ValueError, match="Missing required variables"):
            await prompt_manager.generate(
                template_name="sample_template",
                variables={}  # Missing required 'task' variable
            )
    
    async def test_generate_with_caching(self, prompt_manager, sample_template):
        """Test generation with response caching"""
        prompt_manager.register_template(sample_template)
        
        variables = {"task": "write a test"}
        cache_key = "test_cache_key"
        
        # First generation - should not be cached
        result1 = await prompt_manager.generate(
            template_name="sample_template",
            variables=variables,
            cache_key=cache_key
        )
        assert result1["cached"] is False
        
        # Second generation - should be cached
        result2 = await prompt_manager.generate(
            template_name="sample_template",
            variables=variables,
            cache_key=cache_key
        )
        assert result2["cached"] is True
        assert result2["response"] == result1["response"]
    
    async def test_generate_model_override(self, prompt_manager, sample_template):
        """Test generation with model override"""
        prompt_manager.register_template(sample_template)
        
        variables = {"task": "write a test"}
        
        # Mock model manager to verify the correct model is used
        mock_generate = AsyncMock(return_value={
            "response": "Override response",
            "tokens_used": 30,
            "cost_usd": 0.0005,
            "model_used": "override-model"
        })
        prompt_manager.model_manager.generate_response = mock_generate
        
        result = await prompt_manager.generate(
            template_name="sample_template",
            variables=variables,
            model_override="override-model"
        )
        
        # Verify the override model was used
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args[1]["model_name"] == "override-model"
    
    async def test_generate_error_handling(self, prompt_manager, sample_template):
        """Test generation error handling"""
        prompt_manager.register_template(sample_template)
        
        # Mock model manager to raise an exception
        prompt_manager.model_manager.generate_response = AsyncMock(
            side_effect=Exception("Model error")
        )
        
        variables = {"task": "write a test"}
        
        with pytest.raises(Exception, match="Model error"):
            await prompt_manager.generate(
                template_name="sample_template",
                variables=variables
            )
        
        # Check that template metrics were updated for failure
        assert sample_template.usage_count == 1
        assert sample_template.success_rate < 1.0
    
    async def test_cache_management(self, prompt_manager):
        """Test cache TTL and cleanup"""
        # Test cache entry and retrieval
        test_response = {"test": "data", "timestamp": time.time()}
        prompt_manager._cache_response("test_key", test_response)
        
        # Should retrieve valid cache entry
        cached = prompt_manager._get_cached_response("test_key")
        assert cached is not None
        assert cached["test"] == "data"
        
        # Test expired cache entry
        old_response = {"test": "old_data", "timestamp": time.time() - 2000}  # Expired
        prompt_manager.cache["old_key"] = {
            "data": old_response,
            "timestamp": time.time() - 2000
        }
        
        expired = prompt_manager._get_cached_response("old_key")
        assert expired is None
        assert "old_key" not in prompt_manager.cache  # Should be cleaned up
    
    async def test_get_metrics(self, prompt_manager, sample_template):
        """Test metrics collection"""
        prompt_manager.register_template(sample_template)
        
        # Generate some usage
        variables = {"task": "test task"}
        await prompt_manager.generate("sample_template", variables)
        
        metrics = await prompt_manager.get_metrics()
        
        assert "service_metrics" in metrics
        assert "template_count" in metrics
        assert "categories" in metrics
        assert "cache_size" in metrics
        assert "cache_hit_rate" in metrics
        assert "template_performance" in metrics
        
        assert metrics["template_count"] > 0
        assert "sample_template" in metrics["template_performance"]
        assert metrics["template_performance"]["sample_template"]["usage_count"] == 1
    
    async def test_clear_cache(self, prompt_manager):
        """Test cache clearing"""
        # Add some cache entries
        prompt_manager._cache_response("key1", {"data": "test1"})
        prompt_manager._cache_response("key2", {"data": "test2"})
        
        assert len(prompt_manager.cache) == 2
        
        await prompt_manager.clear_cache()
        
        assert len(prompt_manager.cache) == 0


class TestGlobalFunctions:
    """Test suite for global utility functions"""
    
    async def test_get_prompt_manager_singleton(self):
        """Test that get_prompt_manager returns singleton instance"""
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager'):
            manager1 = await get_prompt_manager()
            manager2 = await get_prompt_manager()
            
            assert manager1 is manager2  # Should be the same instance
    
    async def test_register_template_from_dict(self):
        """Test template registration from dictionary"""
        template_data = {
            "name": "dict_template",
            "system_prompt": "System prompt",
            "user_prompt_template": "User prompt with {variable}",
            "description": "Template from dict",
            "category": "test",
            "tags": ["dict", "test"],
            "required_variables": ["variable"]
        }
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager'):
            success = await register_template_from_dict(template_data)
            assert success is True
            
            # Verify template was registered
            manager = await get_prompt_manager()
            template = manager.get_template("dict_template")
            assert template is not None
            assert template.name == "dict_template"
            assert template.description == "Template from dict"


class TestTemplateCategory:
    """Test suite for TemplateCategory enum"""
    
    def test_template_categories(self):
        """Test that all expected categories are defined"""
        expected_categories = [
            "system", "formatting", "context", "quest", "npc", 
            "world", "combat", "item", "utility", "dialogue", "narrative"
        ]
        
        for category in expected_categories:
            assert hasattr(TemplateCategory, category.upper())
            assert getattr(TemplateCategory, category.upper()).value == category


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    @pytest.fixture
    async def full_prompt_manager(self):
        """Create a fully initialized prompt manager with mock dependencies"""
        manager = PromptManager()
        
        # Mock model manager with realistic responses
        mock_model_manager = AsyncMock()
        mock_model_manager.generate_response = AsyncMock(return_value={
            "response": "Generated response for integration test",
            "tokens_used": 75,
            "cost_usd": 0.002,
            "model_used": "integration-test-model"
        })
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        return manager
    
    async def test_full_workflow_npc_dialogue(self, full_prompt_manager):
        """Test complete workflow for NPC dialogue generation"""
        # Use the built-in NPC dialogue template
        variables = {
            "character_name": "Elara the Merchant",
            "character_background": "A wise trader who has traveled many lands",
            "current_situation": "Standing in her shop, organizing inventory",
            "player_message": "Do you have any rare items for sale?"
        }
        
        result = await full_prompt_manager.generate(
            template_name="npc_dialogue_basic",
            variables=variables,
            cache_key="npc_elara_rare_items"
        )
        
        assert result["response"] == "Generated response for integration test"
        assert result["template"]["name"] == "npc_dialogue_basic"
        assert result["template"]["category"] == "npc"
        assert result["cached"] is False
        
        # Test caching works
        cached_result = await full_prompt_manager.generate(
            template_name="npc_dialogue_basic",
            variables=variables,
            cache_key="npc_elara_rare_items"
        )
        
        assert cached_result["cached"] is True
    
    async def test_full_workflow_location_description(self, full_prompt_manager):
        """Test complete workflow for location description generation"""
        variables = {
            "location_name": "The Whispering Woods",
            "location_type": "Ancient Forest",
            "notable_features": "Glowing mushrooms and ethereal mist",
            "time_of_day": "twilight",
            "weather": "light rain"
        }
        
        result = await full_prompt_manager.generate(
            template_name="location_description",
            variables=variables
        )
        
        assert result["response"] == "Generated response for integration test"
        assert result["template"]["name"] == "location_description"
        assert result["template"]["category"] == "world"
    
    async def test_performance_under_load(self, full_prompt_manager):
        """Test performance with multiple concurrent requests"""
        variables = {
            "quest_type": "exploration",
            "difficulty": "medium",
            "location": "Ancient Ruins",
            "player_level": 5
        }
        
        # Generate multiple requests concurrently
        tasks = []
        for i in range(10):
            task = full_prompt_manager.generate(
                template_name="quest_hook_generation",
                variables=variables,
                cache_key=f"quest_load_test_{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(results) == 10
        for result in results:
            assert "response" in result
            assert result["template"]["name"] == "quest_hook_generation"
        
        # Check metrics
        metrics = await full_prompt_manager.get_metrics()
        assert metrics["service_metrics"]["total_generations"] >= 10
    
    async def test_error_recovery_and_metrics(self, full_prompt_manager):
        """Test error handling and metrics tracking"""
        # Create a template that will cause validation errors
        error_template = PromptTemplate(
            name="error_template",
            system_prompt="System",
            user_prompt_template="Template with {missing_var}",
            description="Template designed to cause errors",
            required_variables=["required_var"]  # Different from template variable
        )
        
        full_prompt_manager.register_template(error_template)
        
        # This should fail due to missing variables
        with pytest.raises(ValueError):
            await full_prompt_manager.generate(
                template_name="error_template",
                variables={"wrong_var": "value"}
            )
        
        # Check that error was tracked in metrics
        assert error_template.usage_count == 1
        assert error_template.success_rate == 0.0  # Failed attempt
        
        # Now provide correct variables
        await full_prompt_manager.generate(
            template_name="error_template",
            variables={"required_var": "value", "missing_var": "value"}
        )
        
        # Metrics should show recovery
        assert error_template.usage_count == 2
        assert error_template.success_rate == 0.5  # 1 success out of 2 attempts


# Performance and stress tests
class TestPerformanceAndStress:
    """Performance and stress testing for the prompt management system"""
    
    async def test_large_template_library_performance(self):
        """Test performance with a large number of templates"""
        manager = PromptManager()
        
        # Mock model manager
        mock_model_manager = AsyncMock()
        mock_model_manager.generate_response = AsyncMock(return_value={
            "response": "Performance test response",
            "tokens_used": 25,
            "cost_usd": 0.0001,
            "model_used": "perf-test-model"
        })
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        # Register many templates
        start_time = time.time()
        for i in range(100):
            template = PromptTemplate(
                name=f"perf_template_{i}",
                system_prompt="System prompt",
                user_prompt_template=f"Template {i} with {{variable}}",
                description=f"Performance test template {i}",
                category=f"category_{i % 5}",  # 5 different categories
                tags=[f"tag_{i % 3}", "performance"],  # 3 different tags + performance
                required_variables=["variable"]
            )
            manager.register_template(template)
        
        registration_time = time.time() - start_time
        
        # Registration should be fast even with many templates
        assert registration_time < 1.0  # Should complete in under 1 second
        assert len(manager.templates) >= 100
        
        # Test search performance
        start_time = time.time()
        results = manager.find_templates(category="category_0")
        search_time = time.time() - start_time
        
        assert search_time < 0.1  # Search should be very fast
        assert len(results) == 20  # Should find 20 templates (100/5 categories)
    
    async def test_cache_performance_and_limits(self):
        """Test cache performance and size limits"""
        manager = PromptManager()
        
        # Mock model manager
        mock_model_manager = AsyncMock()
        mock_model_manager.generate_response = AsyncMock(return_value={
            "response": "Cache test response",
            "tokens_used": 30,
            "cost_usd": 0.0001,
            "model_used": "cache-test-model"
        })
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        # Add many cache entries to test size management
        for i in range(50):
            manager._cache_response(f"cache_key_{i}", {
                "response": f"Response {i}",
                "timestamp": time.time()
            })
        
        assert len(manager.cache) == 50
        
        # Test cache retrieval performance
        start_time = time.time()
        for i in range(50):
            result = manager._get_cached_response(f"cache_key_{i}")
            assert result is not None
        
        retrieval_time = time.time() - start_time
        assert retrieval_time < 0.1  # Should be very fast
    
    async def test_concurrent_access_safety(self):
        """Test thread safety with concurrent access"""
        manager = PromptManager()
        
        # Mock model manager
        mock_model_manager = AsyncMock()
        mock_model_manager.generate_response = AsyncMock(return_value={
            "response": "Concurrent test response",
            "tokens_used": 40,
            "cost_usd": 0.0001,
            "model_used": "concurrent-test-model"
        })
        
        with patch('backend.infrastructure.llm.services.prompt_manager.get_model_manager', 
                  return_value=mock_model_manager):
            await manager.initialize()
        
        # Register a test template
        template = PromptTemplate(
            name="concurrent_template",
            system_prompt="System",
            user_prompt_template="Concurrent test with {variable}",
            description="Concurrent access test",
            required_variables=["variable"]
        )
        manager.register_template(template)
        
        # Run multiple concurrent operations
        async def concurrent_operation(operation_id: int):
            variables = {"variable": f"value_{operation_id}"}
            return await manager.generate(
                template_name="concurrent_template",
                variables=variables,
                cache_key=f"concurrent_{operation_id}"
            )
        
        # Execute many concurrent operations
        tasks = [concurrent_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert len(results) == 20
        for i, result in enumerate(results):
            assert "response" in result
            assert result["template"]["name"] == "concurrent_template"
        
        # Template metrics should be consistent
        assert template.usage_count == 20
        assert template.success_rate == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend.infrastructure.llm.services.prompt_manager", "--cov-report=term-missing"]) 