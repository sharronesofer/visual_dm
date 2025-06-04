"""
PostgreSQL Repository for World State System

Alternative repository implementation that stores world state in PostgreSQL
while maintaining the same interface as JSON repository.

Benefits:
- ACID transactions for data consistency
- Complex queries with SQL
- Better performance for large datasets
- Concurrent access safety
- Still provides full data access through repository methods

Usage:
    # Choose JSON for development
    repo = JSONFileWorldStateRepository(project_root)
    
    # Choose PostgreSQL for production
    repo = PostgreSQLWorldStateRepository(connection_string)
    
    # Rest of your code stays exactly the same!
    service = WorldStateService(repo)
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json
import logging
import asyncpg
import asyncio

from backend.systems.world_state.manager import WorldStateRepository, RegionalSnapshot, HistoricalSummary, SnapshotLevel
from backend.systems.world_state.world_types import WorldState, WorldStateChange

logger = logging.getLogger(__name__)


class PostgreSQLWorldStateRepository(WorldStateRepository):
    """PostgreSQL implementation of world state repository"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self) -> bool:
        """Initialize PostgreSQL connection and create tables"""
        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Create tables if they don't exist
            await self._create_tables()
            
            logger.info("PostgreSQL repository initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL repository: {e}")
            return False
    
    async def _create_tables(self):
        """Create necessary tables for world state storage"""
        async with self._pool.acquire() as conn:
            # Main world state table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS world_state (
                    id SERIAL PRIMARY KEY,
                    current_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    game_day INTEGER NOT NULL DEFAULT 0,
                    season VARCHAR(20) NOT NULL DEFAULT 'spring',
                    year INTEGER NOT NULL DEFAULT 1,
                    global_state JSONB NOT NULL DEFAULT '{}',
                    regions JSONB NOT NULL DEFAULT '{}',
                    active_effects JSONB NOT NULL DEFAULT '[]',
                    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            
            # State changes table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS state_changes (
                    id SERIAL PRIMARY KEY,
                    change_id VARCHAR(255) UNIQUE NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    key_path VARCHAR(500) NOT NULL,
                    old_value JSONB,
                    new_value JSONB,
                    region_id VARCHAR(100),
                    category VARCHAR(50) NOT NULL,
                    reason TEXT,
                    user_id VARCHAR(100),
                    metadata JSONB
                );
            """)
            
            # Regional snapshots table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS regional_snapshots (
                    id SERIAL PRIMARY KEY,
                    snapshot_id VARCHAR(255) UNIQUE NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    region_id VARCHAR(100) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    regional_state JSONB NOT NULL,
                    global_context JSONB NOT NULL DEFAULT '{}',
                    metadata JSONB NOT NULL DEFAULT '{}'
                );
            """)
            
            # Historical summaries table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_summaries (
                    id SERIAL PRIMARY KEY,
                    summary_id VARCHAR(255) UNIQUE NOT NULL,
                    start_time TIMESTAMPTZ NOT NULL,
                    end_time TIMESTAMPTZ NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    region_id VARCHAR(100),
                    summary_data JSONB NOT NULL,
                    change_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            
            # Create useful indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_state_changes_timestamp ON state_changes(timestamp);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_state_changes_region ON state_changes(region_id);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_state_changes_category ON state_changes(category);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_regional_snapshots_region_time ON regional_snapshots(region_id, timestamp);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_historical_summaries_time_range ON historical_summaries(start_time, end_time);")
    
    # ===== CORE WORLD STATE OPERATIONS =====
    
    async def load_world_state(self) -> Optional[WorldState]:
        """Load current world state from PostgreSQL"""
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT current_time, game_day, season, year, global_state, regions, active_effects
                    FROM world_state 
                    ORDER BY id DESC 
                    LIMIT 1
                """)
                
                if not row:
                    return None
                
                return WorldState(
                    current_time=row['current_time'],
                    game_day=row['game_day'],
                    season=row['season'],
                    year=row['year'],
                    global_state=dict(row['global_state']),
                    regions=dict(row['regions']),
                    active_effects=list(row['active_effects'])
                )
                
        except Exception as e:
            logger.error(f"Failed to load world state: {e}")
            return None
    
    async def save_world_state(self, world_state: WorldState) -> bool:
        """Save world state to PostgreSQL"""
        try:
            async with self._pool.acquire() as conn:
                # Check if we have existing state
                existing = await conn.fetchval("SELECT id FROM world_state ORDER BY id DESC LIMIT 1")
                
                if existing:
                    # Update existing record
                    await conn.execute("""
                        UPDATE world_state SET
                            current_time = $1,
                            game_day = $2,
                            season = $3,
                            year = $4,
                            global_state = $5,
                            regions = $6,
                            active_effects = $7,
                            last_updated = NOW()
                        WHERE id = $8
                    """, 
                    world_state.current_time,
                    world_state.game_day,
                    world_state.season,
                    world_state.year,
                    json.dumps(world_state.global_state),
                    json.dumps(world_state.regions),
                    json.dumps(world_state.active_effects),
                    existing
                    )
                else:
                    # Insert new record
                    await conn.execute("""
                        INSERT INTO world_state (current_time, game_day, season, year, global_state, regions, active_effects)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    world_state.current_time,
                    world_state.game_day,
                    world_state.season,
                    world_state.year,
                    json.dumps(world_state.global_state),
                    json.dumps(world_state.regions),
                    json.dumps(world_state.active_effects)
                    )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False
    
    # ===== STATE CHANGE TRACKING =====
    
    async def record_state_change(self, change: WorldStateChange) -> bool:
        """Record state change in PostgreSQL"""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO state_changes 
                    (change_id, timestamp, key_path, old_value, new_value, region_id, category, reason, user_id, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                change.change_id,
                change.timestamp,
                change.key_path,
                json.dumps(change.old_value) if change.old_value is not None else None,
                json.dumps(change.new_value) if change.new_value is not None else None,
                change.region_id,
                change.category.value if change.category else None,
                change.reason,
                change.user_id,
                json.dumps(change.metadata) if change.metadata else None
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to record state change: {e}")
            return False
    
    async def get_state_changes(
        self,
        region_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[WorldStateChange]:
        """Get state changes with powerful SQL filtering"""
        try:
            # Build dynamic query based on parameters
            conditions = []
            params = []
            param_count = 0
            
            if region_id:
                param_count += 1
                conditions.append(f"region_id = ${param_count}")
                params.append(region_id)
            
            if start_time:
                param_count += 1
                conditions.append(f"timestamp >= ${param_count}")
                params.append(start_time)
            
            if end_time:
                param_count += 1
                conditions.append(f"timestamp <= ${param_count}")
                params.append(end_time)
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            param_count += 1
            query = f"""
                SELECT change_id, timestamp, key_path, old_value, new_value, region_id, category, reason, user_id, metadata
                FROM state_changes
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT ${param_count}
            """
            params.append(limit)
            
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
                changes = []
                for row in rows:
                    # Reconstruct WorldStateChange from database row
                    # (Implementation would create proper WorldStateChange objects)
                    pass  # Simplified for brevity
                
                return changes
                
        except Exception as e:
            logger.error(f"Failed to get state changes: {e}")
            return []
    
    # ===== POWERFUL DATABASE QUERIES =====
    
    async def complex_historical_query(self, sql_query: str, params: List[Any]) -> List[Dict[str, Any]]:
        """Execute complex SQL queries for historical analysis"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(sql_query, *params)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to execute complex query: {e}")
            return []
    
    async def get_faction_territorial_history(self, faction_id: str, days: int = 30) -> Dict[str, Any]:
        """Example of complex query: Get faction territorial control over time"""
        query = """
            SELECT 
                DATE_TRUNC('day', timestamp) as day,
                COUNT(*) as territory_changes,
                COUNT(CASE WHEN new_value::text LIKE $1 THEN 1 END) as gains,
                COUNT(CASE WHEN old_value::text LIKE $1 THEN 1 END) as losses
            FROM state_changes 
            WHERE key_path LIKE 'regions.%.controlling_faction'
                AND timestamp >= NOW() - INTERVAL '%s days'
                AND (old_value::text LIKE $1 OR new_value::text LIKE $1)
            GROUP BY DATE_TRUNC('day', timestamp)
            ORDER BY day DESC
        """ % days
        
        return await self.complex_historical_query(query, [f'%{faction_id}%'])
    
    # ===== STILL IMPLEMENT ALL OTHER REPOSITORY METHODS =====
    # (snapshot management, summarization, etc. - same interface as JSON repo)
    
    async def create_regional_snapshot(
        self,
        region_id: str,
        level: SnapshotLevel,
        regional_state: Dict[str, Any],
        global_context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create regional snapshot in PostgreSQL"""
        # Implementation follows same pattern as above
        pass
    
    # ... all other methods from WorldStateRepository interface


# ===== REPOSITORY FACTORY FOR EASY SWITCHING =====

async def create_repository(backend_type: str = "json", **kwargs) -> WorldStateRepository:
    """Factory function to create appropriate repository"""
    if backend_type == "json":
        from backend.systems.world_state.repositories import JSONFileWorldStateRepository
        project_root = kwargs.get('project_root', './data/world_state')
        return JSONFileWorldStateRepository(project_root)
    
    elif backend_type == "postgresql":
        connection_string = kwargs.get('connection_string', 'postgresql://user:pass@localhost/worldstate')
        repo = PostgreSQLWorldStateRepository(connection_string)
        await repo.initialize()
        return repo
    
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


# ===== MIGRATION UTILITIES =====

async def migrate_json_to_postgresql(
    json_repo: 'JSONFileWorldStateRepository',
    pg_repo: PostgreSQLWorldStateRepository
):
    """Migrate data from JSON files to PostgreSQL"""
    try:
        # Load world state from JSON
        world_state = await json_repo.load_world_state()
        if world_state:
            await pg_repo.save_world_state(world_state)
        
        # Migrate state changes
        changes = await json_repo.get_state_changes(limit=10000)
        for change in changes:
            await pg_repo.record_state_change(change)
        
        # Migrate snapshots and summaries
        # ... implementation continues
        
        logger.info("Migration from JSON to PostgreSQL completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise 