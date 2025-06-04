"""
Simple Equipment Instance Repository Implementation

Provides data persistence for equipment instances using SQLite database
with focus on simplicity and avoiding complex dependency injection patterns.
Now with performance optimizations: caching, indexing, and query optimization.
"""

import sqlite3
import json
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
from uuid import UUID, uuid4
from dataclasses import asdict
from functools import lru_cache
import time

from backend.systems.equipment.services.business_logic_service import (
    EquipmentInstanceData, EquipmentSlot
)


class EquipmentInstanceRepositorySimple:
    """
    Simple equipment instance repository with performance optimizations.
    
    Features:
    - SQLite database with optimized indexes
    - In-memory caching for frequently accessed data
    - Query optimization and batching
    - Character equipment caching
    - Template-based caching
    """
    
    def __init__(self, db_path: str = "equipment_instances.db"):
        self.db_path = db_path
        self._connection_cache = {}
        self._thread_local = threading.local()
        
        # Performance caches
        self._character_equipment_cache: Dict[UUID, List[EquipmentInstanceData]] = {}
        self._equipment_cache: Dict[UUID, EquipmentInstanceData] = {}
        self._template_cache: Dict[str, List[EquipmentInstanceData]] = {}
        self._slot_cache: Dict[EquipmentSlot, List[EquipmentInstanceData]] = {}
        
        # Cache metadata
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = 300  # 5 minutes TTL for cached data
        
        # Performance tracking
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        self._init_database()
        self._create_indexes()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-safe database connection with optimizations."""
        if not hasattr(self._thread_local, 'connection'):
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            
            # Performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            conn.execute("PRAGMA synchronous=NORMAL")  # Balanced safety/performance
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
            
            self._thread_local.connection = conn
        
        return self._thread_local.connection
    
    def _init_database(self):
        """Initialize database with optimized schema."""
        conn = self._get_connection()
        
        # Create equipment instances table with performance optimizations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment_instances (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                slot TEXT NOT NULL,
                current_durability INTEGER NOT NULL,
                max_durability INTEGER NOT NULL,
                usage_count INTEGER DEFAULT 0,
                quality_tier TEXT NOT NULL,
                rarity_tier TEXT NOT NULL,
                is_equipped BOOLEAN DEFAULT FALSE,
                equipment_set TEXT,
                enchantments TEXT,  -- JSON
                effective_stats TEXT,  -- JSON
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
    
    def _create_indexes(self):
        """Create optimized indexes for common query patterns."""
        conn = self._get_connection()
        
        indexes = [
            # Character-based queries (most common)
            "CREATE INDEX IF NOT EXISTS idx_character_id ON equipment_instances(character_id)",
            "CREATE INDEX IF NOT EXISTS idx_character_equipped ON equipment_instances(character_id, is_equipped)",
            "CREATE INDEX IF NOT EXISTS idx_character_slot ON equipment_instances(character_id, slot)",
            
            # Template-based queries
            "CREATE INDEX IF NOT EXISTS idx_template_id ON equipment_instances(template_id)",
            "CREATE INDEX IF NOT EXISTS idx_template_quality ON equipment_instances(template_id, quality_tier)",
            
            # Equipment set queries
            "CREATE INDEX IF NOT EXISTS idx_equipment_set ON equipment_instances(equipment_set) WHERE equipment_set IS NOT NULL",
            
            # Multi-column indexes for complex queries
            "CREATE INDEX IF NOT EXISTS idx_character_template ON equipment_instances(character_id, template_id)",
            "CREATE INDEX IF NOT EXISTS idx_quality_rarity ON equipment_instances(quality_tier, rarity_tier)",
            
            # Time-based queries for maintenance
            "CREATE INDEX IF NOT EXISTS idx_updated_at ON equipment_instances(updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON equipment_instances(created_at)",
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except sqlite3.Error as e:
                print(f"Index creation warning: {e}")
        
        conn.commit()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache_timestamps:
            return False
        
        return (time.time() - self._cache_timestamps[cache_key]) < self._cache_ttl
    
    def _set_cache_timestamp(self, cache_key: str):
        """Update cache timestamp."""
        self._cache_timestamps[cache_key] = time.time()
    
    def _invalidate_character_cache(self, character_id: UUID):
        """Invalidate all caches related to a character."""
        cache_key = f"character_{character_id}"
        
        # Remove from character equipment cache
        if character_id in self._character_equipment_cache:
            del self._character_equipment_cache[character_id]
        
        # Remove from cache timestamps
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]
        
        # Clear individual equipment cache for this character's items
        to_remove = []
        for equipment_id, equipment in self._equipment_cache.items():
            if equipment.character_id == character_id:
                to_remove.append(equipment_id)
        
        for equipment_id in to_remove:
            del self._equipment_cache[equipment_id]
    
    def _invalidate_template_cache(self, template_id: str):
        """Invalidate template-based caches."""
        if template_id in self._template_cache:
            del self._template_cache[template_id]
            
        cache_key = f"template_{template_id}"
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]
    
    def create_equipment(self, equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create new equipment instance with cache invalidation."""
        conn = self._get_connection()
        self._query_count += 1
        
        # Serialize complex fields
        enchantments_json = json.dumps([asdict(ench) for ench in equipment_data.enchantments])
        effective_stats_json = json.dumps(equipment_data.effective_stats)
        
        conn.execute("""
            INSERT INTO equipment_instances (
                id, character_id, template_id, slot, current_durability, max_durability,
                usage_count, quality_tier, rarity_tier, is_equipped, equipment_set,
                enchantments, effective_stats, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(equipment_data.id),
            str(equipment_data.character_id),
            equipment_data.template_id,
            equipment_data.slot.value,
            equipment_data.current_durability,
            equipment_data.max_durability,
            equipment_data.usage_count,
            equipment_data.quality_tier,
            equipment_data.rarity_tier,
            equipment_data.is_equipped,
            equipment_data.equipment_set,
            enchantments_json,
            effective_stats_json,
            equipment_data.created_at.isoformat(),
            equipment_data.updated_at.isoformat()
        ))
        
        conn.commit()
        
        # Invalidate relevant caches
        self._invalidate_character_cache(equipment_data.character_id)
        self._invalidate_template_cache(equipment_data.template_id)
        
        # Add to individual equipment cache
        self._equipment_cache[equipment_data.id] = equipment_data
        
        return equipment_data
    
    def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentInstanceData]:
        """Get equipment by ID with caching."""
        # Check cache first
        if equipment_id in self._equipment_cache:
            self._cache_hits += 1
            return self._equipment_cache[equipment_id]
        
        self._cache_misses += 1
        self._query_count += 1
        
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM equipment_instances WHERE id = ?",
            (str(equipment_id),)
        )
        
        row = cursor.fetchone()
        if not row:
            return None
        
        equipment_data = self._row_to_equipment_data(row)
        
        # Cache the result
        self._equipment_cache[equipment_id] = equipment_data
        
        return equipment_data
    
    def get_character_equipment(self, character_id: UUID, equipped_only: bool = False) -> List[EquipmentInstanceData]:
        """Get character equipment with caching."""
        cache_key = f"character_{character_id}{'_equipped' if equipped_only else ''}"
        
        # Check cache first
        if (character_id in self._character_equipment_cache and 
            self._is_cache_valid(cache_key) and 
            not equipped_only):  # For simplicity, only cache full equipment lists
            self._cache_hits += 1
            equipment_list = self._character_equipment_cache[character_id]
            if equipped_only:
                return [eq for eq in equipment_list if eq.is_equipped]
            return equipment_list
        
        self._cache_misses += 1
        self._query_count += 1
        
        conn = self._get_connection()
        
        if equipped_only:
            cursor = conn.execute("""
                SELECT * FROM equipment_instances 
                WHERE character_id = ? AND is_equipped = TRUE
                ORDER BY slot
            """, (str(character_id),))
        else:
            cursor = conn.execute("""
                SELECT * FROM equipment_instances 
                WHERE character_id = ?
                ORDER BY is_equipped DESC, slot, created_at
            """, (str(character_id),))
        
        rows = cursor.fetchall()
        equipment_list = [self._row_to_equipment_data(row) for row in rows]
        
        # Cache the full equipment list
        if not equipped_only:
            self._character_equipment_cache[character_id] = equipment_list
            self._set_cache_timestamp(cache_key)
        
        return equipment_list
    
    def get_equipment_by_template(self, template_id: str) -> List[EquipmentInstanceData]:
        """Get all equipment instances of a specific template with caching."""
        cache_key = f"template_{template_id}"
        
        # Check cache first
        if template_id in self._template_cache and self._is_cache_valid(cache_key):
            self._cache_hits += 1
            return self._template_cache[template_id]
        
        self._cache_misses += 1
        self._query_count += 1
        
        conn = self._get_connection()
        cursor = conn.execute("""
            SELECT * FROM equipment_instances 
            WHERE template_id = ?
            ORDER BY character_id, created_at
        """, (template_id,))
        
        rows = cursor.fetchall()
        equipment_list = [self._row_to_equipment_data(row) for row in rows]
        
        # Cache the results
        self._template_cache[template_id] = equipment_list
        self._set_cache_timestamp(cache_key)
        
        return equipment_list
    
    def list_equipment(self, character_id: UUID = None, slot: EquipmentSlot = None, 
                      equipment_set: str = None, quality_tier: str = None,
                      rarity_tier: str = None, limit: int = 100, offset: int = 0) -> List[EquipmentInstanceData]:
        """List equipment with filters and pagination, optimized queries."""
        self._query_count += 1
        
        # Build optimized query based on available indexes
        base_query = "SELECT * FROM equipment_instances"
        conditions = []
        params = []
        
        # Use indexed columns first for better performance
        if character_id:
            conditions.append("character_id = ?")
            params.append(str(character_id))
        
        if slot:
            conditions.append("slot = ?")
            params.append(slot.value)
        
        if quality_tier:
            conditions.append("quality_tier = ?")
            params.append(quality_tier)
        
        if rarity_tier:
            conditions.append("rarity_tier = ?")
            params.append(rarity_tier)
        
        if equipment_set:
            conditions.append("equipment_set = ?")
            params.append(equipment_set)
        
        # Build final query
        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else:
            query = base_query
        
        # Add ordering and pagination
        query += " ORDER BY character_id, is_equipped DESC, slot, created_at"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        conn = self._get_connection()
        cursor = conn.execute(query, params)
        
        rows = cursor.fetchall()
        return [self._row_to_equipment_data(row) for row in rows]
    
    def update_equipment(self, equipment_id: UUID, updates: Dict[str, Any]) -> Optional[EquipmentInstanceData]:
        """Update equipment with optimized cache invalidation."""
        # Get current equipment to determine what caches to invalidate
        current_equipment = self.get_equipment_by_id(equipment_id)
        if not current_equipment:
            return None
        
        self._query_count += 1
        
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field == "enchantments":
                set_clauses.append("enchantments = ?")
                params.append(json.dumps([asdict(ench) for ench in value]))
            elif field == "effective_stats":
                set_clauses.append("effective_stats = ?")
                params.append(json.dumps(value))
            elif field in ["current_durability", "usage_count", "is_equipped"]:
                set_clauses.append(f"{field} = ?")
                params.append(value)
        
        if not set_clauses:
            return current_equipment
        
        # Always update timestamp
        set_clauses.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(str(equipment_id))
        
        conn = self._get_connection()
        conn.execute(f"""
            UPDATE equipment_instances 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """, params)
        
        conn.commit()
        
        # Invalidate relevant caches
        self._invalidate_character_cache(current_equipment.character_id)
        if equipment_id in self._equipment_cache:
            del self._equipment_cache[equipment_id]
        
        # Return updated equipment
        return self.get_equipment_by_id(equipment_id)
    
    def delete_equipment(self, equipment_id: UUID) -> bool:
        """Delete equipment with cache cleanup."""
        # Get equipment info before deletion for cache invalidation
        equipment = self.get_equipment_by_id(equipment_id)
        if not equipment:
            return False
        
        self._query_count += 1
        
        conn = self._get_connection()
        cursor = conn.execute("DELETE FROM equipment_instances WHERE id = ?", (str(equipment_id),))
        conn.commit()
        
        success = cursor.rowcount > 0
        
        if success:
            # Invalidate relevant caches
            self._invalidate_character_cache(equipment.character_id)
            self._invalidate_template_cache(equipment.template_id)
            
            if equipment_id in self._equipment_cache:
                del self._equipment_cache[equipment_id]
        
        return success
    
    def get_equipped_items(self, character_id: UUID) -> List[EquipmentInstanceData]:
        """Get only equipped items with caching."""
        return self.get_character_equipment(character_id, equipped_only=True)
    
    def get_equipment_by_slot(self, character_id: UUID, slot: EquipmentSlot) -> Optional[EquipmentInstanceData]:
        """Get equipped item in specific slot with optimized query."""
        self._query_count += 1
        
        conn = self._get_connection()
        cursor = conn.execute("""
            SELECT * FROM equipment_instances 
            WHERE character_id = ? AND slot = ? AND is_equipped = TRUE
            LIMIT 1
        """, (str(character_id), slot.value))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        equipment_data = self._row_to_equipment_data(row)
        
        # Cache the individual item
        self._equipment_cache[equipment_data.id] = equipment_data
        
        return equipment_data
    
    def count_character_equipment(self, character_id: UUID) -> int:
        """Get count of character equipment efficiently."""
        self._query_count += 1
        
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) FROM equipment_instances WHERE character_id = ?",
            (str(character_id),)
        )
        
        return cursor.fetchone()[0]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get repository performance statistics."""
        cache_hit_rate = (self._cache_hits / (self._cache_hits + self._cache_misses)) * 100 if (self._cache_hits + self._cache_misses) > 0 else 0
        
        return {
            "query_count": self._query_count,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cached_characters": len(self._character_equipment_cache),
            "cached_equipment": len(self._equipment_cache),
            "cached_templates": len(self._template_cache),
            "cache_size_kb": round(
                (len(str(self._character_equipment_cache)) + 
                 len(str(self._equipment_cache)) + 
                 len(str(self._template_cache))) / 1024, 2
            )
        }
    
    def clear_cache(self):
        """Clear all performance caches."""
        self._character_equipment_cache.clear()
        self._equipment_cache.clear()
        self._template_cache.clear()
        self._slot_cache.clear()
        self._cache_timestamps.clear()
        
        print("Equipment repository cache cleared")
    
    def _row_to_equipment_data(self, row) -> EquipmentInstanceData:
        """Convert database row to EquipmentInstanceData with error handling."""
        try:
            # Parse JSON fields safely
            enchantments_data = json.loads(row['enchantments']) if row['enchantments'] else []
            effective_stats = json.loads(row['effective_stats']) if row['effective_stats'] else {}
            
            # Convert enchantments data back to proper objects
            # Note: This is simplified - in a real system you'd reconstruct proper enchantment objects
            from backend.systems.equipment.services.business_logic_service import EnchantmentEffect
            enchantments = []
            for ench_data in enchantments_data:
                enchantments.append(EnchantmentEffect(
                    enchantment_type=ench_data.get('enchantment_type', 'unknown'),
                    magnitude=ench_data.get('magnitude', 0),
                    target_attribute=ench_data.get('target_attribute', 'unknown'),
                    is_active=ench_data.get('is_active', True)
                ))
            
            return EquipmentInstanceData(
                id=UUID(row['id']),
                character_id=UUID(row['character_id']),
                template_id=row['template_id'],
                slot=EquipmentSlot(row['slot']),
                current_durability=row['current_durability'],
                max_durability=row['max_durability'],
                usage_count=row['usage_count'],
                quality_tier=row['quality_tier'],
                rarity_tier=row['rarity_tier'],
                is_equipped=bool(row['is_equipped']),
                equipment_set=row['equipment_set'],
                enchantments=enchantments,
                effective_stats=effective_stats,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
        except Exception as e:
            print(f"Error converting row to equipment data: {e}")
            raise 