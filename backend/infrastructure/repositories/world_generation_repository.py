"""
World Generation Repository - Infrastructure Implementation

SQLAlchemy implementation of the world generation repository protocol.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session

from backend.systems.world_generation.models import (
    WorldGenerationRecord, GeneratedWorldData
)


class SQLAlchemyWorldGenerationRepository:
    """SQLAlchemy implementation of WorldGenerationRepository protocol"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_world_generation(self, record: WorldGenerationRecord) -> WorldGenerationRecord:
        """Save a world generation record"""
        # This would normally interact with SQLAlchemy models
        # For now, we'll store in memory as a placeholder
        if not hasattr(self, '_records'):
            self._records = {}
        
        self._records[record.id] = record
        return record
    
    def get_world_generation_by_id(self, world_id: UUID) -> Optional[WorldGenerationRecord]:
        """Get world generation record by ID"""
        if not hasattr(self, '_records'):
            self._records = {}
        
        return self._records.get(world_id)
    
    def list_world_generations(self, active_only: bool = False) -> List[WorldGenerationRecord]:
        """List world generation records"""
        if not hasattr(self, '_records'):
            self._records = {}
        
        records = list(self._records.values())
        
        if active_only:
            records = [r for r in records if r.simulation_active]
        
        # Sort by creation date, newest first
        records.sort(key=lambda r: r.created_at, reverse=True)
        
        return records
    
    def update_world_generation(self, record: WorldGenerationRecord) -> WorldGenerationRecord:
        """Update world generation record"""
        return self.save_world_generation(record)
    
    def delete_world_generation(self, world_id: UUID) -> bool:
        """Delete world generation record"""
        if not hasattr(self, '_records'):
            self._records = {}
        
        if world_id in self._records:
            del self._records[world_id]
            return True
        
        return False
    
    def find_worlds_by_template(self, template_name: str) -> List[WorldGenerationRecord]:
        """Find worlds created with specific template"""
        if not hasattr(self, '_records'):
            self._records = {}
        
        return [r for r in self._records.values() if r.template_used == template_name]
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get overall generation statistics"""
        if not hasattr(self, '_records'):
            self._records = {}
        
        records = list(self._records.values())
        
        if not records:
            return {
                'total_worlds': 0,
                'active_simulations': 0,
                'average_generation_time': 0.0,
                'most_used_template': None
            }
        
        active_count = sum(1 for r in records if r.simulation_active)
        avg_time = sum(r.generation_time for r in records) / len(records)
        
        # Find most used template
        template_counts = {}
        for r in records:
            if r.template_used:
                template_counts[r.template_used] = template_counts.get(r.template_used, 0) + 1
        
        most_used_template = max(template_counts.items(), key=lambda x: x[1])[0] if template_counts else None
        
        return {
            'total_worlds': len(records),
            'active_simulations': active_count,
            'average_generation_time': avg_time,
            'most_used_template': most_used_template,
            'template_usage': template_counts
        }


class SQLAlchemyWorldContentRepository:
    """SQLAlchemy implementation of WorldContentRepository protocol"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_world_content(self, world_id: UUID, content: GeneratedWorldData) -> GeneratedWorldData:
        """Save world content data"""
        # This would normally interact with SQLAlchemy models
        # For now, we'll store in memory as a placeholder
        if not hasattr(self, '_content'):
            self._content = {}
        
        self._content[world_id] = content
        return content
    
    def get_world_content(self, world_id: UUID) -> Optional[GeneratedWorldData]:
        """Get world content by ID"""
        if not hasattr(self, '_content'):
            self._content = {}
        
        return self._content.get(world_id)
    
    def update_world_content(self, world_id: UUID, content: GeneratedWorldData) -> GeneratedWorldData:
        """Update world content data"""
        return self.save_world_content(world_id, content)
    
    def delete_world_content(self, world_id: UUID) -> bool:
        """Delete world content data"""
        if not hasattr(self, '_content'):
            self._content = {}
        
        if world_id in self._content:
            del self._content[world_id]
            return True
        
        return False
    
    def get_regions_by_world(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get all regions for a world"""
        content = self.get_world_content(world_id)
        return content.regions if content else []
    
    def get_npcs_by_world(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get all NPCs for a world"""
        content = self.get_world_content(world_id)
        return content.npcs if content else []
    
    def get_factions_by_world(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get all factions for a world"""
        content = self.get_world_content(world_id)
        return content.factions if content else []
    
    def get_trade_routes_by_world(self, world_id: UUID) -> List[Dict[str, Any]]:
        """Get all trade routes for a world"""
        content = self.get_world_content(world_id)
        return content.trade_routes if content else [] 