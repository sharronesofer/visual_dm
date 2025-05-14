export type Position = {
  x: number;
  y: number;
};

export type Dimensions = {
  width: number;
  height: number;
};

export type Range = {
  start: Position;
  end: Position;
};

export type TerrainType = 
  | 'plains'
  | 'forest'
  | 'mountain'
  | 'water'
  | 'desert'
  | 'swamp';

export type VisibilityState = 
  | 'visible'
  | 'discovered'
  | 'hidden';

export type MovementType = 
  | 'walk'
  | 'swim'
  | 'fly';

export type FactionAffiliation = 
  | 'neutral'
  | 'friendly'
  | 'hostile'
  | 'unknown';

export type Direction = 
  | 'north'
  | 'northeast'
  | 'east'
  | 'southeast'
  | 'south'
  | 'southwest'
  | 'west'
  | 'northwest'; 