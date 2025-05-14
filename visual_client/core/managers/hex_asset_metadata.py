"""
Metadata management for hex-based assets.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import sqlite3
from dataclasses import dataclass
from ..error_handler import handle_component_error, ErrorSeverity

@dataclass
class AssetMetadata:
    """Metadata for a single hex asset."""
    asset_id: str
    category: str
    subcategory: str
    name: str
    path: str
    dimensions: tuple[int, int]
    has_variations: bool
    variation_types: List[str]
    color_palette: List[str]
    memory_size: int
    tags: List[str]

class HexAssetMetadataManager:
    """Manages metadata for hex-based assets with search and filtering capabilities."""
    
    def __init__(self, db_path: str = "assets/metadata.db"):
        """Initialize the metadata manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        try:
            self.db_path = db_path
            self._init_database()
        except Exception as e:
            handle_component_error(
                "Failed to initialize metadata manager",
                e,
                ErrorSeverity.HIGH
            )
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    has_variations BOOLEAN NOT NULL,
                    memory_size INTEGER NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS variations (
                    asset_id TEXT,
                    variation_type TEXT,
                    FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
                    PRIMARY KEY(asset_id, variation_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS colors (
                    asset_id TEXT,
                    color_hex TEXT,
                    FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
                    PRIMARY KEY(asset_id, color_hex)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    asset_id TEXT,
                    tag TEXT,
                    FOREIGN KEY(asset_id) REFERENCES assets(asset_id),
                    PRIMARY KEY(asset_id, tag)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON assets(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_subcategory ON assets(subcategory)")
    
    def add_asset(self, metadata: AssetMetadata) -> bool:
        """Add or update asset metadata in the database.
        
        Args:
            metadata: Asset metadata to store
            
        Returns:
            bool: True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Insert/update main asset data
                conn.execute("""
                    INSERT OR REPLACE INTO assets
                    (asset_id, category, subcategory, name, path, width, height, 
                     has_variations, memory_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.asset_id, metadata.category, metadata.subcategory,
                    metadata.name, metadata.path, metadata.dimensions[0],
                    metadata.dimensions[1], metadata.has_variations,
                    metadata.memory_size
                ))
                
                # Clear existing related data
                conn.execute("DELETE FROM variations WHERE asset_id = ?", 
                           (metadata.asset_id,))
                conn.execute("DELETE FROM colors WHERE asset_id = ?",
                           (metadata.asset_id,))
                conn.execute("DELETE FROM tags WHERE asset_id = ?",
                           (metadata.asset_id,))
                
                # Insert variations
                for var_type in metadata.variation_types:
                    conn.execute("""
                        INSERT INTO variations (asset_id, variation_type)
                        VALUES (?, ?)
                    """, (metadata.asset_id, var_type))
                
                # Insert colors
                for color in metadata.color_palette:
                    conn.execute("""
                        INSERT INTO colors (asset_id, color_hex)
                        VALUES (?, ?)
                    """, (metadata.asset_id, color))
                
                # Insert tags
                for tag in metadata.tags:
                    conn.execute("""
                        INSERT INTO tags (asset_id, tag)
                        VALUES (?, ?)
                    """, (metadata.asset_id, tag))
                
            return True
        except Exception as e:
            handle_component_error(
                f"Failed to add metadata for asset {metadata.asset_id}",
                e,
                ErrorSeverity.MEDIUM
            )
            return False
    
    def search_assets(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        has_variations: Optional[bool] = None,
        name_contains: Optional[str] = None
    ) -> List[AssetMetadata]:
        """Search for assets based on various criteria.
        
        Args:
            category: Filter by asset category
            subcategory: Filter by asset subcategory
            tags: Filter by tags (all must match)
            has_variations: Filter by whether asset has variations
            name_contains: Filter by asset name containing text
            
        Returns:
            List of matching asset metadata
        """
        try:
            query = "SELECT DISTINCT a.* FROM assets a"
            params = []
            conditions = []
            
            if tags:
                query += f" JOIN tags t ON a.asset_id = t.asset_id"
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("t.tag = ?")
                    params.append(tag)
                conditions.append(
                    f"a.asset_id IN (SELECT asset_id FROM tags WHERE tag IN ({','.join('?' * len(tags))}) GROUP BY asset_id HAVING COUNT(DISTINCT tag) = {len(tags)})"
                )
            
            if category:
                conditions.append("a.category = ?")
                params.append(category)
            
            if subcategory:
                conditions.append("a.subcategory = ?")
                params.append(subcategory)
            
            if has_variations is not None:
                conditions.append("a.has_variations = ?")
                params.append(has_variations)
            
            if name_contains:
                conditions.append("a.name LIKE ?")
                params.append(f"%{name_contains}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    # Get variations
                    variations = [r[0] for r in conn.execute(
                        "SELECT variation_type FROM variations WHERE asset_id = ?",
                        (row[0],)
                    ).fetchall()]
                    
                    # Get colors
                    colors = [r[0] for r in conn.execute(
                        "SELECT color_hex FROM colors WHERE asset_id = ?",
                        (row[0],)
                    ).fetchall()]
                    
                    # Get tags
                    tags = [r[0] for r in conn.execute(
                        "SELECT tag FROM tags WHERE asset_id = ?",
                        (row[0],)
                    ).fetchall()]
                    
                    results.append(AssetMetadata(
                        asset_id=row[0],
                        category=row[1],
                        subcategory=row[2],
                        name=row[3],
                        path=row[4],
                        dimensions=(row[5], row[6]),
                        has_variations=bool(row[7]),
                        variation_types=variations,
                        color_palette=colors,
                        memory_size=row[8],
                        tags=tags
                    ))
                
                return results
                
        except Exception as e:
            handle_component_error(
                "Failed to search assets",
                e,
                ErrorSeverity.MEDIUM
            )
            return []
    
    def get_asset(self, asset_id: str) -> Optional[AssetMetadata]:
        """Get metadata for a specific asset.
        
        Args:
            asset_id: ID of the asset to retrieve
            
        Returns:
            Asset metadata if found, None otherwise
        """
        try:
            results = self.search_assets(name_contains=asset_id)
            return results[0] if results else None
        except Exception as e:
            handle_component_error(
                f"Failed to get metadata for asset {asset_id}",
                e,
                ErrorSeverity.LOW
            )
            return None
    
    def get_memory_usage(self, category: Optional[str] = None) -> int:
        """Get total memory usage of assets.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Total memory usage in bytes
        """
        try:
            query = "SELECT SUM(memory_size) FROM assets"
            params = []
            
            if category:
                query += " WHERE category = ?"
                params.append(category)
            
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute(query, params).fetchone()
                return result[0] or 0
        except Exception as e:
            handle_component_error(
                "Failed to get memory usage",
                e,
                ErrorSeverity.LOW
            )
            return 0
    
    def add_metadata(self, asset_id: str, metadata: dict) -> bool:
        """Add or update asset metadata from a dict (for test compatibility)."""
        # Convert dict to AssetMetadata
        meta = AssetMetadata(
            asset_id=asset_id,
            category=metadata.get('category', ''),
            subcategory=metadata.get('subcategory', ''),
            name=metadata.get('name', ''),
            path=metadata.get('path', ''),
            dimensions=tuple(metadata.get('dimensions', (64, 64))),
            has_variations=metadata.get('has_variations', False),
            variation_types=metadata.get('variation_types', []),
            color_palette=metadata.get('color_palette', []),
            memory_size=metadata.get('memory_size', 0),
            tags=metadata.get('tags', [])
        )
        return self.add_asset(meta)
    
    def search(self, filters: dict) -> list:
        """Search for assets using a dict of filters (for test compatibility)."""
        results = self.search_assets(
            category=filters.get('category'),
            subcategory=filters.get('subcategory'),
            tags=filters.get('tags'),
            has_variations=filters.get('has_variations'),
            name_contains=filters.get('name_contains')
        )
        # Convert AssetMetadata objects to dicts for test compatibility, with 'id' key
        return [dict(id=meta.asset_id, **meta.__dict__) for meta in results] 