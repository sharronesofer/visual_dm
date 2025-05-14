import { BuildingType, InteriorParams, InteriorLayout, InteriorMesh, VariationParams, Room, FurniturePlacement, DecorationPlacement, Door } from './types';
import { BSPLayout } from './BSPLayout';
import { BuildingTemplates } from './BuildingTemplates';
import { FurniturePlacer } from './FurniturePlacer';
import { DecorationPlacer } from './DecorationPlacer';
import { InteriorTemplateManager } from '../../managers/InteriorTemplateManager';
import { Vector2, distance, randomRange } from '../../utils/math';
import { NPCZoneType, NPCZoneDefinition, InteractiveObjectRule, InteractiveObjectType, InteractiveObjectPlacementType, FurnitureType } from '../../types/interiors/template';

interface CacheKey {
  buildingType: BuildingType;
  width: number;
  length: number;
  height: number;
  region?: string;
  culture?: string;
}

interface CacheEntry {
  params: InteriorParams;
  layout: InteriorLayout;
  timestamp: number;
}

interface NPCZone {
  id: string;
  type: NPCZoneType;
  area: {
    x: number;
    y: number;
    width: number;
    length: number;
  };
  roomId: string;
  capacity: number;
}

interface InteractiveObject {
  id: string;
  type: InteractiveObjectType;
  position: Vector2;
  rotation: number;
  roomId: string;
}

export class InteriorGenerator {
  private templateManager: InteriorTemplateManager;
  private layoutCache: Map<string, CacheEntry> = new Map();
  private readonly CACHE_EXPIRY_MS = 30 * 60 * 1000; // 30 minutes
  private readonly DOOR_SPACING = 2; // Minimum spacing between doors
  private rooms: Room[] = [];
  private template: {
    npcZones: Array<{
      roomType: string;
      zoneType: NPCZoneType;
      capacity: number;
      requiredFurniture: FurnitureType[];
    }>;
    interactiveObjects: Array<{
      roomType: string;
      objectType: InteractiveObjectType;
      count: number;
      requiredSpace: number;
      placementRules: Array<{
        type: InteractiveObjectPlacementType;
        parameters: {
          furnitureType?: FurnitureType;
        };
      }>;
    }>;
  };

  constructor(
    private readonly params: InteriorParams,
    private readonly templateManager: InteriorTemplateManager
  ) {
    this.templateManager = templateManager;
    this.template = templateManager.getTemplateForBuilding(params.buildingType);
  }

  generate(params: InteriorParams): InteriorLayout {
    // Check cache first
    const cached = this.getCachedLayout(params);
    if (cached) return cached;

    // 1. Get appropriate template
    const template = this.templateManager.getTemplateForBuilding(params.buildingType);
    if (!template) {
      throw new Error(`No template found for building type ${params.buildingType}`);
    }

    // 2. Generate room structure
    const bsp = new BSPLayout(params);
    let rooms = bsp.generateRooms();

    // 3. Assign room types from template
    rooms = rooms.map((room, i) => ({
      ...room,
      type: template.roomLayouts[i % template.roomLayouts.length]?.type || 'generic'
    }));

    // 4. Generate doors between rooms
    const doors = this.generateDoors(rooms, template);

    // 5. Place furniture
    const furniturePlacer = new FurniturePlacer();
    const furniture = furniturePlacer.placeFurniture(rooms);

    // 6. Place decorations
    const decorationPlacer = new DecorationPlacer();
    const decorations = decorationPlacer.placeDecorations(rooms, template.decorationSchemes);

    // 7. Create layout and cache it
    const layout = {
      rooms,
      doors,
      furniture,
      decorations
    };

    this.cacheLayout(params, layout);
    return layout;
  }

  private generateDoors(rooms: Room[], template: any): Door[] {
    const doors: Door[] = [];
    const processedPairs = new Set<string>();

    // Helper to create a unique key for a room pair
    const getPairKey = (r1: string, r2: string) => [r1, r2].sort().join('-');

    // For each room
    for (const room1 of rooms) {
      // Find adjacent rooms
      for (const room2 of rooms) {
        if (room1.id === room2.id) continue;

        const pairKey = getPairKey(room1.id, room2.id);
        if (processedPairs.has(pairKey)) continue;
        processedPairs.add(pairKey);

        // Check if rooms are adjacent
        if (this.areRoomsAdjacent(room1, room2)) {
          // Check template rules for allowed connections
          const room1Layout = template.roomLayouts.find((l: any) => l.type === room1.type);
          const room2Layout = template.roomLayouts.find((l: any) => l.type === room2.type);

          if (this.canRoomsConnect(room1Layout, room2Layout)) {
            // Generate door position
            const doorPos = this.findDoorPosition(room1, room2, doors);
            if (doorPos) {
              doors.push({
                fromRoom: room1.id,
                toRoom: room2.id,
                x: doorPos.x,
                y: doorPos.y
              });
            }
          }
        }
      }
    }

    return doors;
  }

  private areRoomsAdjacent(room1: Room, room2: Room): boolean {
    // Check if rooms share a wall
    const shareVerticalWall = (
      Math.abs((room1.x + room1.width) - room2.x) <= 1 ||
      Math.abs((room2.x + room2.width) - room1.x) <= 1
    ) && (
      Math.max(room1.y, room2.y) < Math.min(room1.y + room1.length, room2.y + room2.length)
    );

    const shareHorizontalWall = (
      Math.abs((room1.y + room1.length) - room2.y) <= 1 ||
      Math.abs((room2.y + room2.length) - room1.y) <= 1
    ) && (
      Math.max(room1.x, room2.x) < Math.min(room1.x + room1.width, room2.x + room2.width)
    );

    return shareVerticalWall || shareHorizontalWall;
  }

  private canRoomsConnect(room1Layout: any, room2Layout: any): boolean {
    if (!room1Layout || !room2Layout) return true; // Default to allowing connection if no rules

    return (
      room1Layout.requiredConnections.includes(room2Layout.type) ||
      room1Layout.optionalConnections.includes(room2Layout.type) ||
      room2Layout.requiredConnections.includes(room1Layout.type) ||
      room2Layout.optionalConnections.includes(room1Layout.type)
    );
  }

  private findDoorPosition(room1: Room, room2: Room, existingDoors: Door[]): Vector2 | null {
    let sharedWallStart: Vector2;
    let sharedWallEnd: Vector2;

    // Find shared wall coordinates
    if (Math.abs((room1.x + room1.width) - room2.x) <= 1 || Math.abs((room2.x + room2.width) - room1.x) <= 1) {
      // Vertical wall
      const x = Math.abs((room1.x + room1.width) - room2.x) <= 1 ? room1.x + room1.width : room1.x;
      const y1 = Math.max(room1.y, room2.y);
      const y2 = Math.min(room1.y + room1.length, room2.y + room2.length);
      sharedWallStart = { x, y: y1 };
      sharedWallEnd = { x, y: y2 };
    } else {
      // Horizontal wall
      const y = Math.abs((room1.y + room1.length) - room2.y) <= 1 ? room1.y + room1.length : room1.y;
      const x1 = Math.max(room1.x, room2.x);
      const x2 = Math.min(room1.x + room1.width, room2.x + room2.width);
      sharedWallStart = { x: x1, y };
      sharedWallEnd = { x: x2, y };
    }

    // Try to place door in middle of shared wall if possible
    const midPoint: Vector2 = {
      x: (sharedWallStart.x + sharedWallEnd.x) / 2,
      y: (sharedWallStart.y + sharedWallEnd.y) / 2
    };

    // Check if midpoint is far enough from existing doors
    if (this.isValidDoorPosition(midPoint, existingDoors)) {
      return midPoint;
    }

    // Try other positions along the wall if midpoint doesn't work
    const wallLength = distance(sharedWallStart, sharedWallEnd);
    const steps = Math.floor(wallLength / this.DOOR_SPACING);

    for (let i = 1; i <= steps; i++) {
      const t = i / (steps + 1);
      const pos: Vector2 = {
        x: sharedWallStart.x + (sharedWallEnd.x - sharedWallStart.x) * t,
        y: sharedWallStart.y + (sharedWallEnd.y - sharedWallStart.y) * t
      };

      if (this.isValidDoorPosition(pos, existingDoors)) {
        return pos;
      }
    }

    return null;
  }

  private isValidDoorPosition(pos: Vector2, existingDoors: Door[]): boolean {
    // Check distance from other doors
    for (const door of existingDoors) {
      const doorPos: Vector2 = { x: door.x, y: door.y };
      if (distance(pos, doorPos) < this.DOOR_SPACING) {
        return false;
      }
    }
    return true;
  }

  generateMesh(layout: InteriorLayout, lod: number): InteriorMesh {
    // Basic mesh generation - can be expanded based on LOD requirements
    const vertices: number[][] = [];
    const faces: number[][] = [];

    // Generate room geometry
    for (const room of layout.rooms) {
      const baseIndex = vertices.length;

      // Floor vertices
      vertices.push([room.x, 0, room.y]);
      vertices.push([room.x + room.width, 0, room.y]);
      vertices.push([room.x + room.width, 0, room.y + room.length]);
      vertices.push([room.x, 0, room.y + room.length]);

      // Floor face
      faces.push([baseIndex, baseIndex + 1, baseIndex + 2, baseIndex + 3]);

      // Wall vertices and faces if LOD > 1
      if (lod > 1) {
        const height = 3; // Standard wall height
        vertices.push([room.x, height, room.y]);
        vertices.push([room.x + room.width, height, room.y]);
        vertices.push([room.x + room.width, height, room.y + room.length]);
        vertices.push([room.x, height, room.y + room.length]);

        // Wall faces
        faces.push([baseIndex, baseIndex + 1, baseIndex + 5, baseIndex + 4]); // Front
        faces.push([baseIndex + 1, baseIndex + 2, baseIndex + 6, baseIndex + 5]); // Right
        faces.push([baseIndex + 2, baseIndex + 3, baseIndex + 7, baseIndex + 6]); // Back
        faces.push([baseIndex + 3, baseIndex, baseIndex + 4, baseIndex + 7]); // Left
      }
    }

    return {
      vertices,
      faces,
      lod
    };
  }

  private getCacheKey(params: InteriorParams): string {
    const key: CacheKey = {
      buildingType: params.buildingType,
      width: params.width,
      length: params.length,
      height: params.height,
      region: params.region,
      culture: params.culture
    };
    return JSON.stringify(key);
  }

  cacheLayout(params: InteriorParams, layout: InteriorLayout): void {
    const key = this.getCacheKey(params);
    this.layoutCache.set(key, {
      params,
      layout,
      timestamp: Date.now()
    });

    // Clean old cache entries
    this.cleanCache();
  }

  getCachedLayout(params: InteriorParams): InteriorLayout | null {
    const key = this.getCacheKey(params);
    const cached = this.layoutCache.get(key);

    if (!cached) return null;

    // Check if cache has expired
    if (Date.now() - cached.timestamp > this.CACHE_EXPIRY_MS) {
      this.layoutCache.delete(key);
      return null;
    }

    return cached.layout;
  }

  private cleanCache(): void {
    const now = Date.now();
    for (const [key, entry] of this.layoutCache.entries()) {
      if (now - entry.timestamp > this.CACHE_EXPIRY_MS) {
        this.layoutCache.delete(key);
      }
    }
  }

  /**
   * Define NPC zones in rooms based on template rules
   */
  private defineNPCZones(): NPCZone[] {
    const zones: NPCZone[] = [];

    // Process each room
    for (const room of this.rooms) {
      // Find zone definitions for this room type
      const roomZones = this.template.npcZones.filter((zone: { roomType: string }) => zone.roomType === room.type);
      
      for (const zoneDefinition of roomZones) {
        // Calculate zone size based on capacity and room size
        const zoneSize = this.calculateNPCZoneSize(zoneDefinition, room);
        if (!zoneSize) continue;

        // Find valid position for zone
        const zonePosition = this.findNPCZonePosition(room, zoneSize, zoneDefinition, zones);
        if (!zonePosition) continue;

        // Create zone
        zones.push({
          id: crypto.randomUUID(),
          type: zoneDefinition.zoneType,
          area: {
            x: zonePosition.x,
            y: zonePosition.y,
            width: zoneSize.width,
            length: zoneSize.length
          },
          roomId: room.id,
          capacity: zoneDefinition.capacity
        });
      }
    }

    return zones;
  }

  /**
   * Calculate appropriate size for an NPC zone based on capacity and room size
   */
  private calculateNPCZoneSize(
    zoneDefinition: NPCZoneDefinition,
    room: Room
  ): { width: number; length: number } | null {
    // Calculate space needed per NPC (varies by zone type)
    const spacePerNPC = this.getSpacePerNPC(zoneDefinition.zoneType);
    
    // Calculate total area needed
    const totalArea = spacePerNPC * zoneDefinition.capacity;
    
    // Try to maintain a reasonable aspect ratio
    const maxWidth = room.width * 0.8; // Don't use more than 80% of room width
    const maxLength = room.length * 0.8; // Don't use more than 80% of room length
    
    // Calculate dimensions maintaining area while respecting max sizes
    let width = Math.sqrt(totalArea);
    let length = width;
    
    if (width > maxWidth) {
      width = maxWidth;
      length = totalArea / width;
    }
    
    if (length > maxLength) {
      length = maxLength;
      width = totalArea / length;
    }
    
    // Return null if the zone won't fit
    if (width > maxWidth || length > maxLength) {
      return null;
    }
    
    return { width, length };
  }

  /**
   * Get space needed per NPC based on zone type
   */
  private getSpacePerNPC(zoneType: NPCZoneType): number {
    switch (zoneType) {
      case NPCZoneType.SERVICE:
        return 4; // Need space for counter/workspace
      case NPCZoneType.SOCIAL:
        return 3; // Space for movement and interaction
      case NPCZoneType.WORK:
        return 4; // Space for workstation
      case NPCZoneType.REST:
        return 6; // Space for bed/furniture
      case NPCZoneType.GUARD:
        return 2; // Just standing space
      default:
        return 3;
    }
  }

  /**
   * Find a valid position for an NPC zone in a room
   */
  private findNPCZonePosition(
    room: Room,
    zoneSize: { width: number; length: number },
    zoneDefinition: NPCZoneDefinition,
    existingZones: NPCZone[]
  ): Vector2 | null {
    // Check if zone requires specific furniture
    if (zoneDefinition.requiredFurniture.length > 0) {
      return this.findZoneNearFurniture(room, zoneSize, zoneDefinition.requiredFurniture[0], existingZones);
    }

    // Try positions in a grid pattern
    const stepX = (room.width - zoneSize.width) / 4;
    const stepY = (room.length - zoneSize.length) / 4;

    for (let x = room.x; x <= room.x + room.width - zoneSize.width; x += stepX) {
      for (let y = room.y; y <= room.y + room.length - zoneSize.length; y += stepY) {
        const pos = { x, y };
        if (this.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos;
        }
      }
    }

    return null;
  }

  /**
   * Find a zone position near required furniture
   */
  private findZoneNearFurniture(
    room: Room,
    zoneSize: { width: number; length: number },
    requiredFurnitureType: FurnitureType,
    existingZones: NPCZone[]
  ): Vector2 | null {
    // Find furniture of required type in room
    const furniture = this.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === requiredFurnitureType);

    if (!furniture || furniture.length === 0) return null;

    // Try positions near each piece of furniture
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - zoneSize.width, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - zoneSize.length },
        { x: piece.position.x, y: piece.position.y + 1 }
      ];

      for (const pos of positions) {
        if (this.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos;
        }
      }
    }

    return null;
  }

  /**
   * Check if a position is valid for an NPC zone
   */
  private isValidZonePosition(
    position: Vector2,
    zoneSize: { width: number; length: number },
    room: Room,
    existingZones: NPCZone[]
  ): boolean {
    // Check room boundaries
    if (
      position.x < room.x ||
      position.y < room.y ||
      position.x + zoneSize.width > room.x + room.width ||
      position.y + zoneSize.length > room.y + room.length
    ) {
      return false;
    }

    // Check overlap with existing zones
    for (const zone of existingZones.filter(z => z.roomId === room.id)) {
      if (
        position.x < zone.area.x + zone.area.width &&
        position.x + zoneSize.width > zone.area.x &&
        position.y < zone.area.y + zone.area.length &&
        position.y + zoneSize.length > zone.area.y
      ) {
        return false;
      }
    }

    return true;
  }

  /**
   * Place interactive objects in rooms according to template rules
   */
  private placeInteractiveObjects(): InteractiveObject[] {
    const objects: InteractiveObject[] = [];

    // Process each room
    for (const room of this.rooms) {
      // Find object rules for this room type
      const roomObjects = this.template.interactiveObjects.filter((obj: { roomType: string }) => obj.roomType === room.type);

      for (const objectRule of roomObjects) {
        // Place required number of objects
        for (let i = 0; i < objectRule.count; i++) {
          const position = this.findObjectPosition(room, objectRule, objects);
          if (!position) continue;

          objects.push({
            id: crypto.randomUUID(),
            type: objectRule.objectType,
            position,
            rotation: this.calculateObjectRotation(position, room, objectRule),
            roomId: room.id
          });
        }
      }
    }

    return objects;
  }

  /**
   * Find a valid position for an interactive object
   */
  private findObjectPosition(
    room: Room,
    rule: InteractiveObjectRule,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    const placementType = rule.placementRules[0]?.type || InteractiveObjectPlacementType.RANDOM;
    const requiredSpace = rule.requiredSpace;

    switch (placementType) {
      case InteractiveObjectPlacementType.NEAR_WALL:
        return this.findPositionNearWall(room, requiredSpace, existingObjects);

      case InteractiveObjectPlacementType.NEAR_FURNITURE:
        if (rule.placementRules[0].parameters.furnitureType) {
          return this.findPositionNearFurniture(
            room,
            rule.placementRules[0].parameters.furnitureType,
            requiredSpace,
            existingObjects
          );
        }
        return this.findRandomPosition(room, requiredSpace, existingObjects);

      case InteractiveObjectPlacementType.CENTER:
        return this.findCenterPosition(room, requiredSpace, existingObjects);

      case InteractiveObjectPlacementType.CORNER:
        return this.findCornerPosition(room, requiredSpace, existingObjects);

      case InteractiveObjectPlacementType.RANDOM:
      default:
        return this.findRandomPosition(room, requiredSpace, existingObjects);
    }
  }

  /**
   * Find a position near a wall for an interactive object
   */
  private findPositionNearWall(
    room: Room,
    requiredSpace: number,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    const wallPositions = [
      // Left wall
      ...Array.from({ length: room.length - requiredSpace }, (_, i) => ({
        x: room.x,
        y: room.y + i
      })),
      // Right wall
      ...Array.from({ length: room.length - requiredSpace }, (_, i) => ({
        x: room.x + room.width - requiredSpace,
        y: room.y + i
      })),
      // Top wall
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y
      })),
      // Bottom wall
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y + room.length - requiredSpace
      }))
    ];

    // Shuffle positions for variety
    for (let i = wallPositions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [wallPositions[i], wallPositions[j]] = [wallPositions[j], wallPositions[i]];
    }

    // Find first valid position
    for (const pos of wallPositions) {
      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos;
      }
    }

    return null;
  }

  /**
   * Find a position near specific furniture
   */
  private findPositionNearFurniture(
    room: Room,
    furnitureType: FurnitureType,
    requiredSpace: number,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    // Find furniture of required type in room
    const furniture = this.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === furnitureType);

    if (!furniture || furniture.length === 0) return null;

    // Try positions around each piece of furniture
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - requiredSpace, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - requiredSpace },
        { x: piece.position.x, y: piece.position.y + 1 }
      ];

      for (const pos of positions) {
        if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos;
        }
      }
    }

    return null;
  }

  /**
   * Find a position in the center of the room
   */
  private findCenterPosition(
    room: Room,
    requiredSpace: number,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    const center = {
      x: room.x + Math.floor(room.width / 2) - Math.floor(requiredSpace / 2),
      y: room.y + Math.floor(room.length / 2) - Math.floor(requiredSpace / 2)
    };

    if (this.isValidObjectPosition(center, requiredSpace, room, existingObjects)) {
      return center;
    }

    // Try positions around the center if exact center doesn't work
    const radius = 1;
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = {
          x: center.x + dx,
          y: center.y + dy
        };
        if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos;
        }
      }
    }

    return null;
  }

  /**
   * Find a position in a corner of the room
   */
  private findCornerPosition(
    room: Room,
    requiredSpace: number,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    const corners = [
      { x: room.x, y: room.y },
      { x: room.x + room.width - requiredSpace, y: room.y },
      { x: room.x, y: room.y + room.length - requiredSpace },
      { x: room.x + room.width - requiredSpace, y: room.y + room.length - requiredSpace }
    ];

    // Try each corner
    for (const pos of corners) {
      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos;
      }
    }

    return null;
  }

  /**
   * Find a random position in the room
   */
  private findRandomPosition(
    room: Room,
    requiredSpace: number,
    existingObjects: InteractiveObject[]
  ): Vector2 | null {
    // Try several random positions
    for (let attempts = 0; attempts < 10; attempts++) {
      const pos = {
        x: room.x + Math.floor(Math.random() * (room.width - requiredSpace)),
        y: room.y + Math.floor(Math.random() * (room.length - requiredSpace))
      };

      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos;
      }
    }

    return null;
  }

  /**
   * Check if a position is valid for an interactive object
   */
  private isValidObjectPosition(
    position: Vector2,
    requiredSpace: number,
    room: Room,
    existingObjects: InteractiveObject[]
  ): boolean {
    // Check room boundaries
    if (
      position.x < room.x ||
      position.y < room.y ||
      position.x + requiredSpace > room.x + room.width ||
      position.y + requiredSpace > room.y + room.length
    ) {
      return false;
    }

    // Check distance from other objects
    for (const obj of existingObjects.filter(o => o.roomId === room.id)) {
      const dist = distance(position, obj.position);
      if (dist < requiredSpace) {
        return false;
      }
    }

    return true;
  }

  /**
   * Calculate rotation for an interactive object
   */
  private calculateObjectRotation(
    position: Vector2,
    room: Room,
    rule: InteractiveObjectRule
  ): number {
    const placementType = rule.placementRules[0]?.type || InteractiveObjectPlacementType.RANDOM;

    switch (placementType) {
      case InteractiveObjectPlacementType.NEAR_WALL:
        // Face away from the nearest wall
        if (position.x === room.x) return 0; // Left wall
        if (position.x === room.x + room.width - rule.requiredSpace) return Math.PI; // Right wall
        if (position.y === room.y) return Math.PI / 2; // Top wall
        if (position.y === room.y + room.length - rule.requiredSpace) return -Math.PI / 2; // Bottom wall
        break;

      case InteractiveObjectPlacementType.CENTER:
      case InteractiveObjectPlacementType.CORNER:
        // Face toward room center
        const centerX = room.x + room.width / 2;
        const centerY = room.y + room.length / 2;
        return Math.atan2(centerY - position.y, centerX - position.x);

      case InteractiveObjectPlacementType.RANDOM:
      default:
        return Math.random() * Math.PI * 2;
    }

    return 0;
  }
} 