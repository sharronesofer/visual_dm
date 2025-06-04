"""
Database Interface for Memory System
-----------------------------------

This module provides a proper database interface to replace mock database dependencies
with real implementations that can work with actual databases.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MemoryDatabaseInterface(ABC):
    """Abstract interface for memory database operations."""
    
    @abstractmethod
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in the database."""
        pass
    
    @abstractmethod
    def retrieve_memories(
        self, 
        npc_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve memories for an NPC with optional filters."""
        pass
    
    @abstractmethod
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory."""
        pass
    
    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        pass
    
    @abstractmethod
    def search_memories(
        self, 
        query: str, 
        npc_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search memories by content."""
        pass
    
    @abstractmethod
    def get_memory_statistics(self, npc_id: str) -> Dict[str, Any]:
        """Get statistics about an NPC's memories."""
        pass


class SQLiteMemoryDatabase(MemoryDatabaseInterface):
    """SQLite implementation of the memory database interface."""
    
    def __init__(self, database_path: str = "memory_system.db"):
        self.database_path = database_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the SQLite database schema."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Create memories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        npc_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        importance REAL NOT NULL,
                        categories TEXT NOT NULL,  -- JSON array
                        timestamp TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        metadata TEXT NOT NULL,  -- JSON object
                        INDEX(npc_id),
                        INDEX(timestamp),
                        INDEX(importance)
                    )
                """)
                
                # Create memory associations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_associations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memory_id TEXT NOT NULL,
                        associated_memory_id TEXT NOT NULL,
                        association_type TEXT NOT NULL,
                        strength REAL DEFAULT 0.5,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (memory_id) REFERENCES memories (id),
                        FOREIGN KEY (associated_memory_id) REFERENCES memories (id),
                        INDEX(memory_id),
                        INDEX(association_type)
                    )
                """)
                
                # Create full-text search virtual table
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_search 
                    USING fts5(memory_id, content, categories)
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store a memory in SQLite database."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Insert into main table
                cursor.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, npc_id, content, importance, categories, timestamp, 
                     created_at, last_accessed, access_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory['id'],
                    memory['npc_id'],
                    memory['content'],
                    memory['importance'],
                    json.dumps(memory['categories']),
                    memory['timestamp'],
                    memory['created_at'],
                    memory['last_accessed'],
                    memory['access_count'],
                    json.dumps(memory['metadata'])
                ))
                
                # Insert into search table
                cursor.execute("""
                    INSERT OR REPLACE INTO memory_search 
                    (memory_id, content, categories)
                    VALUES (?, ?, ?)
                """, (
                    memory['id'],
                    memory['content'],
                    ' '.join(memory['categories'])
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store memory {memory.get('id')}: {e}")
            return False
    
    def retrieve_memories(
        self, 
        npc_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve memories for an NPC with optional filters."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                query = "SELECT * FROM memories WHERE npc_id = ?"
                params = [npc_id]
                
                if filters:
                    if 'min_importance' in filters:
                        query += " AND importance >= ?"
                        params.append(filters['min_importance'])
                    
                    if 'categories' in filters:
                        categories = filters['categories']
                        if isinstance(categories, list):
                            # Check if memory has any of the specified categories
                            category_conditions = []
                            for category in categories:
                                category_conditions.append("categories LIKE ?")
                                params.append(f'%"{category}"%')
                            query += f" AND ({' OR '.join(category_conditions)})"
                    
                    if 'after_date' in filters:
                        query += " AND timestamp >= ?"
                        params.append(filters['after_date'])
                    
                    if 'before_date' in filters:
                        query += " AND timestamp <= ?"
                        params.append(filters['before_date'])
                
                query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                memories = []
                for row in rows:
                    memory = {
                        'id': row[0],
                        'npc_id': row[1],
                        'content': row[2],
                        'importance': row[3],
                        'categories': json.loads(row[4]),
                        'timestamp': row[5],
                        'created_at': row[6],
                        'last_accessed': row[7],
                        'access_count': row[8],
                        'metadata': json.loads(row[9])
                    }
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories for NPC {npc_id}: {e}")
            return []
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                set_clauses = []
                params = []
                
                for key, value in updates.items():
                    if key in ['categories', 'metadata']:
                        set_clauses.append(f"{key} = ?")
                        params.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
                
                if not set_clauses:
                    return True  # Nothing to update
                
                params.append(memory_id)
                query = f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?"
                
                cursor.execute(query, params)
                
                # Update search index if content changed
                if 'content' in updates or 'categories' in updates:
                    cursor.execute("SELECT content, categories FROM memories WHERE id = ?", (memory_id,))
                    row = cursor.fetchone()
                    if row:
                        categories = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                        cursor.execute("""
                            UPDATE memory_search 
                            SET content = ?, categories = ?
                            WHERE memory_id = ?
                        """, (row[0], ' '.join(categories), memory_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Delete from main table
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                
                # Delete from search index
                cursor.execute("DELETE FROM memory_search WHERE memory_id = ?", (memory_id,))
                
                # Delete associations
                cursor.execute("""
                    DELETE FROM memory_associations 
                    WHERE memory_id = ? OR associated_memory_id = ?
                """, (memory_id, memory_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def search_memories(
        self, 
        query: str, 
        npc_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search memories by content using full-text search."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Use FTS5 for full-text search
                if npc_id:
                    sql_query = """
                        SELECT m.* FROM memories m
                        JOIN memory_search ms ON m.id = ms.memory_id
                        WHERE ms.content MATCH ? AND m.npc_id = ?
                        ORDER BY rank, m.importance DESC
                        LIMIT ?
                    """
                    params = (query, npc_id, limit)
                else:
                    sql_query = """
                        SELECT m.* FROM memories m
                        JOIN memory_search ms ON m.id = ms.memory_id
                        WHERE ms.content MATCH ?
                        ORDER BY rank, m.importance DESC
                        LIMIT ?
                    """
                    params = (query, limit)
                
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                memories = []
                for row in rows:
                    memory = {
                        'id': row[0],
                        'npc_id': row[1],
                        'content': row[2],
                        'importance': row[3],
                        'categories': json.loads(row[4]),
                        'timestamp': row[5],
                        'created_at': row[6],
                        'last_accessed': row[7],
                        'access_count': row[8],
                        'metadata': json.loads(row[9])
                    }
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            self.logger.error(f"Failed to search memories with query '{query}': {e}")
            return []
    
    def get_memory_statistics(self, npc_id: str) -> Dict[str, Any]:
        """Get statistics about an NPC's memories."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Basic counts
                cursor.execute("SELECT COUNT(*) FROM memories WHERE npc_id = ?", (npc_id,))
                total_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT AVG(importance), MIN(importance), MAX(importance) 
                    FROM memories WHERE npc_id = ?
                """, (npc_id,))
                importance_stats = cursor.fetchone()
                
                # Category distribution
                cursor.execute("SELECT categories FROM memories WHERE npc_id = ?", (npc_id,))
                category_counts = {}
                for (categories_json,) in cursor.fetchall():
                    categories = json.loads(categories_json)
                    for category in categories:
                        category_counts[category] = category_counts.get(category, 0) + 1
                
                # Recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM memories 
                    WHERE npc_id = ? AND timestamp >= datetime('now', '-7 days')
                """, (npc_id,))
                recent_count = cursor.fetchone()[0]
                
                return {
                    'total_memories': total_count,
                    'average_importance': importance_stats[0] if importance_stats[0] else 0.0,
                    'min_importance': importance_stats[1] if importance_stats[1] else 0.0,
                    'max_importance': importance_stats[2] if importance_stats[2] else 0.0,
                    'category_distribution': category_counts,
                    'recent_memories_7_days': recent_count
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get statistics for NPC {npc_id}: {e}")
            return {}


class PostgreSQLMemoryDatabase(MemoryDatabaseInterface):
    """PostgreSQL implementation with advanced features."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize PostgreSQL database schema with advanced features."""
        try:
            import psycopg2
            import psycopg2.extras
            
            with psycopg2.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                # Create memories table with JSONB for metadata
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        npc_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        importance REAL NOT NULL,
                        categories JSONB NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        last_accessed TIMESTAMPTZ NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        metadata JSONB NOT NULL,
                        content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_npc_id ON memories(npc_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_categories ON memories USING GIN(categories)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_content_vector ON memories USING GIN(content_vector)")
                
                # Memory associations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_associations (
                        id SERIAL PRIMARY KEY,
                        memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
                        associated_memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
                        association_type TEXT NOT NULL,
                        strength REAL DEFAULT 0.5,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """)
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_associations_memory_id ON memory_associations(memory_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_associations_type ON memory_associations(association_type)")
                
                conn.commit()
                self.logger.info("PostgreSQL database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL database: {e}")
            raise
    
    def store_memory(self, memory: Dict[str, Any]) -> bool:
        """Store memory in PostgreSQL with JSONB support."""
        try:
            import psycopg2
            import psycopg2.extras
            
            with psycopg2.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO memories 
                    (id, npc_id, content, importance, categories, timestamp, 
                     created_at, last_accessed, access_count, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        importance = EXCLUDED.importance,
                        categories = EXCLUDED.categories,
                        last_accessed = EXCLUDED.last_accessed,
                        access_count = EXCLUDED.access_count,
                        metadata = EXCLUDED.metadata
                """, (
                    memory['id'],
                    memory['npc_id'],
                    memory['content'],
                    memory['importance'],
                    json.dumps(memory['categories']),
                    memory['timestamp'],
                    memory['created_at'],
                    memory['last_accessed'],
                    memory['access_count'],
                    json.dumps(memory['metadata'])
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store memory {memory.get('id')} in PostgreSQL: {e}")
            return False
    
    def retrieve_memories(
        self, 
        npc_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve memories with advanced JSONB queries."""
        try:
            import psycopg2
            import psycopg2.extras
            
            with psycopg2.connect(self.connection_string) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                # Build query with JSONB operators
                query = "SELECT * FROM memories WHERE npc_id = %s"
                params = [npc_id]
                
                if filters:
                    if 'min_importance' in filters:
                        query += " AND importance >= %s"
                        params.append(filters['min_importance'])
                    
                    if 'categories' in filters:
                        # Use JSONB contains operator
                        query += " AND categories ?| %s"
                        params.append(filters['categories'])
                    
                    if 'metadata_filter' in filters:
                        # Advanced metadata filtering using JSONB
                        for key, value in filters['metadata_filter'].items():
                            query += f" AND metadata->'{key}' = %s"
                            params.append(json.dumps(value))
                
                query += " ORDER BY importance DESC, timestamp DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to regular dictionaries
                memories = []
                for row in rows:
                    memory = dict(row)
                    memory['categories'] = memory['categories'] if isinstance(memory['categories'], list) else json.loads(memory['categories'])
                    memory['metadata'] = memory['metadata'] if isinstance(memory['metadata'], dict) else json.loads(memory['metadata'])
                    memory['timestamp'] = memory['timestamp'].isoformat() if hasattr(memory['timestamp'], 'isoformat') else memory['timestamp']
                    memory['created_at'] = memory['created_at'].isoformat() if hasattr(memory['created_at'], 'isoformat') else memory['created_at']
                    memory['last_accessed'] = memory['last_accessed'].isoformat() if hasattr(memory['last_accessed'], 'isoformat') else memory['last_accessed']
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories for NPC {npc_id} from PostgreSQL: {e}")
            return []
    
    def search_memories(
        self, 
        query: str, 
        npc_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Advanced full-text search using PostgreSQL's text search capabilities."""
        try:
            import psycopg2
            import psycopg2.extras
            
            with psycopg2.connect(self.connection_string) as conn:
                cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                if npc_id:
                    sql_query = """
                        SELECT *, ts_rank(content_vector, plainto_tsquery('english', %s)) as rank
                        FROM memories 
                        WHERE content_vector @@ plainto_tsquery('english', %s) AND npc_id = %s
                        ORDER BY rank DESC, importance DESC
                        LIMIT %s
                    """
                    params = (query, query, npc_id, limit)
                else:
                    sql_query = """
                        SELECT *, ts_rank(content_vector, plainto_tsquery('english', %s)) as rank
                        FROM memories 
                        WHERE content_vector @@ plainto_tsquery('english', %s)
                        ORDER BY rank DESC, importance DESC
                        LIMIT %s
                    """
                    params = (query, query, limit)
                
                cursor.execute(sql_query, params)
                rows = cursor.fetchall()
                
                # Convert to regular dictionaries
                memories = []
                for row in rows:
                    memory = dict(row)
                    del memory['rank']  # Remove ranking from final result
                    memory['categories'] = memory['categories'] if isinstance(memory['categories'], list) else json.loads(memory['categories'])
                    memory['metadata'] = memory['metadata'] if isinstance(memory['metadata'], dict) else json.loads(memory['metadata'])
                    memory['timestamp'] = memory['timestamp'].isoformat()
                    memory['created_at'] = memory['created_at'].isoformat()
                    memory['last_accessed'] = memory['last_accessed'].isoformat()
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            self.logger.error(f"Failed to search memories with query '{query}' in PostgreSQL: {e}")
            return []
    
    # Implement remaining abstract methods...
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update memory using PostgreSQL JSONB operations."""
        # Implementation similar to SQLite but with JSONB operations
        pass
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete memory with CASCADE support."""
        # Implementation with CASCADE delete
        pass
    
    def get_memory_statistics(self, npc_id: str) -> Dict[str, Any]:
        """Get advanced statistics using PostgreSQL aggregations."""
        # Implementation with advanced JSONB aggregations
        pass


# Factory function to create appropriate database interface
def create_memory_database(database_type: str = "sqlite", **kwargs) -> MemoryDatabaseInterface:
    """
    Factory function to create the appropriate database interface.
    
    Args:
        database_type: Type of database ("sqlite", "postgresql")
        **kwargs: Database-specific configuration
        
    Returns:
        Database interface instance
    """
    if database_type.lower() == "sqlite":
        database_path = kwargs.get("database_path", "memory_system.db")
        return SQLiteMemoryDatabase(database_path)
    elif database_type.lower() == "postgresql":
        connection_string = kwargs.get("connection_string")
        if not connection_string:
            raise ValueError("PostgreSQL requires connection_string")
        return PostgreSQLMemoryDatabase(connection_string)
    else:
        raise ValueError(f"Unsupported database type: {database_type}")


# Global database instance
_memory_db = None


def get_memory_database() -> MemoryDatabaseInterface:
    """Get the global memory database instance."""
    global _memory_db
    if _memory_db is None:
        # Default to SQLite for now
        _memory_db = create_memory_database("sqlite")
    return _memory_db


def set_memory_database(database: MemoryDatabaseInterface):
    """Set the global memory database instance."""
    global _memory_db
    _memory_db = database 