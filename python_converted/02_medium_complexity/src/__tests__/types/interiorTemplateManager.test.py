from typing import Any, Dict



describe('InteriorTemplateManager', () => {
  let manager: InteriorTemplateManager
  let baseRoom: RoomLayout
  let baseFurniture: FurnitureRule
  let baseDecoration: DecorationScheme
  let baseNPCZone: NPCZoneDefinition
  let baseInteractive: InteractiveObjectRule
  beforeEach(() => {
    manager = new InteriorTemplateManager()
    baseRoom = {
      id: 'room1',
      name: 'Entrance',
      type: RoomType.ENTRANCE,
      minSize: Dict[str, Any],
      maxSize: Dict[str, Any],
      requiredConnections: [],
      optionalConnections: [],
      priority: 1,
      placementRules: []
    }
    baseFurniture = {
      roomType: RoomType.ENTRANCE,
      requiredFurniture: [],
      optionalFurniture: [],
      groupings: [],
      spacingRules: []
    }
    baseDecoration = {
      roomType: RoomType.ENTRANCE,
      theme: 'Classic',
      decorations: [],
      colorPalette: ['#fff'],
      density: 0.5
    }
    baseNPCZone = {
      roomType: RoomType.ENTRANCE,
      zoneType: 'SERVICE',
      capacity: 1,
      requiredFurniture: [],
      activityType: []
    } as any
    baseInteractive = {
      roomType: RoomType.ENTRANCE,
      objectType: 'DOOR',
      count: 1,
      placementRules: [],
      requiredSpace: 1
    } as any
  })
  it('validates a correct template', () => {
    expect(() => manager.createTemplate({
      name: 'Valid',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).not.toThrow()
  })
  it('throws if missing entrance room', () => {
    const room = { ...baseRoom, type: RoomType.BEDROOM }
    expect(() => manager.createTemplate({
      name: 'No Entrance',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [room],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/entrance/)
  })
  it('throws if required connection is invalid', () => {
    const room = { ...baseRoom, requiredConnections: [RoomType.KITCHEN] }
    expect(() => manager.createTemplate({
      name: 'Bad Conn',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [room],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/connection/)
  })
  it('throws if furniture rule references non-existent room', () => {
    const badFurniture = { ...baseFurniture, roomType: RoomType.KITCHEN }
    expect(() => manager.createTemplate({
      name: 'Bad Furniture',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [badFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/furniture rule/)
  })
  it('throws if furniture count is invalid', () => {
    const badFurniture = {
      ...baseFurniture,
      requiredFurniture: [{ type: 'BED', minCount: 2, maxCount: 1, placementRules: [] }]
    }
    expect(() => manager.createTemplate({
      name: 'Bad Furniture Count',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [badFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/furniture count/)
  })
  it('throws if decoration scheme references non-existent room', () => {
    const badDecoration = { ...baseDecoration, roomType: RoomType.KITCHEN }
    expect(() => manager.createTemplate({
      name: 'Bad Decoration',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [badDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/decoration scheme/)
  })
  it('throws if decoration density is invalid', () => {
    const badDecoration = { ...baseDecoration, density: 2 }
    expect(() => manager.createTemplate({
      name: 'Bad Density',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [badDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })).toThrow(/decoration density/)
  })
  it('can update and version a template', () => {
    const template = manager.createTemplate({
      name: 'To Update',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })
    const updated = manager.updateTemplate(template.id, { name: 'Updated' })
    expect(updated.name).toBe('Updated')
    expect(manager.getTemplate(template.id)?.name).toBe('Updated')
  })
  it('can delete a template', () => {
    const template = manager.createTemplate({
      name: 'To Delete',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })
    expect(manager.deleteTemplate(template.id)).toBe(true)
    expect(manager.getTemplate(template.id)).toBeUndefined()
  })
  it('can serialize and deserialize templates', () => {
    const template = manager.createTemplate({
      name: 'To Export',
      buildingType: BuildingType.INN,
      category: POICategory.SOCIAL,
      roomLayouts: [baseRoom],
      furnitureRules: [baseFurniture],
      decorationSchemes: [baseDecoration],
      npcZones: [baseNPCZone],
      interactiveObjects: [baseInteractive]
    })
    const json = JSON.stringify(template)
    const parsed: InteriorTemplate = JSON.parse(json)
    expect(parsed.name).toBe('To Export')
    expect(() => manager['validateTemplate'](parsed)).not.toThrow()
  })
}) 