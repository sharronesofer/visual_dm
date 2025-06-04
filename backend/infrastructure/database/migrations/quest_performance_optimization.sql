-- Quest System Performance Optimization Migration
-- Adds indexes and optimizations for common query patterns
-- Run Date: 2025-01-16
-- Version: 1.1.0

BEGIN;

-- Create performance indexes for common query patterns
-- These indexes target the most frequent query patterns in the quest system

-- Index for player quest queries (most common: get player's active quests)
CREATE INDEX IF NOT EXISTS idx_quest_player_status 
ON quest_entities (player_id, current_status) 
WHERE player_id IS NOT NULL;

-- Index for NPC quest queries (get available quests from specific NPCs)
CREATE INDEX IF NOT EXISTS idx_quest_npc_status 
ON quest_entities (npc_id, current_status) 
WHERE npc_id IS NOT NULL;

-- Index for location-based quest queries (get quests in specific areas)
CREATE INDEX IF NOT EXISTS idx_quest_location_status 
ON quest_entities (location_id, current_status) 
WHERE location_id IS NOT NULL;

-- Composite index for quest filtering by theme and difficulty
CREATE INDEX IF NOT EXISTS idx_quest_theme_difficulty 
ON quest_entities (theme, difficulty, current_status);

-- Index for quest level-based queries (match quests to player level)
CREATE INDEX IF NOT EXISTS idx_quest_level_status 
ON quest_entities (level, current_status);

-- Index for main quest filtering
CREATE INDEX IF NOT EXISTS idx_quest_main_status 
ON quest_entities (is_main_quest, current_status) 
WHERE is_main_quest = true;

-- Index for quest expiry cleanup jobs
CREATE INDEX IF NOT EXISTS idx_quest_expires_at 
ON quest_entities (expires_at) 
WHERE expires_at IS NOT NULL;

-- Index for quest creation date (for analytics and recent quest queries)
CREATE INDEX IF NOT EXISTS idx_quest_created_at 
ON quest_entities (created_at DESC);

-- Index for quest updates (for tracking recent changes)
CREATE INDEX IF NOT EXISTS idx_quest_updated_at 
ON quest_entities (updated_at DESC) 
WHERE updated_at IS NOT NULL;

-- Partial index for pending quests (most commonly queried status)
CREATE INDEX IF NOT EXISTS idx_quest_pending 
ON quest_entities (difficulty, theme, level) 
WHERE current_status = 'pending';

-- Partial index for active quests (second most common)
CREATE INDEX IF NOT EXISTS idx_quest_active 
ON quest_entities (player_id, created_at DESC) 
WHERE current_status = 'active' AND player_id IS NOT NULL;

-- Index for quest statistics queries
CREATE INDEX IF NOT EXISTS idx_quest_stats_status_theme 
ON quest_entities (current_status, theme);

CREATE INDEX IF NOT EXISTS idx_quest_stats_status_difficulty 
ON quest_entities (current_status, difficulty);

-- JSONB indexes for properties and objectives (if using PostgreSQL)
-- These help with queries that filter on quest properties or step completion

-- GIN index for quest properties (enables fast JSONB queries)
CREATE INDEX IF NOT EXISTS idx_quest_properties_gin 
ON quest_entities USING GIN (properties) 
WHERE properties IS NOT NULL;

-- GIN index for quest objectives/steps (enables fast step queries)
CREATE INDEX IF NOT EXISTS idx_quest_objectives_gin 
ON quest_entities USING GIN (objectives) 
WHERE objectives IS NOT NULL;

-- Specific JSONB path indexes for common property queries
CREATE INDEX IF NOT EXISTS idx_quest_generated_from_npc 
ON quest_entities ((properties->>'generated_from_npc')) 
WHERE properties ? 'generated_from_npc';

CREATE INDEX IF NOT EXISTS idx_quest_template_id 
ON quest_entities ((properties->>'template_id')) 
WHERE properties ? 'template_id';

-- Add table statistics update for query planner optimization
ANALYZE quest_entities;

-- Create materialized view for quest statistics (faster analytics)
CREATE MATERIALIZED VIEW IF NOT EXISTS quest_statistics_mv AS
SELECT 
    current_status,
    theme,
    difficulty,
    COUNT(*) as quest_count,
    AVG(level) as avg_level,
    MIN(created_at) as first_created,
    MAX(created_at) as last_created
FROM quest_entities 
GROUP BY current_status, theme, difficulty;

-- Index the materialized view for fast queries
CREATE UNIQUE INDEX IF NOT EXISTS idx_quest_stats_mv_unique
ON quest_statistics_mv (current_status, theme, difficulty);

-- Create function to refresh materialized view (call periodically)
CREATE OR REPLACE FUNCTION refresh_quest_statistics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY quest_statistics_mv;
END;
$$ LANGUAGE plpgsql;

-- Add constraints to improve query performance and data integrity
-- These constraints help the query planner make better decisions

-- Check constraint for valid status values (helps with partial indexes)
ALTER TABLE quest_entities 
ADD CONSTRAINT IF NOT EXISTS check_valid_status 
CHECK (current_status IN ('pending', 'active', 'completed', 'failed', 'abandoned', 'expired'));

-- Check constraint for valid difficulty values
ALTER TABLE quest_entities 
ADD CONSTRAINT IF NOT EXISTS check_valid_difficulty 
CHECK (difficulty IN ('easy', 'medium', 'hard', 'epic'));

-- Check constraint for valid theme values
ALTER TABLE quest_entities 
ADD CONSTRAINT IF NOT EXISTS check_valid_theme 
CHECK (theme IN ('combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general'));

-- Check constraint for reasonable level values
ALTER TABLE quest_entities 
ADD CONSTRAINT IF NOT EXISTS check_reasonable_level 
CHECK (level >= 1 AND level <= 100);

-- Partial unique constraint to prevent duplicate active quests per player per NPC
-- (business rule: player can't have multiple active quests from same NPC)
CREATE UNIQUE INDEX IF NOT EXISTS idx_quest_unique_active_player_npc
ON quest_entities (player_id, npc_id)
WHERE current_status = 'active' AND player_id IS NOT NULL AND npc_id IS NOT NULL;

-- Add comments for maintenance documentation
COMMENT ON INDEX idx_quest_player_status IS 'Optimizes player quest lookup queries';
COMMENT ON INDEX idx_quest_npc_status IS 'Optimizes NPC quest availability queries';
COMMENT ON INDEX idx_quest_location_status IS 'Optimizes location-based quest discovery';
COMMENT ON INDEX idx_quest_theme_difficulty IS 'Optimizes quest filtering by theme and difficulty';
COMMENT ON INDEX idx_quest_pending IS 'Optimizes quest board/available quest queries';
COMMENT ON INDEX idx_quest_active IS 'Optimizes active quest tracking for players';
COMMENT ON MATERIALIZED VIEW quest_statistics_mv IS 'Pre-computed quest statistics for analytics dashboard';

-- Record migration completion
INSERT INTO schema_migrations (version, description, executed_at) 
VALUES ('20250116_002', 'Quest performance optimization migration', NOW())
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Performance tuning recommendations:
/*
1. Run ANALYZE quest_entities regularly (daily) to keep statistics current
2. Refresh quest_statistics_mv periodically (hourly or when needed)
3. Monitor query performance with EXPLAIN ANALYZE
4. Consider partitioning by created_at if quest volume becomes very large
5. Archive old completed/failed quests to separate table if performance degrades

Example maintenance schedule:
- Daily: ANALYZE quest_entities;
- Hourly: SELECT refresh_quest_statistics();
- Weekly: Review slow query log and adjust indexes as needed
- Monthly: Archive quests older than 90 days

Query performance tips:
- Always include status in WHERE clauses when possible
- Use LIMIT for paginated queries
- Prefer specific status filters over NOT status
- Use the materialized view for dashboard statistics
*/ 