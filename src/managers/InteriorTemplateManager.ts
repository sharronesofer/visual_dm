import { v4 as uuidv4 } from 'uuid';
import {
  InteriorTemplate,
  RoomLayout,
  FurnitureRule,
  DecorationScheme,
  NPCZoneDefinition,
  InteractiveObjectRule,
  RoomType
} from '../types/interiors/template';
import { BuildingType, POICategory } from '../types/buildings/base';

export class InteriorTemplateManager {
  private templates: Map<string, InteriorTemplate>;

  constructor() {
    this.templates = new Map();
  }

  /**
   * Create a new interior template
   */
  createTemplate(params: {
    name: string;
    buildingType: BuildingType;
    category: POICategory;
    roomLayouts: RoomLayout[];
    furnitureRules: FurnitureRule[];
    decorationSchemes: DecorationScheme[];
    npcZones: NPCZoneDefinition[];
    interactiveObjects: InteractiveObjectRule[];
  }): InteriorTemplate {
    const template: InteriorTemplate = {
      id: uuidv4(),
      ...params
    };

    this.validateTemplate(template);
    this.templates.set(template.id, template);
    return template;
  }

  /**
   * Get a template for a specific building type
   */
  getTemplateForBuilding(buildingType: BuildingType): InteriorTemplate | undefined {
    return Array.from(this.templates.values()).find(
      template => template.buildingType === buildingType
    );
  }

  /**
   * Get a template by ID
   */
  getTemplate(id: string): InteriorTemplate | undefined {
    return this.templates.get(id);
  }

  /**
   * Get templates by building type
   */
  getTemplatesByBuildingType(buildingType: BuildingType): InteriorTemplate[] {
    return Array.from(this.templates.values())
      .filter(template => template.buildingType === buildingType);
  }

  /**
   * Get templates by category
   */
  getTemplatesByCategory(category: POICategory): InteriorTemplate[] {
    return Array.from(this.templates.values())
      .filter(template => template.category === category);
  }

  /**
   * Update an existing template
   */
  updateTemplate(id: string, updates: Partial<Omit<InteriorTemplate, 'id'>>): InteriorTemplate {
    const template = this.templates.get(id);
    if (!template) {
      throw new Error(`Template with ID ${id} not found`);
    }

    const updatedTemplate: InteriorTemplate = {
      ...template,
      ...updates
    };

    this.validateTemplate(updatedTemplate);
    this.templates.set(id, updatedTemplate);
    return updatedTemplate;
  }

  /**
   * Delete a template
   */
  deleteTemplate(id: string): boolean {
    return this.templates.delete(id);
  }

  /**
   * Validate a template's structure and rules
   */
  private validateTemplate(template: InteriorTemplate): void {
    // Validate basic structure
    if (!template.id || !template.name || !template.buildingType || !template.category) {
      throw new Error('Template missing required fields');
    }

    // Validate room layouts
    if (!template.roomLayouts.length) {
      throw new Error('Template must have at least one room layout');
    }

    // Ensure entrance exists
    const hasEntrance = template.roomLayouts.some(room => room.type === RoomType.ENTRANCE);
    if (!hasEntrance) {
      throw new Error('Template must have an entrance room');
    }

    // Validate room connections
    this.validateRoomConnections(template.roomLayouts);

    // Validate furniture rules
    this.validateFurnitureRules(template.roomLayouts, template.furnitureRules);

    // Validate decoration schemes
    this.validateDecorationSchemes(template.roomLayouts, template.decorationSchemes);

    // Validate NPC zones
    this.validateNPCZones(template.roomLayouts, template.npcZones);

    // Validate interactive objects
    this.validateInteractiveObjects(template.roomLayouts, template.interactiveObjects);
  }

  /**
   * Validate room connections
   */
  private validateRoomConnections(roomLayouts: RoomLayout[]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type));

    for (const room of roomLayouts) {
      // Check required connections
      for (const requiredRoom of room.requiredConnections) {
        if (!roomTypes.has(requiredRoom)) {
          throw new Error(`Room ${room.type} requires connection to non-existent room type ${requiredRoom}`);
        }
      }

      // Check optional connections
      for (const optionalRoom of room.optionalConnections) {
        if (!roomTypes.has(optionalRoom)) {
          throw new Error(`Room ${room.type} has optional connection to non-existent room type ${optionalRoom}`);
        }
      }
    }
  }

  /**
   * Validate furniture rules
   */
  private validateFurnitureRules(roomLayouts: RoomLayout[], furnitureRules: FurnitureRule[]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type));

    for (const rule of furnitureRules) {
      if (!roomTypes.has(rule.roomType)) {
        throw new Error(`Furniture rule references non-existent room type ${rule.roomType}`);
      }

      // Validate furniture requirements
      for (const req of rule.requiredFurniture) {
        if (req.minCount < 0 || req.maxCount < req.minCount) {
          throw new Error(`Invalid furniture count range for ${req.type} in room ${rule.roomType}`);
        }
      }
    }
  }

  /**
   * Validate decoration schemes
   */
  private validateDecorationSchemes(roomLayouts: RoomLayout[], schemes: DecorationScheme[]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type));

    for (const scheme of schemes) {
      if (!roomTypes.has(scheme.roomType)) {
        throw new Error(`Decoration scheme references non-existent room type ${scheme.roomType}`);
      }

      if (scheme.density < 0 || scheme.density > 1) {
        throw new Error(`Invalid decoration density for room ${scheme.roomType}`);
      }
    }
  }

  /**
   * Validate NPC zones
   */
  private validateNPCZones(roomLayouts: RoomLayout[], zones: NPCZoneDefinition[]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type));

    for (const zone of zones) {
      if (!roomTypes.has(zone.roomType)) {
        throw new Error(`NPC zone references non-existent room type ${zone.roomType}`);
      }

      if (zone.capacity < 0) {
        throw new Error(`Invalid NPC capacity for zone in room ${zone.roomType}`);
      }
    }
  }

  /**
   * Validate interactive objects
   */
  private validateInteractiveObjects(roomLayouts: RoomLayout[], objects: InteractiveObjectRule[]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type));

    for (const object of objects) {
      if (!roomTypes.has(object.roomType)) {
        throw new Error(`Interactive object rule references non-existent room type ${object.roomType}`);
      }

      if (object.count < 0) {
        throw new Error(`Invalid object count for ${object.objectType} in room ${object.roomType}`);
      }

      if (object.requiredSpace < 0) {
        throw new Error(`Invalid required space for ${object.objectType} in room ${object.roomType}`);
      }
    }
  }
} 