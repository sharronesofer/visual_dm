import { BuildingBase, BuildingType, POICategory, Coordinate } from '../types/buildings/base';
import { SocialBuilding, Inn, Shop, Tavern, GuildHall, NPCHome, SocialService, RoomType, ShopType, EntertainmentType, SocialStatus } from '../types/buildings/social';
import { DungeonStructure, EnemyLair, PuzzleRoom, TreasureChamber, TrapRoom, DifficultyRating, PuzzleType, TrapType, DamageType, RewardType } from '../types/buildings/dungeon';
import { ExplorationFeature, Ruins, Campsite, Landmark, ResourceNode, InteractionType, Season, PreservationState, ArtifactType, CampsiteFacility, RestQuality, LandmarkType, ResourceType } from '../types/buildings/exploration';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

// Base validation
export function validateBuildingBase(building: BuildingBase): ValidationResult {
  const errors: string[] = [];
  
  if (!building.id) errors.push('Missing id');
  if (!building.name) errors.push('Missing name');
  if (!Object.values(BuildingType).includes(building.type)) {
    errors.push(`Invalid building type: ${building.type}`);
  }
  if (!Object.values(POICategory).includes(building.category)) {
    errors.push(`Invalid POI category: ${building.category}`);
  }
  if (!building.dimensions || typeof building.dimensions.width !== 'number' || typeof building.dimensions.height !== 'number') {
    errors.push('Invalid dimensions');
  }
  if (!Array.isArray(building.entrances) || !building.entrances.every(isValidCoordinate)) {
    errors.push('Invalid entrances');
  }
  if (!Array.isArray(building.tags)) errors.push('Invalid tags');
  if (typeof building.minDangerLevel !== 'number' || typeof building.maxDangerLevel !== 'number') {
    errors.push('Invalid danger level range');
  }
  if (building.minDangerLevel > building.maxDangerLevel) {
    errors.push('Min danger level cannot be greater than max danger level');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// Social building validation
export function validateSocialBuilding(building: SocialBuilding): ValidationResult {
  const baseValidation = validateBuildingBase(building);
  const errors = [...baseValidation.errors];

  if (building.category !== POICategory.SOCIAL) {
    errors.push('Invalid category for social building');
  }
  if (typeof building.npcCapacity !== 'number' || building.npcCapacity < 0) {
    errors.push('Invalid NPC capacity');
  }
  if (!isValidTimeRange(building.openingHours)) {
    errors.push('Invalid opening hours');
  }
  if (!Array.isArray(building.services) || building.services.length === 0) {
    errors.push('Invalid services');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// Dungeon structure validation
export function validateDungeonStructure(structure: DungeonStructure): ValidationResult {
  const baseValidation = validateBuildingBase(structure);
  const errors = [...baseValidation.errors];

  if (structure.category !== POICategory.DUNGEON) {
    errors.push('Invalid category for dungeon structure');
  }
  if (!Object.values(DifficultyRating).includes(structure.difficulty)) {
    errors.push('Invalid difficulty rating');
  }
  if (typeof structure.requiredLevel !== 'number' || structure.requiredLevel < 1) {
    errors.push('Invalid required level');
  }
  if (!Array.isArray(structure.rewards) || structure.rewards.length === 0) {
    errors.push('Invalid rewards');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// Exploration feature validation
export function validateExplorationFeature(feature: ExplorationFeature): ValidationResult {
  const baseValidation = validateBuildingBase(feature);
  const errors = [...baseValidation.errors];

  if (feature.category !== POICategory.EXPLORATION) {
    errors.push('Invalid category for exploration feature');
  }
  if (typeof feature.discoveryDC !== 'number' || feature.discoveryDC < 1) {
    errors.push('Invalid discovery DC');
  }
  if (!Array.isArray(feature.interactionType) || feature.interactionType.length === 0) {
    errors.push('Invalid interaction types');
  }
  if (!Array.isArray(feature.seasonalAvailability)) {
    errors.push('Invalid seasonal availability');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// Specific building type validation
export function validateInn(inn: Inn): ValidationResult {
  const socialValidation = validateSocialBuilding(inn);
  const errors = [...socialValidation.errors];

  if (inn.type !== BuildingType.INN) {
    errors.push('Invalid type for inn');
  }
  if (typeof inn.roomCount !== 'number' || inn.roomCount < 1) {
    errors.push('Invalid room count');
  }
  if (!Array.isArray(inn.roomTypes) || !inn.roomTypes.every(type => Object.values(RoomType).includes(type))) {
    errors.push('Invalid room types');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

export function validateShop(shop: Shop): ValidationResult {
  const socialValidation = validateSocialBuilding(shop);
  const errors = [...socialValidation.errors];

  if (shop.type !== BuildingType.SHOP) {
    errors.push('Invalid type for shop');
  }
  if (!Object.values(ShopType).includes(shop.shopType)) {
    errors.push('Invalid shop type');
  }
  if (typeof shop.inventorySize !== 'number' || shop.inventorySize < 0) {
    errors.push('Invalid inventory size');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

// Helper functions
function isValidCoordinate(coord: Coordinate): boolean {
  return typeof coord.x === 'number' && typeof coord.y === 'number';
}

function isValidTimeRange(time: { start: number; end: number }): boolean {
  return (
    typeof time.start === 'number' &&
    typeof time.end === 'number' &&
    time.start >= 0 &&
    time.start <= 23 &&
    time.end >= 0 &&
    time.end <= 23
  );
} 