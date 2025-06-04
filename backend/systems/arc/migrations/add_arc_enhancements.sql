-- Migration: Add Arc System Enhancements
-- Version: 1.0.0
-- Description: Add relationship fields, enhanced metadata, and progression tracking

-- Add new fields to arc_entities table
ALTER TABLE arc_entities 
ADD COLUMN predecessor_arcs JSONB DEFAULT '[]',
ADD COLUMN successor_arcs JSONB DEFAULT '[]',
ADD COLUMN related_arcs JSONB DEFAULT '[]',
ADD COLUMN relationship_generation_prompt TEXT,
ADD COLUMN outcome_influences JSONB DEFAULT '{}';

-- Create arc_relationships table
CREATE TABLE IF NOT EXISTS arc_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_arc_id UUID NOT NULL REFERENCES arc_entities(id) ON DELETE CASCADE,
    target_arc_id UUID NOT NULL REFERENCES arc_entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN (
        'sequel', 'prequel', 'parallel', 'branching', 'confluence', 
        'thematic_link', 'continuation', 'consequence'
    )),
    influence_level VARCHAR(20) NOT NULL DEFAULT 'moderate' CHECK (influence_level IN (
        'minimal', 'moderate', 'major', 'critical'
    )),
    influence_data JSONB DEFAULT '{}',
    narrative_connection TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT no_self_reference CHECK (source_arc_id != target_arc_id),
    CONSTRAINT unique_arc_relationship UNIQUE (source_arc_id, target_arc_id, relationship_type)
);

-- Create indexes for performance
CREATE INDEX idx_arc_relationships_source ON arc_relationships(source_arc_id);
CREATE INDEX idx_arc_relationships_target ON arc_relationships(target_arc_id);
CREATE INDEX idx_arc_relationships_type ON arc_relationships(relationship_type);
CREATE INDEX idx_arc_entities_predecessor_arcs ON arc_entities USING GIN (predecessor_arcs);
CREATE INDEX idx_arc_entities_successor_arcs ON arc_entities USING GIN (successor_arcs);
CREATE INDEX idx_arc_entities_related_arcs ON arc_entities USING GIN (related_arcs);

-- Enhanced arc_progression table
ALTER TABLE arc_progression 
ADD COLUMN milestone_data JSONB DEFAULT '[]',
ADD COLUMN risk_factors JSONB DEFAULT '[]',
ADD COLUMN completion_confidence DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN velocity_data JSONB DEFAULT '{}',
ADD COLUMN engagement_metrics JSONB DEFAULT '{}';

-- Create arc_milestones table for detailed milestone tracking
CREATE TABLE IF NOT EXISTS arc_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    progression_id UUID NOT NULL REFERENCES arc_progression(id) ON DELETE CASCADE,
    milestone_type VARCHAR(50) NOT NULL,
    milestone_id VARCHAR(100) NOT NULL,
    achieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT NOT NULL,
    significance VARCHAR(20) DEFAULT 'medium' CHECK (significance IN ('low', 'medium', 'high', 'special')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_milestone UNIQUE (progression_id, milestone_type)
);

-- Create indexes for milestone tracking
CREATE INDEX idx_arc_milestones_progression ON arc_milestones(progression_id);
CREATE INDEX idx_arc_milestones_type ON arc_milestones(milestone_type);
CREATE INDEX idx_arc_milestones_achieved ON arc_milestones(achieved_at);

-- Enhanced arc_steps table
ALTER TABLE arc_steps 
ADD COLUMN validation_data JSONB DEFAULT '{}',
ADD COLUMN transition_history JSONB DEFAULT '[]',
ADD COLUMN business_rule_errors JSONB DEFAULT '[]',
ADD COLUMN completion_analytics JSONB DEFAULT '{}';

-- Create arc_step_validation_log for tracking validation history
CREATE TABLE IF NOT EXISTS arc_step_validation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID NOT NULL REFERENCES arc_steps(id) ON DELETE CASCADE,
    validation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    validation_type VARCHAR(50) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    errors JSONB DEFAULT '[]',
    warnings JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    
    -- Index for performance
    INDEX (step_id, validation_timestamp DESC)
);

-- Create arc_complexity_reports table
CREATE TABLE IF NOT EXISTS arc_complexity_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    arc_id UUID NOT NULL REFERENCES arc_entities(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    complexity_score INTEGER NOT NULL CHECK (complexity_score BETWEEN 0 AND 100),
    complexity_factors JSONB NOT NULL DEFAULT '[]',
    expansion_recommended BOOLEAN NOT NULL DEFAULT FALSE,
    expansion_reasoning TEXT,
    suggested_steps INTEGER,
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    generated_by VARCHAR(100), -- Could be 'system', 'user', or specific AI model
    report_data JSONB DEFAULT '{}',
    
    -- Indexes
    INDEX (arc_id, generated_at DESC),
    INDEX (complexity_score),
    INDEX (expansion_recommended)
);

-- Create trigger function for updating updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_arc_relationships_updated_at 
    BEFORE UPDATE ON arc_relationships 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add trigger to maintain relationship consistency
CREATE OR REPLACE FUNCTION maintain_arc_relationship_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- When inserting/updating a relationship, update the arc references
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Update source arc's successor_arcs or related_arcs
        IF NEW.relationship_type IN ('sequel', 'continuation') THEN
            UPDATE arc_entities 
            SET successor_arcs = successor_arcs || jsonb_build_array(NEW.target_arc_id::text)
            WHERE id = NEW.source_arc_id 
            AND NOT (successor_arcs ? NEW.target_arc_id::text);
            
            UPDATE arc_entities 
            SET predecessor_arcs = predecessor_arcs || jsonb_build_array(NEW.source_arc_id::text)
            WHERE id = NEW.target_arc_id 
            AND NOT (predecessor_arcs ? NEW.source_arc_id::text);
            
        ELSIF NEW.relationship_type = 'prequel' THEN
            UPDATE arc_entities 
            SET predecessor_arcs = predecessor_arcs || jsonb_build_array(NEW.target_arc_id::text)
            WHERE id = NEW.source_arc_id 
            AND NOT (predecessor_arcs ? NEW.target_arc_id::text);
            
            UPDATE arc_entities 
            SET successor_arcs = successor_arcs || jsonb_build_array(NEW.source_arc_id::text)
            WHERE id = NEW.target_arc_id 
            AND NOT (successor_arcs ? NEW.source_arc_id::text);
            
        ELSE -- parallel, thematic_link, etc.
            UPDATE arc_entities 
            SET related_arcs = related_arcs || jsonb_build_array(NEW.target_arc_id::text)
            WHERE id = NEW.source_arc_id 
            AND NOT (related_arcs ? NEW.target_arc_id::text);
            
            UPDATE arc_entities 
            SET related_arcs = related_arcs || jsonb_build_array(NEW.source_arc_id::text)
            WHERE id = NEW.target_arc_id 
            AND NOT (related_arcs ? NEW.source_arc_id::text);
        END IF;
        
        RETURN NEW;
    END IF;
    
    -- When deleting a relationship, clean up arc references
    IF TG_OP = 'DELETE' THEN
        -- Remove from successor/predecessor/related arrays
        UPDATE arc_entities 
        SET successor_arcs = successor_arcs - OLD.target_arc_id::text,
            predecessor_arcs = predecessor_arcs - OLD.target_arc_id::text,
            related_arcs = related_arcs - OLD.target_arc_id::text
        WHERE id = OLD.source_arc_id;
        
        UPDATE arc_entities 
        SET successor_arcs = successor_arcs - OLD.source_arc_id::text,
            predecessor_arcs = predecessor_arcs - OLD.source_arc_id::text,
            related_arcs = related_arcs - OLD.source_arc_id::text
        WHERE id = OLD.target_arc_id;
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for relationship consistency
CREATE TRIGGER maintain_arc_relationships
    AFTER INSERT OR UPDATE OR DELETE ON arc_relationships
    FOR EACH ROW EXECUTE FUNCTION maintain_arc_relationship_consistency();

-- Create function to validate arc business rules in database
CREATE OR REPLACE FUNCTION validate_arc_business_rules(arc_data JSONB)
RETURNS JSONB AS $$
DECLARE
    violations JSONB := '[]'::JSONB;
    arc_type TEXT;
    total_steps INTEGER;
    faction_count INTEGER;
BEGIN
    -- Extract key fields
    arc_type := arc_data->>'arc_type';
    total_steps := COALESCE((arc_data->>'total_steps')::INTEGER, 0);
    faction_count := COALESCE(jsonb_array_length(arc_data->'faction_ids'), 0);
    
    -- Global arc validation
    IF arc_type = 'global' THEN
        IF (arc_data->>'priority') = 'low' THEN
            violations := violations || '"Global arcs should not have low priority"';
        END IF;
        
        IF COALESCE((arc_data->>'estimated_duration_hours')::INTEGER, 0) < 20 THEN
            violations := violations || '"Global arcs should have at least 20 hours estimated duration"';
        END IF;
        
        IF faction_count < 2 THEN
            violations := violations || '"Global arcs should involve at least 2 factions"';
        END IF;
    END IF;
    
    -- Character arc validation
    IF arc_type = 'character' THEN
        IF arc_data->>'character_id' IS NULL THEN
            violations := violations || '"Character arcs must have a character_id"';
        END IF;
        
        IF total_steps > 10 THEN
            violations := violations || '"Character arcs should not exceed 10 steps for personal focus"';
        END IF;
    END IF;
    
    -- Regional arc validation
    IF arc_type = 'regional' THEN
        IF arc_data->>'region_id' IS NULL THEN
            violations := violations || '"Regional arcs must have a region_id"';
        END IF;
        
        IF COALESCE((arc_data->>'difficulty_level')::INTEGER, 5) > 8 THEN
            violations := violations || '"Regional arcs should not exceed difficulty 8"';
        END IF;
    END IF;
    
    -- General validation
    IF total_steps > 50 THEN
        violations := violations || '"Total steps should not exceed 50 for manageable complexity"';
    END IF;
    
    RETURN violations;
END;
$$ LANGUAGE plpgsql;

-- Create view for arc relationship network analysis
CREATE OR REPLACE VIEW arc_relationship_network AS
SELECT 
    a.id as arc_id,
    a.title,
    a.arc_type,
    a.status,
    COALESCE(jsonb_array_length(a.predecessor_arcs), 0) as predecessor_count,
    COALESCE(jsonb_array_length(a.successor_arcs), 0) as successor_count,
    COALESCE(jsonb_array_length(a.related_arcs), 0) as related_count,
    (
        COALESCE(jsonb_array_length(a.predecessor_arcs), 0) +
        COALESCE(jsonb_array_length(a.successor_arcs), 0) +
        COALESCE(jsonb_array_length(a.related_arcs), 0)
    ) as total_connections,
    a.created_at
FROM arc_entities a;

-- Create view for progression analytics
CREATE OR REPLACE VIEW arc_progression_summary AS
SELECT 
    a.id as arc_id,
    a.title,
    a.arc_type,
    a.status as arc_status,
    COUNT(p.id) as total_progressions,
    COUNT(CASE WHEN p.status = 'active' THEN 1 END) as active_progressions,
    COUNT(CASE WHEN p.status = 'completed' THEN 1 END) as completed_progressions,
    AVG(p.progress_percentage) as avg_progress,
    AVG(p.time_spent) as avg_time_spent,
    MAX(p.last_activity) as last_activity
FROM arc_entities a
LEFT JOIN arc_progression p ON a.id = p.arc_id
GROUP BY a.id, a.title, a.arc_type, a.status;

-- Insert sample data for testing (optional)
INSERT INTO arc_entities (
    title, description, arc_type, status, priority, 
    themes, objectives, difficulty_level,
    predecessor_arcs, successor_arcs, related_arcs,
    outcome_influences
) VALUES (
    'Sample Enhanced Arc',
    'A test arc with relationship capabilities',
    'regional',
    'pending',
    'medium',
    '["adventure", "mystery"]',
    '["Investigate mystery", "Solve puzzle", "Restore peace"]',
    6,
    '[]',
    '[]', 
    '[]',
    '{"mystery_solved": "Opens new questlines", "peace_restored": "Improves regional stability"}'
) ON CONFLICT DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE arc_relationships IS 'Defines relationships between arcs for narrative continuity';
COMMENT ON TABLE arc_milestones IS 'Tracks player achievements and progress milestones within arcs';
COMMENT ON TABLE arc_complexity_reports IS 'Stores AI-generated complexity analysis and expansion recommendations';
COMMENT ON COLUMN arc_entities.predecessor_arcs IS 'Array of arc IDs that must complete before this arc';
COMMENT ON COLUMN arc_entities.successor_arcs IS 'Array of arc IDs that follow this arc';
COMMENT ON COLUMN arc_entities.related_arcs IS 'Array of arc IDs with thematic or narrative connections';
COMMENT ON COLUMN arc_entities.outcome_influences IS 'JSON object defining how different outcomes affect future arcs';

-- Migration complete
SELECT 'Arc system enhancements migration completed successfully' as result; 