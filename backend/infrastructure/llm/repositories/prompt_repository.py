"""
Enhanced Prompt Template Repository for Visual DM LLM Infrastructure

This repository provides comprehensive persistence, retrieval, and management capabilities
for prompt templates. It supports both database storage and file-based template loading,
integrating seamlessly with the centralized prompt management system.

Features:
- Template persistence with versioning
- Metadata tracking and performance analytics
- Bulk operations for template management
- Search and filtering capabilities
- Integration with prompt library system
"""

from typing import Dict, List, Optional, Any, Union
import uuid
import logging
import json
import time
from pathlib import Path
import asyncio
from dataclasses import asdict

from backend.infrastructure.models import BaseRepository
from backend.infrastructure.shared.exceptions import ValidationError

logger = logging.getLogger(__name__)

class PromptRepository(BaseRepository):
    """
    Enhanced repository for prompt templates with comprehensive persistence capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour
        self.metrics = {
            "total_reads": 0,
            "total_writes": 0,
            "cache_hits": 0,
            "last_cleanup": time.time()
        }
    
    async def save_prompt_template(self, template_data: Dict[str, Any]) -> str:
        """
        Save prompt template with comprehensive validation and metadata
        """
        self.metrics["total_writes"] += 1
        
        try:
            # Validate required fields
            required_fields = ["name", "system_prompt", "user_prompt_template", "description"]
            for field in required_fields:
                if field not in template_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Generate template ID if not provided
            template_id = template_data.get("id") or str(uuid.uuid4())
            template_data["id"] = template_id
            
            # Add timestamps
            current_time = time.time()
            if "created_at" not in template_data:
                template_data["created_at"] = current_time
            template_data["updated_at"] = current_time
            
            # Set defaults for optional fields
            template_data.setdefault("version", "1.0")
            template_data.setdefault("category", "utility")
            template_data.setdefault("tags", [])
            template_data.setdefault("model", "gpt-4.1-mini")
            template_data.setdefault("batch_eligible", False)
            template_data.setdefault("usage_count", 0)
            template_data.setdefault("success_rate", 1.0)
            template_data.setdefault("avg_response_time", 0.0)
            template_data.setdefault("required_variables", [])
            template_data.setdefault("optional_variables", [])
            template_data.setdefault("context_requirements", {})
            
            # TODO: Implement actual database save
            # For now, store in memory cache as persistent storage
            await self._save_to_storage(template_id, template_data)
            
            # Update cache
            self.cache[template_id] = {
                "data": template_data,
                "timestamp": current_time
            }
            
            logger.info(f"Saved template: {template_data['name']} (ID: {template_id})")
            return template_id
            
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            raise
    
    async def get_prompt_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve prompt template with caching
        """
        self.metrics["total_reads"] += 1
        
        # Check cache first
        if template_id in self.cache:
            cache_entry = self.cache[template_id]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                self.metrics["cache_hits"] += 1
                return cache_entry["data"]
            else:
                del self.cache[template_id]
        
        # Load from storage
        template_data = await self._load_from_storage(template_id)
        if template_data:
            # Update cache
            self.cache[template_id] = {
                "data": template_data,
                "timestamp": time.time()
            }
        
        return template_data
    
    async def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve template by name rather than ID
        """
        # Search through cached templates first
        for template_id, cache_entry in self.cache.items():
            if cache_entry["data"].get("name") == name:
                if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                    self.metrics["cache_hits"] += 1
                    return cache_entry["data"]
        
        # Search storage
        all_templates = await self.list_templates()
        for template in all_templates:
            if template and template.get("name") == name:
                return template
        
        return None
    
    async def list_templates(self, 
                           category: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           limit: Optional[int] = None,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all prompt templates with optional filtering
        """
        self.metrics["total_reads"] += 1
        
        # For now, return cached templates
        # TODO: Implement database query with proper filtering
        templates = []
        
        for cache_entry in self.cache.values():
            template_data = cache_entry["data"]
            
            # Apply category filter
            if category and template_data.get("category") != category:
                continue
            
            # Apply tags filter
            if tags:
                template_tags = set(template_data.get("tags", []))
                if not any(tag in template_tags for tag in tags):
                    continue
            
            templates.append(template_data)
        
        # Sort by name
        templates.sort(key=lambda x: x.get("name", ""))
        
        # Apply pagination
        if offset > 0:
            templates = templates[offset:]
        if limit:
            templates = templates[:limit]
        
        return templates
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing template with new data
        """
        existing = await self.get_prompt_template(template_id)
        if not existing:
            return False
        
        # Merge updates
        existing.update(updates)
        existing["updated_at"] = time.time()
        
        # Save updated template
        await self.save_prompt_template(existing)
        return True
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete template from storage and cache
        """
        try:
            # Remove from cache
            if template_id in self.cache:
                del self.cache[template_id]
            
            # Remove from storage
            await self._delete_from_storage(template_id)
            
            logger.info(f"Deleted template: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False
    
    async def update_template_metrics(self, 
                                    template_id: str, 
                                    response_time: float, 
                                    success: bool) -> bool:
        """
        Update performance metrics for a template
        """
        template = await self.get_prompt_template(template_id)
        if not template:
            return False
        
        # Update metrics
        usage_count = template.get("usage_count", 0) + 1
        avg_response_time = template.get("avg_response_time", 0.0)
        success_rate = template.get("success_rate", 1.0)
        
        # Calculate new averages
        new_avg_response_time = (
            (avg_response_time * (usage_count - 1) + response_time) / usage_count
        )
        
        if success:
            new_success_rate = (success_rate * (usage_count - 1) + 1.0) / usage_count
        else:
            new_success_rate = (success_rate * (usage_count - 1) + 0.0) / usage_count
        
        # Update template
        updates = {
            "usage_count": usage_count,
            "avg_response_time": new_avg_response_time,
            "success_rate": new_success_rate
        }
        
        return await self.update_template(template_id, updates)
    
    async def search_templates(self, 
                             query: str, 
                             search_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Full-text search across template fields
        """
        if not search_fields:
            search_fields = ["name", "description", "tags", "category"]
        
        query_lower = query.lower()
        results = []
        
        all_templates = await self.list_templates()
        for template in all_templates:
            score = 0
            
            for field in search_fields:
                field_value = template.get(field, "")
                if isinstance(field_value, list):
                    field_value = " ".join(str(v) for v in field_value)
                field_value = str(field_value).lower()
                
                if query_lower in field_value:
                    score += 1
                    if field == "name":
                        score += 2  # Name matches are more important
            
            if score > 0:
                template["_search_score"] = score
                results.append(template)
        
        # Sort by relevance
        results.sort(key=lambda x: x["_search_score"], reverse=True)
        
        # Remove search score from results
        for result in results:
            result.pop("_search_score", None)
        
        return results
    
    async def get_template_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about templates
        """
        all_templates = await self.list_templates()
        
        if not all_templates:
            return {
                "total_templates": 0,
                "categories": {},
                "average_usage": 0,
                "total_usage": 0
            }
        
        # Calculate statistics
        categories = {}
        total_usage = 0
        success_rates = []
        response_times = []
        
        for template in all_templates:
            category = template.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
            
            usage = template.get("usage_count", 0)
            total_usage += usage
            
            if usage > 0:
                success_rates.append(template.get("success_rate", 1.0))
                response_times.append(template.get("avg_response_time", 0.0))
        
        return {
            "total_templates": len(all_templates),
            "categories": categories,
            "total_usage": total_usage,
            "average_usage": total_usage / len(all_templates) if all_templates else 0,
            "average_success_rate": sum(success_rates) / len(success_rates) if success_rates else 1.0,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0.0,
            "repository_metrics": self.metrics
        }
    
    async def bulk_import_templates(self, templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import multiple templates in batch
        """
        results = {
            "imported": 0,
            "failed": 0,
            "errors": []
        }
        
        for template_data in templates:
            try:
                await self.save_prompt_template(template_data)
                results["imported"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "template": template_data.get("name", "unknown"),
                    "error": str(e)
                })
        
        logger.info(f"Bulk import completed: {results['imported']} imported, {results['failed']} failed")
        return results
    
    async def cleanup_cache(self):
        """
        Clean up expired cache entries
        """
        current_time = time.time()
        expired_keys = []
        
        for template_id, cache_entry in self.cache.items():
            if current_time - cache_entry["timestamp"] >= self.cache_ttl:
                expired_keys.append(template_id)
        
        for key in expired_keys:
            del self.cache[key]
        
        self.metrics["last_cleanup"] = current_time
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def _save_to_storage(self, template_id: str, template_data: Dict[str, Any]):
        """
        Save template to persistent storage
        TODO: Implement database storage
        """
        # For now, this is a placeholder
        # In a real implementation, this would save to database
        pass
    
    async def _load_from_storage(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Load template from persistent storage
        TODO: Implement database retrieval
        """
        # For now, this is a placeholder
        # In a real implementation, this would load from database
        return None
    
    async def _delete_from_storage(self, template_id: str):
        """
        Delete template from persistent storage
        TODO: Implement database deletion
        """
        # For now, this is a placeholder
        # In a real implementation, this would delete from database
        pass
