import { v4 as uuidv4 } from 'uuid';
import { BuildingBase } from '../types/buildings/base';
import {
  InteriorTemplate,
  RoomLayout,
  RoomType,
  RoomPlacementType,
  FurnitureRule,
  FurniturePlacementRule,
  FurnitureGrouping,
  GroupArrangement,
  FurniturePlacementType,
  DecorationScheme,
  NPCZoneDefinition,
  InteractiveObjectRule
} from '../types/interiors/template';

interface Room {
  id: string;
  type: RoomType;
  position: { x: number; y: number };
  dimensions: { width: number; length: number };
  connections: Room[];
}

interface GeneratedInterior {
  buildingId: string;
  rooms: Room[];
  furniture: GeneratedFurniture[];
  decorations: GeneratedDecoration[];
  npcZones: GeneratedNPCZone[];
  interactiveObjects: GeneratedInteractiveObject[];
}

interface GeneratedFurniture {
  id: string;
  type: string;
  position: { x: number; y: number };
  rotation: number;
  roomId: string;
}

interface GeneratedDecoration {
  id: string;
  type: string;
  position: { x: number; y: number };
  rotation: number;
  roomId: string;
}

interface GeneratedNPCZone {
  id: string;
  type: string;
  area: { x: number; y: number; width: number; length: number };
  roomId: string;
}

interface GeneratedInteractiveObject {
  id: string;
  type: string;
  position: { x: number; y: number };
  rotation: number;
  roomId: string;
}

export class InteriorGenerator {
  private template: InteriorTemplate;
  private building: BuildingBase;
  private rooms: Room[] = [];
  private unplacedRooms: RoomLayout[] = [];
  private readonly MINIMUM_ROOM_SPACING = 1;

  constructor(template: InteriorTemplate, building: BuildingBase) {
    this.template = template;
    this.building = building;
    this.unplacedRooms = [...template.roomLayouts].sort((a, b) => b.priority - a.priority);
  }

  /**
   * Generate a complete interior based on the template and building
   */
  generate(): GeneratedInterior {
    this.generateRoomLayout();
    const furniture = this.placeFurniture();
    const decorations = this.placeDecorations();
    const npcZones = this.defineNPCZones();
    const interactiveObjects = this.placeInteractiveObjects();

    return {
      buildingId: this.building.id,
      rooms: this.rooms,
      furniture,
      decorations,
      npcZones,
      interactiveObjects
    };
  }

  /**
   * Generate the room layout for the building
   */
  private generateRoomLayout(): void {
    // Start with entrance room
    const entranceRoom = this.unplacedRooms.find(room => room.type === RoomType.ENTRANCE);
    if (!entranceRoom) {
      throw new Error('No entrance room defined in template');
    }

    // Place entrance room near an entrance point
    const entrance = this.building.entrances[0];
    const entranceDimensions = this.calculateRoomDimensions(entranceRoom);
    
    const firstRoom: Room = {
      id: uuidv4(),
      type: entranceRoom.type,
      position: {
        x: entrance.x - Math.floor(entranceDimensions.width / 2),
        y: entrance.y
      },
      dimensions: entranceDimensions,
      connections: []
    };

    this.rooms.push(firstRoom);
    this.unplacedRooms = this.unplacedRooms.filter(room => room.type !== RoomType.ENTRANCE);

    // Place remaining rooms
    while (this.unplacedRooms.length > 0) {
      const nextRoom = this.unplacedRooms[0];
      if (!this.placeRoom(nextRoom)) {
        console.warn(`Could not place room: ${nextRoom.type}`);
        this.unplacedRooms.shift(); // Skip room if it can't be placed
        continue;
      }
      this.unplacedRooms.shift();
    }
  }

  /**
   * Calculate dimensions for a room based on building size and room constraints
   */
  private calculateRoomDimensions(roomLayout: RoomLayout): { width: number; length: number } {
    const maxWidth = Math.min(roomLayout.maxSize.width, this.building.dimensions.width);
    const maxLength = Math.min(roomLayout.maxSize.length, this.building.dimensions.length);
    
    const width = Math.max(
      roomLayout.minSize.width,
      Math.floor(Math.random() * (maxWidth - roomLayout.minSize.width + 1)) + roomLayout.minSize.width
    );
    
    const length = Math.max(
      roomLayout.minSize.length,
      Math.floor(Math.random() * (maxLength - roomLayout.minSize.length + 1)) + roomLayout.minSize.length
    );

    return { width, length };
  }

  /**
   * Attempt to place a room in the building
   */
  private placeRoom(roomLayout: RoomLayout): boolean {
    const dimensions = this.calculateRoomDimensions(roomLayout);
    const requiredConnections = this.findRequiredConnectionRooms(roomLayout);

    // Try different positions based on placement rules
    for (const rule of roomLayout.placementRules) {
      switch (rule.type) {
        case RoomPlacementType.ADJACENT_TO: {
          const targetRoom = this.rooms.find(r => r.type === rule.parameters.roomType);
          if (targetRoom) {
            const position = this.findAdjacentPosition(targetRoom, dimensions);
            if (position && this.isValidPosition(position, dimensions)) {
              const room: Room = {
                id: uuidv4(),
                type: roomLayout.type,
                position,
                dimensions,
                connections: []
              };
              
              // Add connections
              for (const connectedRoom of requiredConnections) {
                if (this.areRoomsAdjacent(room, connectedRoom)) {
                  room.connections.push(connectedRoom);
                  connectedRoom.connections.push(room);
                }
              }

              this.rooms.push(room);
              return true;
            }
          }
          break;
        }
        case RoomPlacementType.NEAR_EDGE: {
          const position = this.findEdgePosition(dimensions);
          if (position && this.isValidPosition(position, dimensions)) {
            const room: Room = {
              id: uuidv4(),
              type: roomLayout.type,
              position,
              dimensions,
              connections: []
            };

            // Add connections
            for (const connectedRoom of requiredConnections) {
              if (this.areRoomsAdjacent(room, connectedRoom)) {
                room.connections.push(connectedRoom);
                connectedRoom.connections.push(room);
              }
            }

            this.rooms.push(room);
            return true;
          }
          break;
        }
        // Add more placement rule handling here
      }
    }

    return false;
  }

  /**
   * Find rooms that this room needs to connect to
   */
  private findRequiredConnectionRooms(roomLayout: RoomLayout): Room[] {
    return this.rooms.filter(room => roomLayout.requiredConnections.includes(room.type));
  }

  /**
   * Find a valid position adjacent to a target room
   */
  private findAdjacentPosition(
    targetRoom: Room,
    dimensions: { width: number; length: number }
  ): { x: number; y: number } | null {
    // Try positions on all sides of the target room
    const positions = [
      // Left
      { x: targetRoom.position.x - dimensions.width - this.MINIMUM_ROOM_SPACING, y: targetRoom.position.y },
      // Right
      { x: targetRoom.position.x + targetRoom.dimensions.width + this.MINIMUM_ROOM_SPACING, y: targetRoom.position.y },
      // Top
      { x: targetRoom.position.x, y: targetRoom.position.y - dimensions.length - this.MINIMUM_ROOM_SPACING },
      // Bottom
      { x: targetRoom.position.x, y: targetRoom.position.y + targetRoom.dimensions.length + this.MINIMUM_ROOM_SPACING }
    ];

    for (const position of positions) {
      if (this.isValidPosition(position, dimensions)) {
        return position;
      }
    }

    return null;
  }

  /**
   * Find a valid position near the building edge
   */
  private findEdgePosition(dimensions: { width: number; length: number }): { x: number; y: number } | null {
    const edges = [
      // Left edge
      { x: 0, y: Math.floor(Math.random() * (this.building.dimensions.length - dimensions.length)) },
      // Right edge
      { x: this.building.dimensions.width - dimensions.width, y: Math.floor(Math.random() * (this.building.dimensions.length - dimensions.length)) },
      // Top edge
      { x: Math.floor(Math.random() * (this.building.dimensions.width - dimensions.width)), y: 0 },
      // Bottom edge
      { x: Math.floor(Math.random() * (this.building.dimensions.width - dimensions.width)), y: this.building.dimensions.length - dimensions.length }
    ];

    for (const position of edges) {
      if (this.isValidPosition(position, dimensions)) {
        return position;
      }
    }

    return null;
  }

  /**
   * Check if a position is valid for room placement
   */
  private isValidPosition(
    position: { x: number; y: number },
    dimensions: { width: number; length: number }
  ): boolean {
    // Check building boundaries
    if (
      position.x < 0 ||
      position.y < 0 ||
      position.x + dimensions.width > this.building.dimensions.width ||
      position.y + dimensions.length > this.building.dimensions.length
    ) {
      return false;
    }

    // Check overlap with existing rooms (including spacing)
    for (const room of this.rooms) {
      if (this.doRoomsOverlap(
        { position, dimensions },
        { position: room.position, dimensions: room.dimensions },
        this.MINIMUM_ROOM_SPACING
      )) {
        return false;
      }
    }

    return true;
  }

  /**
   * Check if two rooms overlap (including spacing)
   */
  private doRoomsOverlap(
    room1: { position: { x: number; y: number }; dimensions: { width: number; length: number } },
    room2: { position: { x: number; y: number }; dimensions: { width: number; length: number } },
    spacing: number
  ): boolean {
    return !(
      room1.position.x + room1.dimensions.width + spacing <= room2.position.x ||
      room2.position.x + room2.dimensions.width + spacing <= room1.position.x ||
      room1.position.y + room1.dimensions.length + spacing <= room2.position.y ||
      room2.position.y + room2.dimensions.length + spacing <= room1.position.y
    );
  }

  /**
   * Check if two rooms are adjacent and can be connected
   */
  private areRoomsAdjacent(room1: Room, room2: Room): boolean {
    const spacing = this.MINIMUM_ROOM_SPACING;
    
    // Check if rooms share a wall (considering spacing)
    const shareVerticalWall = (
      Math.abs((room1.position.x + room1.dimensions.width) - room2.position.x) <= spacing ||
      Math.abs((room2.position.x + room2.dimensions.width) - room1.position.x) <= spacing
    ) && (
      Math.max(room1.position.y, room2.position.y) <= Math.min(room1.position.y + room1.dimensions.length, room2.position.y + room2.dimensions.length)
    );

    const shareHorizontalWall = (
      Math.abs((room1.position.y + room1.dimensions.length) - room2.position.y) <= spacing ||
      Math.abs((room2.position.y + room2.dimensions.length) - room1.position.y) <= spacing
    ) && (
      Math.max(room1.position.x, room2.position.x) <= Math.min(room1.position.x + room1.dimensions.width, room2.position.x + room2.dimensions.width)
    );

    return shareVerticalWall || shareHorizontalWall;
  }

  /**
   * Place furniture in rooms according to rules
   */
  private placeFurniture(): GeneratedFurniture[] {
    const furniture: GeneratedFurniture[] = [];

    // Process each room
    for (const room of this.rooms) {
      const furnitureRule = this.template.furnitureRules.find(rule => rule.roomType === room.type);
      if (!furnitureRule) continue;

      // Place required furniture first
      for (const requirement of furnitureRule.requiredFurniture) {
        const count = Math.floor(Math.random() * (requirement.maxCount - requirement.minCount + 1)) + requirement.minCount;
        
        for (let i = 0; i < count; i++) {
          const placedFurniture = this.placeSingleFurniture(room, requirement, furniture);
          if (placedFurniture) {
            furniture.push(placedFurniture);
          }
        }
      }

      // Place furniture groupings
      for (const grouping of furnitureRule.groupings) {
        const placedGroup = this.placeFurnitureGroup(room, grouping, furniture);
        furniture.push(...placedGroup);
      }

      // Place optional furniture if space permits
      for (const requirement of furnitureRule.optionalFurniture) {
        const count = Math.floor(Math.random() * (requirement.maxCount - requirement.minCount + 1)) + requirement.minCount;
        
        for (let i = 0; i < count; i++) {
          const placedFurniture = this.placeSingleFurniture(room, requirement, furniture);
          if (placedFurniture) {
            furniture.push(placedFurniture);
          }
        }
      }
    }

    return furniture;
  }

  /**
   * Place a single piece of furniture in a room
   */
  private placeSingleFurniture(
    room: Room,
    requirement: FurniturePlacementRule,
    existingFurniture: GeneratedFurniture[]
  ): GeneratedFurniture | null {
    // Try each placement rule in sequence
    for (const rule of requirement.placementRules) {
      const position = this.findFurniturePosition(room, rule, requirement.type, existingFurniture);
      if (position) {
        return {
          id: uuidv4(),
          type: requirement.type,
          position,
          rotation: this.calculateFurnitureRotation(rule.type, position, room),
          roomId: room.id
        };
      }
    }

    return null;
  }

  /**
   * Place a group of furniture pieces together
   */
  private placeFurnitureGroup(
    room: Room,
    grouping: FurnitureGrouping,
    existingFurniture: GeneratedFurniture[]
  ): GeneratedFurniture[] {
    const placedFurniture: GeneratedFurniture[] = [];
    const totalPieces = grouping.furniture.reduce((sum: number, f: { count: number }) => sum + f.count, 0);

    // Find a suitable position for the group center
    const groupCenter = this.findGroupCenter(room, totalPieces, grouping.spacing, existingFurniture);
    if (!groupCenter) return placedFurniture;

    switch (grouping.arrangement) {
      case GroupArrangement.GRID: {
        let row = 0;
        let col = 0;
        const maxCols = Math.ceil(Math.sqrt(totalPieces));

        for (const furnitureType of grouping.furniture) {
          for (let i = 0; i < furnitureType.count; i++) {
            const position = {
              x: groupCenter.x + col * (1 + grouping.spacing),
              y: groupCenter.y + row * (1 + grouping.spacing)
            };

            if (this.isValidFurniturePosition(position, room, existingFurniture)) {
              placedFurniture.push({
                id: uuidv4(),
                type: furnitureType.type,
                position,
                rotation: 0,
                roomId: room.id
              });
            }

            col++;
            if (col >= maxCols) {
              col = 0;
              row++;
            }
          }
        }
        break;
      }

      case GroupArrangement.CIRCLE: {
        let angle = 0;
        const angleStep = (2 * Math.PI) / totalPieces;
        const radius = grouping.spacing;

        for (const furnitureType of grouping.furniture) {
          for (let i = 0; i < furnitureType.count; i++) {
            const position = {
              x: groupCenter.x + Math.cos(angle) * radius,
              y: groupCenter.y + Math.sin(angle) * radius
            };

            if (this.isValidFurniturePosition(position, room, existingFurniture)) {
              placedFurniture.push({
                id: uuidv4(),
                type: furnitureType.type,
                position,
                rotation: angle * (180 / Math.PI),
                roomId: room.id
              });
            }

            angle += angleStep;
          }
        }
        break;
      }

      case GroupArrangement.LINE: {
        let offset = 0;
        for (const furnitureType of grouping.furniture) {
          for (let i = 0; i < furnitureType.count; i++) {
            const position = {
              x: groupCenter.x + offset,
              y: groupCenter.y
            };

            if (this.isValidFurniturePosition(position, room, existingFurniture)) {
              placedFurniture.push({
                id: uuidv4(),
                type: furnitureType.type,
                position,
                rotation: 0,
                roomId: room.id
              });
            }

            offset += 1 + grouping.spacing;
          }
        }
        break;
      }

      case GroupArrangement.CLUSTER: {
        // Random cluster within spacing constraints
        for (const furnitureType of grouping.furniture) {
          for (let i = 0; i < furnitureType.count; i++) {
            const angle = Math.random() * 2 * Math.PI;
            const distance = Math.random() * grouping.spacing;
            const position = {
              x: groupCenter.x + Math.cos(angle) * distance,
              y: groupCenter.y + Math.sin(angle) * distance
            };

            if (this.isValidFurniturePosition(position, room, existingFurniture)) {
              placedFurniture.push({
                id: uuidv4(),
                type: furnitureType.type,
                position,
                rotation: Math.random() * 360,
                roomId: room.id
              });
            }
          }
        }
        break;
      }
    }

    return placedFurniture;
  }

  /**
   * Find a valid position for furniture based on placement rules
   */
  private findFurniturePosition(
    room: Room,
    rule: { type: FurniturePlacementType; parameters: Record<string, any> },
    furnitureType: string,
    existingFurniture: GeneratedFurniture[]
  ): { x: number; y: number } | null {
    switch (rule.type) {
      case FurniturePlacementType.AGAINST_WALL: {
        // Try positions along each wall
        const wallPositions = [
          // Left wall
          { x: room.position.x, y: room.position.y + 1 },
          // Right wall
          { x: room.position.x + room.dimensions.width - 1, y: room.position.y + 1 },
          // Top wall
          { x: room.position.x + 1, y: room.position.y },
          // Bottom wall
          { x: room.position.x + 1, y: room.position.y + room.dimensions.length - 1 }
        ];

        for (const position of wallPositions) {
          if (this.isValidFurniturePosition(position, room, existingFurniture)) {
            return position;
          }
        }
        break;
      }

      case FurniturePlacementType.CENTER: {
        const center = {
          x: room.position.x + Math.floor(room.dimensions.width / 2),
          y: room.position.y + Math.floor(room.dimensions.length / 2)
        };

        if (this.isValidFurniturePosition(center, room, existingFurniture)) {
          return center;
        }
        break;
      }

      case FurniturePlacementType.NEAR_FURNITURE: {
        const targetFurniture = existingFurniture.find(f => 
          f.roomId === room.id && f.type === rule.parameters.furnitureType
        );

        if (targetFurniture) {
          // Try positions around the target furniture
          const nearbyPositions = [
            { x: targetFurniture.position.x + 1, y: targetFurniture.position.y },
            { x: targetFurniture.position.x - 1, y: targetFurniture.position.y },
            { x: targetFurniture.position.x, y: targetFurniture.position.y + 1 },
            { x: targetFurniture.position.x, y: targetFurniture.position.y - 1 }
          ];

          for (const position of nearbyPositions) {
            if (this.isValidFurniturePosition(position, room, existingFurniture)) {
              return position;
            }
          }
        }
        break;
      }

      case FurniturePlacementType.CORNER: {
        // Try each corner
        const corners = [
          { x: room.position.x, y: room.position.y },
          { x: room.position.x + room.dimensions.width - 1, y: room.position.y },
          { x: room.position.x, y: room.position.y + room.dimensions.length - 1 },
          { x: room.position.x + room.dimensions.width - 1, y: room.position.y + room.dimensions.length - 1 }
        ];

        for (const position of corners) {
          if (this.isValidFurniturePosition(position, room, existingFurniture)) {
            return position;
          }
        }
        break;
      }

      case FurniturePlacementType.RANDOM: {
        // Try random positions until we find a valid one or give up
        for (let attempts = 0; attempts < 10; attempts++) {
          const position = {
            x: room.position.x + Math.floor(Math.random() * (room.dimensions.width - 1)),
            y: room.position.y + Math.floor(Math.random() * (room.dimensions.length - 1))
          };

          if (this.isValidFurniturePosition(position, room, existingFurniture)) {
            return position;
          }
        }
        break;
      }
    }

    return null;
  }

  /**
   * Find a suitable center position for a furniture group
   */
  private findGroupCenter(
    room: Room,
    groupSize: number,
    spacing: number,
    existingFurniture: GeneratedFurniture[]
  ): { x: number; y: number } | null {
    // Calculate required space for the group
    const requiredSpace = Math.ceil(Math.sqrt(groupSize)) * (1 + spacing);

    // Try to find a position that can accommodate the group
    for (let y = room.position.y + requiredSpace; y < room.position.y + room.dimensions.length - requiredSpace; y++) {
      for (let x = room.position.x + requiredSpace; x < room.position.x + room.dimensions.width - requiredSpace; x++) {
        const position = { x, y };
        if (this.isValidFurniturePosition(position, room, existingFurniture)) {
          return position;
        }
      }
    }

    return null;
  }

  /**
   * Check if a position is valid for furniture placement
   */
  private isValidFurniturePosition(
    position: { x: number; y: number },
    room: Room,
    existingFurniture: GeneratedFurniture[],
    clearance = 1
  ): boolean {
    // Check room boundaries
    if (
      position.x < room.position.x ||
      position.y < room.position.y ||
      position.x >= room.position.x + room.dimensions.width ||
      position.y >= room.position.y + room.dimensions.length
    ) {
      return false;
    }

    // Check spacing from other furniture
    for (const furniture of existingFurniture.filter(f => f.roomId === room.id)) {
      const distance = Math.sqrt(
        Math.pow(position.x - furniture.position.x, 2) +
        Math.pow(position.y - furniture.position.y, 2)
      );
      if (distance < clearance) {
        return false;
      }
    }

    return true;
  }

  /**
   * Calculate rotation for furniture based on placement type
   */
  private calculateFurnitureRotation(
    placementType: FurniturePlacementType,
    position: { x: number; y: number },
    room: Room
  ): number {
    switch (placementType) {
      case FurniturePlacementType.AGAINST_WALL:
        // Rotate to face away from the wall
        if (position.x === room.position.x) return 0; // Left wall
        if (position.x === room.position.x + room.dimensions.width - 1) return 180; // Right wall
        if (position.y === room.position.y) return 90; // Top wall
        if (position.y === room.position.y + room.dimensions.length - 1) return 270; // Bottom wall
        break;

      case FurniturePlacementType.CORNER:
        // Rotate to face the room center
        const centerX = room.position.x + Math.floor(room.dimensions.width / 2);
        const centerY = room.position.y + Math.floor(room.dimensions.length / 2);
        return Math.atan2(centerY - position.y, centerX - position.x) * (180 / Math.PI);

      case FurniturePlacementType.RANDOM:
        return Math.random() * 360;

      default:
        return 0;
    }

    return 0;
  }

  /**
   * Place decorations according to decoration schemes
   */
  private placeDecorations(): GeneratedDecoration[] {
    const decorations: GeneratedDecoration[] = [];

    // Process each room
    for (const room of this.rooms) {
      const scheme = this.template.decorationSchemes.find(s => s.roomType === room.type);
      if (!scheme) continue;

      // Calculate number of decorations based on room size and density
      const roomArea = room.dimensions.width * room.dimensions.length;
      const maxDecorations = Math.floor(roomArea * scheme.density);

      // Place each type of decoration
      for (const decorationRule of scheme.decorations) {
        const count = Math.min(
          maxDecorations,
          Math.floor(Math.random() * (decorationRule.maxCount - decorationRule.minCount + 1)) + decorationRule.minCount
        );

        for (let i = 0; i < count; i++) {
          const placedDecoration = this.placeSingleDecoration(room, decorationRule, decorations, scheme);
          if (placedDecoration) {
            decorations.push(placedDecoration);
          }
        }
      }
    }

    return decorations;
  }

  /**
   * Place a single decoration in a room
   */
  private placeSingleDecoration(
    room: Room,
    rule: DecorationRule,
    existingDecorations: GeneratedDecoration[],
    scheme: DecorationScheme
  ): GeneratedDecoration | null {
    // Try each placement rule in sequence
    for (const placementRule of rule.placementRules) {
      const position = this.findDecorationPosition(room, placementRule, rule.type, existingDecorations);
      if (position) {
        return {
          id: uuidv4(),
          type: rule.type,
          position,
          rotation: this.calculateDecorationRotation(placementRule.type, position, room),
          roomId: room.id
        };
      }
    }

    return null;
  }

  /**
   * Find a valid position for a decoration based on placement rules
   */
  private findDecorationPosition(
    room: Room,
    rule: { type: DecorationPlacementType; parameters: Record<string, any> },
    decorationType: string,
    existingDecorations: GeneratedDecoration[]
  ): { x: number; y: number } | null {
    switch (rule.type) {
      case DecorationPlacementType.ON_WALL: {
        // Try positions along each wall
        const wallPositions = [
          // Left wall
          { x: room.position.x, y: room.position.y + 1 },
          // Right wall
          { x: room.position.x + room.dimensions.width - 1, y: room.position.y + 1 },
          // Top wall
          { x: room.position.x + 1, y: room.position.y },
          // Bottom wall
          { x: room.position.x + 1, y: room.position.y + room.dimensions.length - 1 }
        ];

        // Shuffle wall positions for variety
        for (let i = wallPositions.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [wallPositions[i], wallPositions[j]] = [wallPositions[j], wallPositions[i]];
        }

        for (const position of wallPositions) {
          if (this.isValidDecorationPosition(position, room, existingDecorations)) {
            return position;
          }
        }
        break;
      }

      case DecorationPlacementType.ON_FLOOR: {
        // Try random floor positions
        for (let attempts = 0; attempts < 10; attempts++) {
          const position = {
            x: room.position.x + Math.floor(Math.random() * (room.dimensions.width - 2)) + 1,
            y: room.position.y + Math.floor(Math.random() * (room.dimensions.length - 2)) + 1
          };

          if (this.isValidDecorationPosition(position, room, existingDecorations)) {
            return position;
          }
        }
        break;
      }

      case DecorationPlacementType.ON_CEILING: {
        // Similar to floor placement, but will be rendered differently
        for (let attempts = 0; attempts < 10; attempts++) {
          const position = {
            x: room.position.x + Math.floor(Math.random() * (room.dimensions.width - 2)) + 1,
            y: room.position.y + Math.floor(Math.random() * (room.dimensions.length - 2)) + 1
          };

          if (this.isValidDecorationPosition(position, room, existingDecorations)) {
            return position;
          }
        }
        break;
      }

      case DecorationPlacementType.ON_FURNITURE: {
        // Find furniture in the room and try to place decoration on it
        const roomFurniture = this.rooms
          .find(r => r.id === room.id)?.furniture
          .filter(f => this.isValidFurnitureForDecoration(f.type));

        if (roomFurniture && roomFurniture.length > 0) {
          const randomFurniture = roomFurniture[Math.floor(Math.random() * roomFurniture.length)];
          const position = {
            x: randomFurniture.position.x,
            y: randomFurniture.position.y
          };

          if (this.isValidDecorationPosition(position, room, existingDecorations)) {
            return position;
          }
        }
        break;
      }
    }

    return null;
  }

  /**
   * Check if a position is valid for decoration placement
   */
  private isValidDecorationPosition(
    position: { x: number; y: number },
    room: Room,
    existingDecorations: GeneratedDecoration[],
    minSpacing = 1
  ): boolean {
    // Check room boundaries
    if (
      position.x < room.position.x ||
      position.y < room.position.y ||
      position.x >= room.position.x + room.dimensions.width ||
      position.y >= room.position.y + room.dimensions.length
    ) {
      return false;
    }

    // Check spacing from other decorations
    for (const decoration of existingDecorations.filter(d => d.roomId === room.id)) {
      const distance = Math.sqrt(
        Math.pow(position.x - decoration.position.x, 2) +
        Math.pow(position.y - decoration.position.y, 2)
      );
      if (distance < minSpacing) {
        return false;
      }
    }

    return true;
  }

  /**
   * Calculate rotation for decoration based on placement type
   */
  private calculateDecorationRotation(
    placementType: DecorationPlacementType,
    position: { x: number; y: number },
    room: Room
  ): number {
    switch (placementType) {
      case DecorationPlacementType.ON_WALL:
        // Rotate to face into the room
        if (position.x === room.position.x) return 90; // Left wall
        if (position.x === room.position.x + room.dimensions.width - 1) return 270; // Right wall
        if (position.y === room.position.y) return 180; // Top wall
        if (position.y === room.position.y + room.dimensions.length - 1) return 0; // Bottom wall
        break;

      case DecorationPlacementType.ON_FLOOR:
      case DecorationPlacementType.ON_CEILING:
        // Random rotation for floor/ceiling decorations
        return Math.random() * 360;

      case DecorationPlacementType.ON_FURNITURE:
        // Face the center of the room
        const centerX = room.position.x + Math.floor(room.dimensions.width / 2);
        const centerY = room.position.y + Math.floor(room.dimensions.length / 2);
        return Math.atan2(centerY - position.y, centerX - position.x) * (180 / Math.PI);
    }

    return 0;
  }

  /**
   * Check if a furniture type is suitable for placing decorations on
   */
  private isValidFurnitureForDecoration(furnitureType: string): boolean {
    // List of furniture types that can hold decorations
    const validTypes = [
      FurnitureType.TABLE,
      FurnitureType.SHELF,
      FurnitureType.COUNTER,
      FurnitureType.DISPLAY_CASE
    ];

    return validTypes.includes(furnitureType as FurnitureType);
  }

  /**
   * Define NPC zones in rooms
   */
  private defineNPCZones(): GeneratedNPCZone[] {
    // TODO: Implement NPC zone definition
    return [];
  }

  /**
   * Place interactive objects in rooms
   */
  private placeInteractiveObjects(): GeneratedInteractiveObject[] {
    // TODO: Implement interactive object placement
    return [];
  }
} 