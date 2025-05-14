-- Create enum for rarity levels
CREATE TYPE item_rarity AS ENUM (
  'COMMON',
  'UNCOMMON',
  'RARE',
  'EPIC',
  'LEGENDARY'
);

-- Create rarity tiers table
CREATE TABLE rarity_tiers (
  id SERIAL PRIMARY KEY,
  name item_rarity NOT NULL UNIQUE,
  probability DECIMAL(5,4) NOT NULL CHECK (probability > 0 AND probability <= 1),
  value_multiplier DECIMAL(10,2) NOT NULL CHECK (value_multiplier > 0),
  color_hex VARCHAR(7) NOT NULL CHECK (color_hex ~ '^#[0-9A-Fa-f]{6}$'),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add rarity_id to items table
ALTER TABLE items
ADD COLUMN rarity_id INTEGER REFERENCES rarity_tiers(id);

-- Create index on rarity_id
CREATE INDEX idx_items_rarity ON items(rarity_id);

-- Insert default rarity tiers
INSERT INTO rarity_tiers (name, probability, value_multiplier, color_hex) VALUES
  ('COMMON', 0.6000, 1.00, '#FFFFFF'),     -- White
  ('UNCOMMON', 0.2500, 2.00, '#1EFF00'),   -- Green
  ('RARE', 0.1000, 5.00, '#0070DD'),       -- Blue
  ('EPIC', 0.0400, 10.00, '#A335EE'),      -- Purple
  ('LEGENDARY', 0.0100, 20.00, '#FF8000');  -- Orange 