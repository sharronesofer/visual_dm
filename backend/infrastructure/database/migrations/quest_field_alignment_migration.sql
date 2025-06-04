-- Quest System Field Alignment Migration
-- Migrates existing quest data to align with business logic requirements
-- Run Date: 2025-01-16
-- Version: 1.0.0

BEGIN;

-- Create backup table before migration
CREATE TABLE quest_entities_backup AS SELECT * FROM quest_entities;

-- Update quest_type field to new status field with correct enum values
-- Add new status column if it doesn't exist
ALTER TABLE quest_entities 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';

-- Migrate quest_type to status with correct enum mapping
UPDATE quest_entities SET status = CASE 
    WHEN quest_type = 'MAIN' THEN 'pending'
    WHEN quest_type = 'SIDE' THEN 'pending' 
    WHEN quest_type = 'CHARACTER' THEN 'pending'
    WHEN quest_type = 'FACTION' THEN 'pending'
    WHEN quest_type = 'RANDOM' THEN 'pending'
    ELSE 'pending'
END WHERE status = 'pending' OR status IS NULL;

-- Update current_status to align with new enum values
UPDATE quest_entities SET current_status = CASE
    WHEN current_status = 'available' THEN 'pending'
    WHEN current_status = 'offered' THEN 'pending'
    WHEN current_status = 'in-progress' THEN 'active'
    WHEN current_status = 'cancelled' THEN 'abandoned'
    WHEN current_status = 'active' THEN 'active'
    WHEN current_status = 'completed' THEN 'completed'
    WHEN current_status = 'failed' THEN 'failed'
    WHEN current_status = 'abandoned' THEN 'abandoned'
    WHEN current_status = 'expired' THEN 'expired'
    ELSE 'pending'
END;

-- Add difficulty and theme columns if they don't exist
ALTER TABLE quest_entities 
ADD COLUMN IF NOT EXISTS difficulty VARCHAR(50) DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS theme VARCHAR(50) DEFAULT 'general';

-- Set default difficulty based on difficulty_level
UPDATE quest_entities SET difficulty = CASE
    WHEN difficulty_level >= 1 AND difficulty_level <= 3 THEN 'easy'
    WHEN difficulty_level >= 4 AND difficulty_level <= 6 THEN 'medium'
    WHEN difficulty_level >= 7 AND difficulty_level <= 9 THEN 'hard'
    WHEN difficulty_level >= 10 THEN 'epic'
    ELSE 'medium'
END WHERE difficulty = 'medium' OR difficulty IS NULL;

-- Set theme based on existing quest properties or defaults
UPDATE quest_entities SET theme = CASE
    WHEN properties->>'type' = 'combat' THEN 'combat'
    WHEN properties->>'type' = 'exploration' THEN 'exploration'
    WHEN properties->>'type' = 'social' THEN 'social'
    WHEN properties->>'type' = 'mystery' THEN 'mystery'
    WHEN properties->>'type' = 'crafting' THEN 'crafting'
    WHEN properties->>'type' = 'trade' THEN 'trade'
    WHEN properties->>'type' = 'aid' THEN 'aid'
    WHEN properties->>'type' = 'knowledge' THEN 'knowledge'
    ELSE 'general'
END WHERE theme = 'general' OR theme IS NULL;

-- Rename giver_id to npc_id if column exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'quest_entities' AND column_name = 'giver_id') THEN
        
        -- Add npc_id column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'quest_entities' AND column_name = 'npc_id') THEN
            ALTER TABLE quest_entities ADD COLUMN npc_id UUID;
        END IF;
        
        -- Copy data from giver_id to npc_id
        UPDATE quest_entities SET npc_id = giver_id WHERE npc_id IS NULL;
        
        -- Drop the old column (comment out if you want to keep it for rollback)
        -- ALTER TABLE quest_entities DROP COLUMN giver_id;
    END IF;
END $$;

-- Update objectives JSONB structure to align with business logic
-- Convert old step format to new step format
UPDATE quest_entities 
SET objectives = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'id', COALESCE((step->>'step_number')::int, (step->>'id')::int, idx + 1),
            'title', COALESCE(step->>'title', 
                CASE step->>'step_type'
                    WHEN 'KILL' THEN 'Eliminate Target'
                    WHEN 'DELIVER' THEN 'Deliver Item'
                    WHEN 'TALK' THEN 'Speak With Contact'
                    WHEN 'EXPLORE' THEN 'Explore Area'
                    WHEN 'GATHER' THEN 'Collect Materials'
                    ELSE 'Complete Task'
                END),
            'description', COALESCE(step->>'description', 'Complete this objective'),
            'completed', COALESCE((step->>'completed')::boolean, false),
            'required', true,
            'order', COALESCE((step->>'step_number')::int, (step->>'order')::int, idx + 1),
            'metadata', COALESCE(step->'metadata', 
                jsonb_build_object('target_id', step->>'target_id'))
        )
    )
    FROM (
        SELECT 
            jsonb_array_elements(objectives) AS step,
            ROW_NUMBER() OVER () - 1 AS idx
        WHERE objectives IS NOT NULL 
        AND jsonb_typeof(objectives) = 'array'
    ) steps
)
WHERE objectives IS NOT NULL 
AND jsonb_typeof(objectives) = 'array'
AND jsonb_array_length(objectives) > 0;

-- Update rewards JSONB structure to align with business logic
UPDATE quest_entities 
SET rewards = jsonb_build_object(
    'gold', COALESCE((rewards->>'gold')::int, 0),
    'experience', COALESCE(
        (rewards->>'experience')::int, 
        (rewards->>'experience_points')::int, 
        0
    ),
    'reputation', COALESCE(rewards->'reputation', '{}'::jsonb),
    'items', COALESCE(rewards->'items', '[]'::jsonb),
    'special', COALESCE(rewards->'special', '{}'::jsonb)
)
WHERE rewards IS NOT NULL;

-- Add level column if it doesn't exist and populate from recommended_level
ALTER TABLE quest_entities 
ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1;

UPDATE quest_entities 
SET level = COALESCE(recommended_level, 1)
WHERE level = 1 OR level IS NULL;

-- Create properties field with legacy data for rollback purposes
UPDATE quest_entities 
SET properties = COALESCE(properties, '{}'::jsonb) || jsonb_build_object(
    'legacy_quest_type', quest_type,
    'legacy_current_status', current_status,
    'migration_date', NOW()::text,
    'migration_version', '1.0.0'
);

-- Add constraints for new enum values
ALTER TABLE quest_entities 
ADD CONSTRAINT check_status_values 
CHECK (current_status IN ('pending', 'active', 'completed', 'failed', 'abandoned', 'expired'));

ALTER TABLE quest_entities 
ADD CONSTRAINT check_difficulty_values 
CHECK (difficulty IN ('easy', 'medium', 'hard', 'epic'));

ALTER TABLE quest_entities 
ADD CONSTRAINT check_theme_values 
CHECK (theme IN ('combat', 'exploration', 'social', 'mystery', 'crafting', 'trade', 'aid', 'knowledge', 'general'));

-- Update indexes for better performance on new fields
CREATE INDEX IF NOT EXISTS idx_quest_status ON quest_entities (current_status);
CREATE INDEX IF NOT EXISTS idx_quest_difficulty ON quest_entities (difficulty);
CREATE INDEX IF NOT EXISTS idx_quest_theme ON quest_entities (theme);
CREATE INDEX IF NOT EXISTS idx_quest_npc ON quest_entities (npc_id);
CREATE INDEX IF NOT EXISTS idx_quest_level ON quest_entities (level);

-- Record migration completion
INSERT INTO schema_migrations (version, description, executed_at) 
VALUES ('20250116_001', 'Quest field alignment migration', NOW())
ON CONFLICT (version) DO NOTHING;

COMMIT;

-- Rollback script (run separately if needed):
/*
BEGIN;

-- Restore from backup
DELETE FROM quest_entities;
INSERT INTO quest_entities SELECT * FROM quest_entities_backup;

-- Remove migration record
DELETE FROM schema_migrations WHERE version = '20250116_001';

-- Drop backup table
DROP TABLE quest_entities_backup;

COMMIT;
*/ 