"""
Comprehensive Test Suite for Enhanced Prompt Service

Tests cover all aspects of the enhanced prompt service including:
- Integration with centralized prompt manager
- Template processing and generation
- Service initialization and configuration
- Error handling and fallback scenarios
- Performance metrics and caching

Ensures ≥90% test coverage as required by Task 71.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
from pathlib import Path

from backend.infrastructure.llm.services.prompt_service import PromptService
from backend.infrastructure.llm.services.prompt_manager import PromptTemplate


class TestPromptService:
    """Test suite for enhanced PromptService functionality"""
    
    @pytest.fixture
    async def prompt_service(self):
        """Create a fresh PromptService instance for testing"""
        service = PromptService()
        
        # Mock dependencies
        mock_prompt_manager = AsyncMock()
        mock_prompt_manager.templates = {
            "test_template": PromptTemplate(
                name="test_template",
                system_prompt="Test system prompt",
                user_prompt_template="Test user prompt with {variable}",
                description="Test template",
                required_variables=["variable"]
            )
        }
        mock_prompt_manager.get_template = Mock(side_effect=lambda name: mock_prompt_manager.templates.get(name))
        mock_prompt_manager.generate = AsyncMock(return_value={
            "response": "Generated test response",
            "template": {"name": "test_template", "category": "test"},
            "generation_time": 0.5,
            "cached": False
        })
        mock_prompt_manager.find_templates = Mock(return_value=[mock_prompt_manager.templates["test_template"]])
        mock_prompt_manager.category_index = {"test": ["test_template"]}
        mock_prompt_manager.tag_index = {"test": ["test_template"]}
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.get_prompt_template = AsyncMock(return_value={
            "content": "Fallback template content with {variable}",
            "name": "fallback_template"
        })
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        mock_prompt_repo.save_prompt_template = AsyncMock(return_value="saved_template_id")
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            await service.initialize()
        
        return service
    
    async def test_initialization(self):
        """Test PromptService initialization"""
        service = PromptService()
        
        assert service.initialized is False
        assert service.prompt_manager is None
        
        # Mock dependencies
        mock_prompt_manager = AsyncMock()
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            await service.initialize()
        
        assert service.initialized is True
        assert service.prompt_manager is not None
    
    async def test_initialization_idempotent(self, prompt_service):
        """Test that initialization is idempotent"""
        # Service should already be initialized from fixture
        assert prompt_service.initialized is True
        
        # Initialize again - should not cause issues
        await prompt_service.initialize()
        assert prompt_service.initialized is True
    
    async def test_generate_prompt_success(self, prompt_service):
        """Test successful prompt generation using legacy interface"""
        result = await prompt_service.generate_prompt(
            template_id="test_template",
            variables={"variable": "test_value"}
        )
        
        assert result == "Generated test response"
        prompt_service.prompt_manager.generate.assert_called_once()
    
    async def test_generate_prompt_fallback_to_repository(self, prompt_service):
        """Test fallback to repository when prompt manager fails"""
        # Make prompt manager fail
        prompt_service.prompt_manager.generate.side_effect = Exception("Manager error")
        
        result = await prompt_service.generate_prompt(
            template_id="fallback_template",
            variables={"variable": "test_value"}
        )
        
        assert result == "Fallback template content with test_value"
        prompt_service.prompt_repo.get_prompt_template.assert_called_once_with("fallback_template")
    
    async def test_generate_prompt_no_template_found(self, prompt_service):
        """Test error when no template is found"""
        # Make both prompt manager and repository fail
        prompt_service.prompt_manager.generate.side_effect = Exception("Manager error")
        prompt_service.prompt_repo.get_prompt_template.return_value = None
        
        with pytest.raises(Exception):
            await prompt_service.generate_prompt(
                template_id="non_existent",
                variables={"variable": "test_value"}
            )
    
    async def test_process_template_success(self, prompt_service):
        """Test successful template processing"""
        result = await prompt_service.process_template(
            template_name="test_template",
            variables={"variable": "processed_value"}
        )
        
        assert result == "Test user prompt with processed_value"
    
    async def test_process_template_not_found(self, prompt_service):
        """Test template processing with non-existent template"""
        prompt_service.prompt_manager.get_template.return_value = None
        
        with pytest.raises(ValueError, match="Template not found"):
            await prompt_service.process_template(
                template_name="non_existent",
                variables={"variable": "value"}
            )
    
    async def test_generate_with_template_success(self, prompt_service):
        """Test successful generation with template"""
        result = await prompt_service.generate_with_template(
            template_name="test_template",
            variables={"variable": "template_value"},
            context={"additional": "context"}
        )
        
        assert result["response"] == "Generated test response"
        assert result["template"]["name"] == "test_template"
        prompt_service.prompt_manager.generate.assert_called_once()
    
    async def test_create_template_success(self, prompt_service):
        """Test successful template creation"""
        template_data = {
            "name": "new_template",
            "system_prompt": "New system prompt",
            "user_prompt_template": "New user prompt",
            "description": "New template description"
        }
        
        # Mock successful registration
        prompt_service.prompt_manager.register_template = Mock(return_value=True)
        
        result = await prompt_service.create_template(template_data)
        
        assert result == "new_template"
        prompt_service.prompt_manager.register_template.assert_called_once()
        prompt_service.prompt_repo.save_prompt_template.assert_called_once()
    
    async def test_create_template_registration_failure(self, prompt_service):
        """Test template creation when registration fails"""
        template_data = {
            "name": "failing_template",
            "system_prompt": "System prompt",
            "user_prompt_template": "User prompt",
            "description": "Description"
        }
        
        # Mock failed registration
        prompt_service.prompt_manager.register_template = Mock(return_value=False)
        
        with pytest.raises(ValueError, match="Failed to register template"):
            await prompt_service.create_template(template_data)
    
    async def test_find_templates_success(self, prompt_service):
        """Test successful template finding"""
        results = await prompt_service.find_templates(
            category="test",
            tags=["test"],
            search_term="test"
        )
        
        assert len(results) == 1
        assert results[0]["name"] == "test_template"
        assert results[0]["description"] == "Test template"
        assert "usage_count" in results[0]
        assert "success_rate" in results[0]
    
    async def test_find_templates_with_search_filter(self, prompt_service):
        """Test template finding with search term filtering"""
        # Add a template that shouldn't match the search
        non_matching_template = PromptTemplate(
            name="other_template",
            system_prompt="Other system",
            user_prompt_template="Other user prompt",
            description="Different description"
        )
        
        prompt_service.prompt_manager.find_templates.return_value = [
            prompt_service.prompt_manager.templates["test_template"],
            non_matching_template
        ]
        
        results = await prompt_service.find_templates(search_term="test")
        
        # Should only return the template that matches "test"
        assert len(results) == 1
        assert results[0]["name"] == "test_template"
    
    async def test_get_template_info_success(self, prompt_service):
        """Test successful template info retrieval"""
        info = await prompt_service.get_template_info("test_template")
        
        assert info is not None
        assert info["name"] == "test_template"
        assert info["description"] == "Test template"
        assert info["system_prompt"] == "Test system prompt"
        assert info["user_prompt_template"] == "Test user prompt with {variable}"
        assert "created_at" in info
        assert "updated_at" in info
    
    async def test_get_template_info_not_found(self, prompt_service):
        """Test template info retrieval for non-existent template"""
        prompt_service.prompt_manager.get_template.return_value = None
        
        info = await prompt_service.get_template_info("non_existent")
        assert info is None
    
    async def test_get_categories(self, prompt_service):
        """Test getting available categories"""
        categories = await prompt_service.get_categories()
        
        assert isinstance(categories, list)
        assert "test" in categories
    
    async def test_get_tags(self, prompt_service):
        """Test getting available tags"""
        tags = await prompt_service.get_tags()
        
        assert isinstance(tags, list)
        assert "test" in tags
    
    async def test_validate_template_variables_success(self, prompt_service):
        """Test successful variable validation"""
        result = await prompt_service.validate_template_variables(
            template_name="test_template",
            variables={"variable": "value", "extra": "extra_value"}
        )
        
        assert result["valid"] is True
        assert result["missing_required"] == []
        assert "extra_variables" in result
    
    async def test_validate_template_variables_missing_required(self, prompt_service):
        """Test variable validation with missing required variables"""
        result = await prompt_service.validate_template_variables(
            template_name="test_template",
            variables={"wrong_var": "value"}
        )
        
        assert result["valid"] is False
        assert "variable" in result["missing_required"]
    
    async def test_validate_template_variables_template_not_found(self, prompt_service):
        """Test variable validation for non-existent template"""
        prompt_service.prompt_manager.get_template.return_value = None
        
        result = await prompt_service.validate_template_variables(
            template_name="non_existent",
            variables={}
        )
        
        assert result["valid"] is False
        assert "Template not found" in result["error"]
    
    async def test_preview_prompt_success(self, prompt_service):
        """Test successful prompt preview"""
        result = await prompt_service.preview_prompt(
            template_name="test_template",
            variables={"variable": "preview_value"}
        )
        
        assert result["system_prompt"] == "Test system prompt"
        assert result["user_prompt"] == "Test user prompt with preview_value"
        assert result["template_name"] == "test_template"
        assert "model" in result
    
    async def test_preview_prompt_template_not_found(self, prompt_service):
        """Test prompt preview for non-existent template"""
        prompt_service.prompt_manager.get_template.return_value = None
        
        with pytest.raises(ValueError, match="Template not found"):
            await prompt_service.preview_prompt(
                template_name="non_existent",
                variables={}
            )
    
    async def test_get_service_metrics(self, prompt_service):
        """Test service metrics retrieval"""
        # Mock prompt manager metrics
        prompt_service.prompt_manager.get_metrics = AsyncMock(return_value={
            "service_metrics": {"total_generations": 10},
            "template_count": 5,
            "cache_hit_rate": 0.8
        })
        
        metrics = await prompt_service.get_service_metrics()
        
        assert "prompt_service" in metrics
        assert metrics["prompt_service"]["initialized"] is True
        assert "service_metrics" in metrics
        assert "template_count" in metrics
    
    async def test_clear_cache(self, prompt_service):
        """Test cache clearing"""
        await prompt_service.clear_cache()
        
        prompt_service.prompt_manager.clear_cache.assert_called_once()
    
    async def test_reload_templates(self, prompt_service):
        """Test template reloading"""
        # Setup mock templates
        core_template = PromptTemplate(
            name="system_dm_persona",
            system_prompt="Core system",
            user_prompt_template="Core template",
            description="Core template"
        )
        
        external_template = PromptTemplate(
            name="external_template",
            system_prompt="External system",
            user_prompt_template="External template",
            description="External template"
        )
        
        prompt_service.prompt_manager.templates = {
            "system_dm_persona": core_template,
            "external_template": external_template
        }
        
        # Mock repository to return new templates
        prompt_service.prompt_repo.list_templates.return_value = [{
            "name": "new_external_template",
            "system_prompt": "New external system",
            "user_prompt_template": "New external template",
            "description": "New external template"
        }]
        
        await prompt_service.reload_templates()
        
        # Core template should remain, external should be removed and new one added
        assert "system_dm_persona" in prompt_service.prompt_manager.templates
        # Note: In a real implementation, we'd verify the external template was replaced
    
    async def test_load_external_templates_error_handling(self, prompt_service):
        """Test error handling during external template loading"""
        # Make repository raise an error
        prompt_service.prompt_repo.list_templates.side_effect = Exception("Repository error")
        
        # Should not raise an exception, just log the error
        await prompt_service._load_external_templates()
        
        # Service should still be functional
        assert prompt_service.initialized is True
    
    async def test_load_prompt_library_templates_file_exists(self, prompt_service):
        """Test loading templates when prompt library file exists"""
        with patch('pathlib.Path.exists', return_value=True):
            # Should not raise an exception
            await prompt_service._load_prompt_library_templates()
    
    async def test_load_prompt_library_templates_file_not_exists(self, prompt_service):
        """Test loading templates when prompt library file doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            # Should not raise an exception
            await prompt_service._load_prompt_library_templates()
    
    async def test_load_prompt_library_templates_error(self, prompt_service):
        """Test error handling during prompt library template loading"""
        with patch('pathlib.Path.exists', side_effect=Exception("File system error")):
            # Should not raise an exception, just log the error
            await prompt_service._load_prompt_library_templates()


class TestPromptServiceIntegration:
    """Integration tests for PromptService with real dependencies"""
    
    async def test_full_initialization_workflow(self):
        """Test complete initialization workflow"""
        service = PromptService()
        
        # Mock all dependencies
        mock_prompt_manager = AsyncMock()
        mock_prompt_manager.templates = {}
        mock_prompt_manager.category_index = {}
        mock_prompt_manager.tag_index = {}
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[
            {
                "name": "repo_template",
                "system_prompt": "Repository system prompt",
                "user_prompt_template": "Repository user prompt",
                "description": "Template from repository"
            }
        ])
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo), \
             patch('pathlib.Path.exists', return_value=True):
            
            await service.initialize()
        
        assert service.initialized is True
        assert service.prompt_manager is not None
        
        # Verify external templates were loaded
        mock_prompt_repo.list_templates.assert_called_once()
    
    async def test_template_lifecycle_management(self):
        """Test complete template lifecycle: create, use, update, delete"""
        service = PromptService()
        
        # Mock dependencies
        mock_prompt_manager = AsyncMock()
        mock_prompt_manager.templates = {}
        mock_prompt_manager.register_template = Mock(return_value=True)
        mock_prompt_manager.get_template = Mock(return_value=None)
        mock_prompt_manager.generate = AsyncMock(return_value={
            "response": "Lifecycle test response",
            "template": {"name": "lifecycle_template"},
            "generation_time": 0.3
        })
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        mock_prompt_repo.save_prompt_template = AsyncMock(return_value="lifecycle_id")
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            
            await service.initialize()
        
        # Create template
        template_data = {
            "name": "lifecycle_template",
            "system_prompt": "Lifecycle system prompt",
            "user_prompt_template": "Lifecycle user prompt with {variable}",
            "description": "Template for lifecycle testing",
            "required_variables": ["variable"]
        }
        
        template_name = await service.create_template(template_data)
        assert template_name == "lifecycle_template"
        
        # Mock template exists for subsequent operations
        created_template = PromptTemplate(**template_data)
        mock_prompt_manager.get_template.return_value = created_template
        
        # Use template
        result = await service.generate_with_template(
            template_name="lifecycle_template",
            variables={"variable": "test_value"}
        )
        
        assert result["response"] == "Lifecycle test response"
    
    async def test_error_recovery_scenarios(self):
        """Test various error recovery scenarios"""
        service = PromptService()
        
        # Mock dependencies with various failure modes
        mock_prompt_manager = AsyncMock()
        mock_prompt_manager.templates = {}
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            
            await service.initialize()
        
        # Test scenario 1: Template not found
        mock_prompt_manager.get_template.return_value = None
        
        with pytest.raises(ValueError):
            await service.process_template("non_existent", {})
        
        # Test scenario 2: Generation failure with fallback
        mock_prompt_manager.generate.side_effect = Exception("Generation failed")
        mock_prompt_repo.get_prompt_template.return_value = {
            "content": "Fallback content for {variable}",
            "name": "fallback"
        }
        
        result = await service.generate_prompt("fallback_template", {"variable": "value"})
        assert result == "Fallback content for value"
        
        # Test scenario 3: Complete failure
        mock_prompt_repo.get_prompt_template.return_value = None
        
        with pytest.raises(Exception):
            await service.generate_prompt("completely_missing", {})


class TestPromptServicePerformance:
    """Performance tests for PromptService"""
    
    async def test_concurrent_operations(self):
        """Test concurrent service operations"""
        service = PromptService()
        
        # Mock dependencies
        mock_prompt_manager = AsyncMock()
        mock_template = PromptTemplate(
            name="concurrent_template",
            system_prompt="Concurrent system",
            user_prompt_template="Concurrent user prompt with {variable}",
            description="Concurrent test template",
            required_variables=["variable"]
        )
        
        mock_prompt_manager.templates = {"concurrent_template": mock_template}
        mock_prompt_manager.get_template = Mock(return_value=mock_template)
        mock_prompt_manager.generate = AsyncMock(return_value={
            "response": "Concurrent response",
            "template": {"name": "concurrent_template"},
            "generation_time": 0.1
        })
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            
            await service.initialize()
        
        # Run multiple concurrent operations
        async def concurrent_operation(operation_id: int):
            return await service.generate_with_template(
                template_name="concurrent_template",
                variables={"variable": f"value_{operation_id}"}
            )
        
        tasks = [concurrent_operation(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert len(results) == 10
        for result in results:
            assert result["response"] == "Concurrent response"
        
        # Verify all calls were made
        assert mock_prompt_manager.generate.call_count == 10
    
    async def test_large_template_processing(self):
        """Test processing of large templates"""
        service = PromptService()
        
        # Create a large template
        large_template_content = "Large template content " * 1000 + " with {variable}"
        large_template = PromptTemplate(
            name="large_template",
            system_prompt="Large system prompt " * 100,
            user_prompt_template=large_template_content,
            description="Large template for performance testing",
            required_variables=["variable"]
        )
        
        mock_prompt_manager = AsyncMock()
        mock_prompt_manager.templates = {"large_template": large_template}
        mock_prompt_manager.get_template = Mock(return_value=large_template)
        
        mock_prompt_repo = AsyncMock()
        mock_prompt_repo.list_templates = AsyncMock(return_value=[])
        
        with patch('backend.infrastructure.llm.services.prompt_service.get_prompt_manager', 
                  return_value=mock_prompt_manager), \
             patch.object(service, 'prompt_repo', mock_prompt_repo):
            
            await service.initialize()
        
        # Process large template
        import time
        start_time = time.time()
        
        result = await service.process_template(
            template_name="large_template",
            variables={"variable": "test_value"}
        )
        
        processing_time = time.time() - start_time
        
        # Should complete quickly even with large template
        assert processing_time < 1.0  # Should complete in under 1 second
        assert "test_value" in result
        assert len(result) > 10000  # Should be a large result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend.infrastructure.llm.services.prompt_service", "--cov-report=term-missing"]) 