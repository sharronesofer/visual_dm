-- Create enum for item types
CREATE TYPE item_type AS ENUM (
  'WEAPON',
  'ARMOR',
  'POTION',
  'SCROLL',
  'MATERIAL',
  'TREASURE',
  'KEY',
  'QUEST',
  'MISC'
);

-- Create base items table
CREATE TABLE items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  type item_type NOT NULL,
  weight DECIMAL(10,2) NOT NULL CHECK (weight >= 0),
  value INTEGER NOT NULL CHECK (value >= 0),
  base_stats JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on commonly queried fields
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_value ON items(value);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 