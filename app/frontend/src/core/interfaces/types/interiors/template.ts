import { BuildingType, POICategory } from '../buildings/base';

export enum RoomType {
  ENTRANCE = 'ENTRANCE',
  MAIN_HALL = 'MAIN_HALL',
  BEDROOM = 'BEDROOM',
  KITCHEN = 'KITCHEN',
  STORAGE = 'STORAGE',
  CORRIDOR = 'CORRIDOR',
  BATHROOM = 'BATHROOM',
  STUDY = 'STUDY',
  WORKSHOP = 'WORKSHOP',
  GARDEN = 'GARDEN',
  COURTYARD = 'COURTYARD',
  THRONE_ROOM = 'THRONE_ROOM',
  TREASURY = 'TREASURY',
  ARMORY = 'ARMORY',
  LIBRARY = 'LIBRARY',
  DUNGEON = 'DUNGEON'
}

export enum FurnitureType {
  BED = 'BED',
  TABLE = 'TABLE',
  CHAIR = 'CHAIR',
  CHEST = 'CHEST',
  SHELF = 'SHELF',
  COUNTER = 'COUNTER',
  WORKBENCH = 'WORKBENCH',
  THRONE = 'THRONE',
  WEAPON_RACK = 'WEAPON_RACK',
  BOOKSHELF = 'BOOKSHELF',
  DISPLAY_CASE = 'DISPLAY_CASE',
  ALTAR = 'ALTAR',
  STATUE = 'STATUE',
  FOUNTAIN = 'FOUNTAIN'
}

export enum GroupArrangement {
  GRID = 'GRID',
  CIRCLE = 'CIRCLE',
  LINE = 'LINE',
  CLUSTER = 'CLUSTER'
}

export enum FurniturePlacementType {
  CENTER = 'CENTER',
  AGAINST_WALL = 'AGAINST_WALL',
  NEAR_WALL = 'NEAR_WALL',
  NEAR_FURNITURE = 'NEAR_FURNITURE',
  CORNER = 'CORNER',
  RANDOM = 'RANDOM'
}

export enum SpacingType {
  BETWEEN_FURNITURE = 'BETWEEN_FURNITURE',
  WALKWAY = 'WALKWAY',
  CLEARANCE = 'CLEARANCE'
}

export enum DecorationType {
  LIGHT_SOURCE = 'LIGHT_SOURCE',
  TAPESTRY = 'TAPESTRY',
  RUG = 'RUG',
  PAINTING = 'PAINTING',
  PLANT = 'PLANT',
  WINDOW = 'WINDOW',
  CURTAIN = 'CURTAIN',
  BANNER = 'BANNER',
  TROPHY = 'TROPHY'
}

export enum DecorationPlacementType {
  ON_WALL = 'ON_WALL',
  ON_FLOOR = 'ON_FLOOR',
  ON_CEILING = 'ON_CEILING',
  ON_FURNITURE = 'ON_FURNITURE'
}

export enum NPCZoneType {
  SERVICE = 'SERVICE',
  SOCIAL = 'SOCIAL',
  WORK = 'WORK',
  REST = 'REST',
  GUARD = 'GUARD'
}

export enum NPCActivityType {
  STANDING = 'STANDING',
  SITTING = 'SITTING',
  WALKING = 'WALKING',
  WORKING = 'WORKING',
  SLEEPING = 'SLEEPING',
  GUARDING = 'GUARDING'
}

export enum InteractiveObjectType {
  SERVICE_POINT = 'SERVICE_POINT',
  QUEST_BOARD = 'QUEST_BOARD',
  CRAFTING_STATION = 'CRAFTING_STATION',
  STORAGE_CONTAINER = 'STORAGE_CONTAINER',
  DOOR = 'DOOR',
  TRAP = 'TRAP',
  PUZZLE = 'PUZZLE',
  TREASURE = 'TREASURE'
}

export enum InteractiveObjectPlacementType {
  NEAR_WALL = 'NEAR_WALL',
  NEAR_FURNITURE = 'NEAR_FURNITURE',
  CENTER = 'CENTER',
  CORNER = 'CORNER',
  RANDOM = 'RANDOM'
}

export enum RoomPlacementType {
  NEAR_EDGE = 'NEAR_EDGE',
  ADJACENT_TO = 'ADJACENT_TO',
  SAME_FLOOR = 'SAME_FLOOR',
  RANDOM = 'RANDOM'
}

export interface InteriorTemplate {
  id: string;
  name: string;
  buildingType: BuildingType;
  category: POICategory;
  roomLayouts: RoomLayout[];
  furnitureRules: FurnitureRule[];
  decorationSchemes: DecorationScheme[];
  npcZones: NPCZoneDefinition[];
  interactiveObjects: InteractiveObjectRule[];
}

export interface RoomLayout {
  id: string;
  name: string;
  type: RoomType;
  minSize: { width: number; length: number };
  maxSize: { width: number; length: number };
  requiredConnections: RoomType[];
  optionalConnections: RoomType[];
  priority: number;
  placementRules: RoomPlacementRule[];
}

export interface RoomPlacementRule {
  type: RoomPlacementType;
  parameters: Record<string, any>;
}

export interface FurnitureRule {
  roomType: RoomType;
  requiredFurniture: FurniturePlacementRule[];
  optionalFurniture: FurniturePlacementRule[];
  groupings: FurnitureGrouping[];
  spacingRules: SpacingRule[];
}

export interface FurniturePlacementRule {
  type: FurnitureType;
  minCount: number;
  maxCount: number;
  placementRules: {
    type: FurniturePlacementType;
    parameters: Record<string, any>;
  }[];
}

export interface FurnitureGrouping {
  name: string;
  furniture: { type: FurnitureType; count: number }[];
  arrangement: GroupArrangement;
  spacing: number;
}

export interface SpacingRule {
  type: SpacingType;
  distance: number;
}

export interface DecorationScheme {
  roomType: RoomType;
  theme: string;
  decorations: DecorationRule[];
  colorPalette: string[];
  density: number;
}

export interface DecorationRule {
  type: DecorationType;
  minCount: number;
  maxCount: number;
  placementRules: {
    type: DecorationPlacementType;
    parameters: Record<string, any>;
  }[];
}

export interface NPCZoneDefinition {
  roomType: RoomType;
  zoneType: NPCZoneType;
  capacity: number;
  requiredFurniture: FurnitureType[];
  activityType: NPCActivityType[];
}

export interface InteractiveObjectRule {
  roomType: RoomType;
  objectType: InteractiveObjectType;
  count: number;
  placementRules: {
    type: InteractiveObjectPlacementType;
    parameters: Record<string, any>;
  }[];
  requiredSpace: number;
} 