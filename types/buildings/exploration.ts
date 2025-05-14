import { BuildingBase, BuildingType, POICategory } from './base';

export interface ExplorationFeature extends BuildingBase {
  category: POICategory.EXPLORATION;
  discoveryDC: number;
  interactionType: InteractionType[];
  seasonalAvailability: Season[];
}

export interface Ruins extends ExplorationFeature {
  type: BuildingType.RUINS;
  civilization: string;
  age: number; // in years
  preservationState: PreservationState;
  artifactTypes: ArtifactType[];
}

export interface Campsite extends ExplorationFeature {
  type: BuildingType.CAMPSITE;
  capacity: number;
  facilities: CampsiteFacility[];
  restQuality: RestQuality;
}

export interface Landmark extends ExplorationFeature {
  type: BuildingType.LANDMARK;
  landmarkType: LandmarkType;
  visibility: number; // 1-10
  significance: string[];
}

export interface ResourceNode extends ExplorationFeature {
  type: BuildingType.RESOURCE_NODE;
  resourceType: ResourceType;
  quantity: number;
  respawnTime: number; // in hours
  toolsRequired: string[];
}

export enum InteractionType {
  GATHER = 'GATHER',
  INVESTIGATE = 'INVESTIGATE',
  REST = 'REST',
  NAVIGATE = 'NAVIGATE',
  HARVEST = 'HARVEST'
}

export enum Season {
  SPRING = 'SPRING',
  SUMMER = 'SUMMER',
  AUTUMN = 'AUTUMN',
  WINTER = 'WINTER'
}

export enum PreservationState {
  PRISTINE = 'PRISTINE',
  WEATHERED = 'WEATHERED',
  DAMAGED = 'DAMAGED',
  CRUMBLING = 'CRUMBLING',
  BURIED = 'BURIED'
}

export enum ArtifactType {
  POTTERY = 'POTTERY',
  WEAPONS = 'WEAPONS',
  JEWELRY = 'JEWELRY',
  SCROLLS = 'SCROLLS',
  STATUES = 'STATUES',
  TOOLS = 'TOOLS'
}

export enum CampsiteFacility {
  FIREPIT = 'FIREPIT',
  SHELTER = 'SHELTER',
  WATER_SOURCE = 'WATER_SOURCE',
  STORAGE = 'STORAGE',
  WORKBENCH = 'WORKBENCH'
}

export enum RestQuality {
  POOR = 'POOR',
  ADEQUATE = 'ADEQUATE',
  GOOD = 'GOOD',
  EXCELLENT = 'EXCELLENT'
}

export enum LandmarkType {
  NATURAL = 'NATURAL',
  ARTIFICIAL = 'ARTIFICIAL',
  MAGICAL = 'MAGICAL',
  HISTORICAL = 'HISTORICAL'
}

export enum ResourceType {
  ORE = 'ORE',
  HERBS = 'HERBS',
  WOOD = 'WOOD',
  CRYSTAL = 'CRYSTAL',
  ANIMAL = 'ANIMAL',
  MAGICAL = 'MAGICAL'
} 