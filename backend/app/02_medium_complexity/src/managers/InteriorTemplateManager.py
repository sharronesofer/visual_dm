from typing import Any, Dict, List



  InteriorTemplate,
  RoomLayout,
  FurnitureRule,
  DecorationScheme,
  NPCZoneDefinition,
  InteractiveObjectRule,
  RoomType
} from '../types/interiors/template'
class InteriorTemplateManager {
  private templates: Map<string, InteriorTemplate>
  constructor() {
    this.templates = new Map()
  }
  /**
   * Create a new interior template
   */
  createTemplate(params: Dict[str, Any]): InteriorTemplate {
    const template: InteriorTemplate = {
      id: uuidv4(),
      ...params
    }
    this.validateTemplate(template)
    this.templates.set(template.id, template)
    return template
  }
  /**
   * Get a template for a specific building type
   */
  getTemplateForBuilding(buildingType: BuildingType): InteriorTemplate | undefined {
    return Array.from(this.templates.values()).find(
      template => template.buildingType === buildingType
    )
  }
  /**
   * Get a template by ID
   */
  getTemplate(id: str): InteriorTemplate | undefined {
    return this.templates.get(id)
  }
  /**
   * Get templates by building type
   */
  getTemplatesByBuildingType(buildingType: BuildingType): InteriorTemplate[] {
    return Array.from(this.templates.values())
      .filter(template => template.buildingType === buildingType)
  }
  /**
   * Get templates by category
   */
  getTemplatesByCategory(category: POICategory): InteriorTemplate[] {
    return Array.from(this.templates.values())
      .filter(template => template.category === category)
  }
  /**
   * Update an existing template
   */
  updateTemplate(id: str, updates: Partial<Omit<InteriorTemplate, 'id'>>): InteriorTemplate {
    const template = this.templates.get(id)
    if (!template) {
      throw new Error(`Template with ID ${id} not found`)
    }
    const updatedTemplate: InteriorTemplate = {
      ...template,
      ...updates
    }
    this.validateTemplate(updatedTemplate)
    this.templates.set(id, updatedTemplate)
    return updatedTemplate
  }
  /**
   * Delete a template
   */
  deleteTemplate(id: str): bool {
    return this.templates.delete(id)
  }
  /**
   * Validate a template's structure and rules
   */
  private validateTemplate(template: InteriorTemplate): void {
    if (!template.id || !template.name || !template.buildingType || !template.category) {
      throw new Error('Template missing required fields')
    }
    if (!template.roomLayouts.length) {
      throw new Error('Template must have at least one room layout')
    }
    const hasEntrance = template.roomLayouts.some(room => room.type === RoomType.ENTRANCE)
    if (!hasEntrance) {
      throw new Error('Template must have an entrance room')
    }
    this.validateRoomConnections(template.roomLayouts)
    this.validateFurnitureRules(template.roomLayouts, template.furnitureRules)
    this.validateDecorationSchemes(template.roomLayouts, template.decorationSchemes)
    this.validateNPCZones(template.roomLayouts, template.npcZones)
    this.validateInteractiveObjects(template.roomLayouts, template.interactiveObjects)
  }
  /**
   * Validate room connections
   */
  private validateRoomConnections(roomLayouts: List[RoomLayout]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type))
    for (const room of roomLayouts) {
      for (const requiredRoom of room.requiredConnections) {
        if (!roomTypes.has(requiredRoom)) {
          throw new Error(`Room ${room.type} requires connection to non-existent room type ${requiredRoom}`)
        }
      }
      for (const optionalRoom of room.optionalConnections) {
        if (!roomTypes.has(optionalRoom)) {
          throw new Error(`Room ${room.type} has optional connection to non-existent room type ${optionalRoom}`)
        }
      }
    }
  }
  /**
   * Validate furniture rules
   */
  private validateFurnitureRules(roomLayouts: List[RoomLayout], furnitureRules: List[FurnitureRule]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type))
    for (const rule of furnitureRules) {
      if (!roomTypes.has(rule.roomType)) {
        throw new Error(`Furniture rule references non-existent room type ${rule.roomType}`)
      }
      for (const req of rule.requiredFurniture) {
        if (req.minCount < 0 || req.maxCount < req.minCount) {
          throw new Error(`Invalid furniture count range for ${req.type} in room ${rule.roomType}`)
        }
      }
    }
  }
  /**
   * Validate decoration schemes
   */
  private validateDecorationSchemes(roomLayouts: List[RoomLayout], schemes: List[DecorationScheme]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type))
    for (const scheme of schemes) {
      if (!roomTypes.has(scheme.roomType)) {
        throw new Error(`Decoration scheme references non-existent room type ${scheme.roomType}`)
      }
      if (scheme.density < 0 || scheme.density > 1) {
        throw new Error(`Invalid decoration density for room ${scheme.roomType}`)
      }
    }
  }
  /**
   * Validate NPC zones
   */
  private validateNPCZones(roomLayouts: List[RoomLayout], zones: List[NPCZoneDefinition]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type))
    for (const zone of zones) {
      if (!roomTypes.has(zone.roomType)) {
        throw new Error(`NPC zone references non-existent room type ${zone.roomType}`)
      }
      if (zone.capacity < 0) {
        throw new Error(`Invalid NPC capacity for zone in room ${zone.roomType}`)
      }
    }
  }
  /**
   * Validate interactive objects
   */
  private validateInteractiveObjects(roomLayouts: List[RoomLayout], objects: List[InteractiveObjectRule]): void {
    const roomTypes = new Set(roomLayouts.map(room => room.type))
    for (const object of objects) {
      if (!roomTypes.has(object.roomType)) {
        throw new Error(`Interactive object rule references non-existent room type ${object.roomType}`)
      }
      if (object.count < 0) {
        throw new Error(`Invalid object count for ${object.objectType} in room ${object.roomType}`)
      }
      if (object.requiredSpace < 0) {
        throw new Error(`Invalid required space for ${object.objectType} in room ${object.roomType}`)
      }
    }
  }
} 