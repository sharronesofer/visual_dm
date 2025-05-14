export enum BuildingType {
  INN = 'INN',
  SHOP = 'SHOP',
  TAVERN = 'TAVERN',
  GUILD_HALL = 'GUILD_HALL',
  NPC_HOME = 'NPC_HOME',
  ENEMY_LAIR = 'ENEMY_LAIR',
  PUZZLE_ROOM = 'PUZZLE_ROOM',
  TREASURE_CHAMBER = 'TREASURE_CHAMBER',
  TRAP_ROOM = 'TRAP_ROOM',
  RUINS = 'RUINS',
  CAMPSITE = 'CAMPSITE',
  LANDMARK = 'LANDMARK',
  RESOURCE_NODE = 'RESOURCE_NODE'
}

export enum POICategory {
  SOCIAL = 'SOCIAL',
  DUNGEON = 'DUNGEON',
  EXPLORATION = 'EXPLORATION'
}

export interface BuildingBase {
  id: string;
  name: string;
  type: BuildingType;
  category: POICategory;
  dimensions: {
    width: number;
    length: number;
    height: number;
  };
  entrances: Coordinate[];
  tags: string[];
  minDangerLevel: number;
  maxDangerLevel: number;
}

export interface Coordinate {
  x: number;
  y: number;
} 