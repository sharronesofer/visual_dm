import { Position } from './common';
import { ReactNode } from 'react';

// Custom type for generic properties
type PropertyValue = string | number | boolean | null | PropertyValue[] | { [key: string]: PropertyValue };
type Properties = Record<string, PropertyValue>;

// 2.1: Core POI Data Types
export enum POIType {
  CITY = 'CITY',
  DUNGEON = 'DUNGEON',
  LANDMARK = 'LANDMARK',
  QUEST = 'QUEST',
  SHOP = 'SHOP',
  TAVERN = 'TAVERN',
}

export enum POISize {
  SMALL = 'SMALL',
  MEDIUM = 'MEDIUM',
  LARGE = 'LARGE',
}

export enum POITheme {
  MEDIEVAL = 'MEDIEVAL',
  FANTASY = 'FANTASY',
  STEAMPUNK = 'STEAMPUNK',
  MODERN = 'MODERN',
}

export interface POIMetadata {
  id: string;
  name: string;
  type: POIType;
  position: Position;
  description?: string;
  status?: string;
  metadata?: Record<string, string>;
}

export interface POIState {
  // State
  pois: Record<string, POI>;
  activePOIs: string[];
  currentPOI: string | null;
  isLoading: boolean;
  error: string | null;

  // Basic selectors
  getPOI: (id: string) => POI | undefined;
  getActivePOIs: () => POI[];
  getCurrentPOI: () => POI | null;

  // Error handling
  setError: (error: string | null) => void;
  clearError: () => void;

  // Loading state
  setLoading: (isLoading: boolean) => void;

  // POI Management
  createPOI: (poi: Omit<POI, 'chunks' | 'activeChunks' | 'isActive'>) => void;
  updatePOI: (id: string, updates: Partial<POI>) => void;
  removePOI: (id: string) => void;
  activatePOI: (id: string) => void;
  deactivatePOI: (id: string) => void;
  setCurrentPOI: (id: string | null) => void;
  updatePlayerPosition: (position: Position) => void;

  // Chunk Management
  addChunk: (poiId: string, chunk: Omit<POIChunk, 'lastAccessed'>) => void;
  activateChunk: (poiId: string, position: Position) => void;
  deactivateChunk: (poiId: string, position: Position) => void;
  removeChunk: (poiId: string, position: Position) => void;
  cleanupInactiveChunks: (poiId: string, maxChunks?: number) => void;

  // Entity Management
  addEntity: (poiId: string, chunkPosition: Position, entity: Omit<POIEntity, 'id'>) => void;
  updateEntity: (
    poiId: string,
    chunkPosition: Position,
    entityId: string,
    updates: Partial<POIEntity>
  ) => void;
  removeEntity: (poiId: string, chunkPosition: Position, entityId: string) => void;
  moveEntity: (
    poiId: string,
    entityId: string,
    fromChunkPosition: Position,
    toChunkPosition: Position,
    newPosition: Position
  ) => void;

  // Service Integration
  loadPOI: (id: string) => Promise<POIServiceResponse>;
  loadPOIChunks: (
    poiId: string,
    centerPosition: Position,
    radius?: number
  ) => Promise<POIServiceResponse>;
  savePOIState: (poiId: string) => Promise<POIServiceResponse>;
  syncWithMapStore: (mapChunks: Record<string, any>) => void;

  // Persistence
  initializeFromStorage: () => void;
}

// 2.2: POI Layout Definitions
export interface POILayout {
  width: number;
  height: number;
  rooms: POIRoom[];
  connections: POIConnection[];
}

export interface POIRoom {
  id: string;
  type: string;
  position: Position;
  width: number;
  height: number;
  properties: Properties;
}

export interface POIConnection {
  from: string;
  to: string;
  type: string;
  properties: Properties;
}

export interface POICorridor {
  id: string;
  start: Position;
  end: Position;
  width: number;
  connects: [string, string]; // IDs of rooms it connects
  features: POIFeature[];
}

export interface POIFeature {
  id: string;
  type: string;
  position: Position;
  properties: Properties;
}

export interface POIObstacle {
  type: string;
  position: Position;
  width: number;
  height: number;
  properties: Properties;
}

// 2.3: Entity-Specific Interfaces
export interface POIEntity {
  id: string;
  poiId: string;
  chunkId: string;
  type: string;
  name: string;
  position: Position;
  properties: Properties;
  createdAt: string;
  updatedAt: string;
}

export interface POIEntityState {
  health?: number;
  status?: string[];
  inventory?: POIInventory;
  behavior?: POIBehavior;
  dialogue?: POIDialogue;
  quest?: POIQuest;
}

export interface POIInventory {
  capacity: number;
  items: POIItem[];
}

export interface POIItem {
  id: string;
  type: string;
  quantity: number;
  properties: Record<string, any>;
}

export interface POIBehavior {
  type: string;
  params: Properties;
  schedule?: POISchedule[];
  triggers?: POITrigger[];
}

export interface POISchedule {
  time: number;
  action: string;
  params: Properties;
}

export interface POITrigger {
  condition: string;
  action: string;
  params: Properties;
}

export interface POIDialogue {
  conversations: Record<string, POIConversation>;
  current?: string;
}

export interface POIConversation {
  id: string;
  nodes: POIDialogueNode[];
  conditions?: Properties;
}

export interface POIDialogueNode {
  id: string;
  text: string;
  options: POIDialogueOption[];
}

export interface POIDialogueOption {
  text: string;
  nextId?: string;
  actions?: POIAction[];
  conditions?: Properties;
}

export interface POIDialogueParams {
  initialText: string;
  nodes: POIDialogueNode[];
  title?: string;
}

export interface POIQuest {
  id: string;
  status: 'available' | 'active' | 'completed' | 'failed';
  objectives: POIQuestObjective[];
  rewards: POIReward[];
}

export interface POIQuestObjective {
  description: string;
  completed: boolean;
  conditions?: Record<string, any>;
}

export interface POIQuestParams {
  title: string;
  description: string;
  objectives: POIQuestObjective[];
}

export interface POIInfoParams {
  title: string;
  content: React.ReactNode;
}

// 2.4: Chunk Management
export interface POIChunk {
  id: string;
  poiId: string;
  position: Position;
  entities: Record<string, POIEntity>;
  createdAt: string;
  updatedAt: string;
}

// 2.5: Interaction-Related Types

/**
 * Represents a specific interaction type with a POI
 */
export type POIInteractionType = 'dialogue' | 'quest' | 'info';

/**
 * Represents a feedback type for visual effects
 */
export type POIVisualFeedbackType = 'animation' | 'particle' | 'highlight' | 'text';

/**
 * Represents a requirement for an interaction
 */
export interface POIRequirement {
  type: string;
  value: PropertyValue;
}

/**
 * Represents a reward for completing an interaction
 */
export interface POIReward {
  type: string;
  value: PropertyValue;
}

/**
 * Represents an interaction option that a user can select
 */
export interface POIInteractionOption {
  id: string;
  text: string;
  action: () => void;
}

/**
 * Represents a complete interaction with a POI
 */
export interface POIInteraction {
  id: string;
  type: POIInteractionType;
  title: string;
  description: string;
  options?: POIInteractionOption[];
  requirements?: POIRequirement[];
}

/**
 * Represents an action that can be triggered during a POI interaction
 */
export interface POIAction {
  type: 'dialog' | 'quest' | 'state' | 'animation';
  params: Properties;
  conditions?: Properties;
  feedback?: POIFeedback;
}

/**
 * Represents feedback that can be given during a POI interaction
 */
export interface POIFeedback {
  visual?: POIVisualFeedback;
  audio?: POIAudioFeedback;
  haptic?: POIHapticFeedback;
}

/**
 * Represents visual feedback during a POI interaction
 */
export interface POIVisualFeedback {
  type: POIVisualFeedbackType;
  params: Properties;
  duration: number;
}

/**
 * Represents audio feedback during a POI interaction
 */
export interface POIAudioFeedback {
  type: string;
  source: string;
  volume: number;
  loop: boolean;
  duration: number;
  params?: Properties;
}

/**
 * Represents haptic feedback during a POI interaction
 */
export interface POIHapticFeedback {
  type: 'vibration';
  intensity: number;
  duration: number;
  pattern?: string;
}

/**
 * Type for feedback callback functions
 */
export type POIFeedbackCallbacks = {
  visual?: (message: string) => void;
  audio?: (soundId: string) => void;
  haptic?: (pattern: string) => void;
};

// Service Response Types
export interface POIServiceResponse<T = unknown> {
  success: boolean;
  error?: string;
  data?: T;
}

export interface POILoadOptions {
  includeChunks?: boolean;
  radius?: number;
}

export interface POIGenerationParams {
  type: POIType;
  size: POISize;
  theme: POITheme;
  complexity: number;
  seed?: string;
}

export interface POIGenerationProgress {
  stage: 'layout' | 'features' | 'entities' | 'finalization';
  progress: number;
  currentTask: string;
  error?: Error;
}

export interface POI {
  id: string;
  name: string;
  type: POIType;
  size: POISize;
  theme: POITheme;
  position: Position;
  coordinates: [number, number];
  state: 'active' | 'inactive';
  regionId: string;
  description?: string;
  chunks: Record<string, POIChunk>;
  createdAt: Date;
  updatedAt: Date;
  layout?: POILayout;
  [key: string]: unknown; // Add index signature for Record<string, unknown>
}

export interface POIPersistentState {
  pois: Record<string, POI>;
  activePOIs: string[];
  currentPOI: string | null;
}

// Re-export all types
export type * from './poi';

export interface IPOI {
  id: string;
  name: string;
  coordinates: [number, number]; // [longitude, latitude]
  type: string;
  state: 'active' | 'inactive';
  regionId: string;

  // Methods
  distanceTo(point: [number, number]): number; // Calculate distance in meters
  getDisplayInfo(): { title: string; description?: string; iconUrl?: string };
}

/**
 * Concrete implementation of the IPOI interface.
 */
export class POI implements IPOI {
  id: string;
  name: string;
  coordinates: [number, number];
  type: POIType;
  state: 'active' | 'inactive';
  regionId: string;

  constructor(params: {
    id: string;
    name: string;
    coordinates: [number, number];
    type: POIType;
    state?: 'active' | 'inactive';
    regionId: string;
  }) {
    this.id = params.id;
    this.name = params.name;
    this.coordinates = params.coordinates;
    this.type = params.type;
    this.state = params.state || 'active';
    this.regionId = params.regionId;
    this.validateCoordinates();
  }

  /**
   * Validates that coordinates are within valid longitude/latitude ranges.
   */
  private validateCoordinates() {
    const [lng, lat] = this.coordinates;
    if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
      throw new Error(`Invalid coordinates: [${lng}, ${lat}]`);
    }
  }

  /**
   * Calculates the distance in meters to another point using the Haversine formula.
   */
  distanceTo(point: [number, number]): number {
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const [lng1, lat1] = this.coordinates;
    const [lng2, lat2] = point;
    const R = 6371000; // Earth radius in meters
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Returns display information for the POI.
   */
  getDisplayInfo(): { title: string; description?: string; iconUrl?: string } {
    return {
      title: this.name,
      description: `${this.type} in region ${this.regionId}`,
      iconUrl: undefined, // Could be extended based on type
    };
  }

  /**
   * Changes the state of the POI.
   */
  setState(newState: 'active' | 'inactive') {
    this.state = newState;
  }

  /**
   * Serializes the POI instance to a plain object for JSON.
   */
  toJSON(): object {
    return {
      id: this.id,
      name: this.name,
      coordinates: this.coordinates,
      type: this.type,
      state: this.state,
      regionId: this.regionId,
    };
  }

  /**
   * Deserializes a POI from a plain object.
   */
  static fromJSON(obj: POICreateDTO & { id: string; state?: 'active' | 'inactive'; regionId: string }): POI {
    return new POI({
      id: obj.id,
      name: obj.name,
      coordinates: [obj.position.x, obj.position.y],
      type: obj.type,
      state: obj.state || 'inactive',
      regionId: obj.regionId
    });
  }
}

export interface POISearchOptions {
  radius?: number;
  type?: POIType;
  tags?: string[];
  theme?: POITheme;
  size?: POISize;
}

export interface POICreateDTO {
  name: string;
  type: POIType;
  size: POISize;
  theme: POITheme;
  position: Position;
  description?: string;
  regionId?: string;
  [key: string]: unknown; // Add index signature
}

export type POIUpdateDTO = Partial<POICreateDTO>;
