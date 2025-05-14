from typing import Any


function createBuildingBase(props: Partial<BuildingBase>): BuildingBase {
  const building: BuildingBase = {
    id: props.id || uuidv4(),
    name: props.name || '',
    type: props.type || BuildingType.INN,
    category: props.category || POICategory.SOCIAL,
    dimensions: props.dimensions || { width: 1, height: 1 },
    entrances: props.entrances || [{ x: 0, y: 0 }],
    tags: props.tags || [],
    minDangerLevel: props.minDangerLevel || 1,
    maxDangerLevel: props.maxDangerLevel || 1
  }
  const validation = validateBuildingBase(building)
  if (!validation.isValid) {
    throw new Error(`Invalid building base: ${validation.errors.join(', ')}`)
  }
  return building
}
function createInn(props: Partial<Inn>): Inn {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.INN,
    category: POICategory.SOCIAL
  })
  const inn = {
    ...baseBuilding,
    type: BuildingType.INN as const,
    category: POICategory.SOCIAL as const,
    npcCapacity: props.npcCapacity || 10,
    openingHours: props.openingHours || { start: 6, end: 22 },
    services: props.services || [SocialService.LODGING],
    roomCount: props.roomCount || 5,
    roomTypes: props.roomTypes || [RoomType.BASIC]
  } as Inn
  const validation = validateSocialBuilding(inn)
  if (!validation.isValid) {
    throw new Error(`Invalid inn: ${validation.errors.join(', ')}`)
  }
  return inn
}
function createShop(props: Partial<Shop>): Shop {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.SHOP,
    category: POICategory.SOCIAL
  })
  const shop = {
    ...baseBuilding,
    type: BuildingType.SHOP as const,
    category: POICategory.SOCIAL as const,
    npcCapacity: props.npcCapacity || 5,
    openingHours: props.openingHours || { start: 8, end: 18 },
    services: props.services || [SocialService.TRADING],
    shopType: props.shopType || ShopType.GENERAL,
    inventorySize: props.inventorySize || 50
  } as Shop
  const validation = validateSocialBuilding(shop)
  if (!validation.isValid) {
    throw new Error(`Invalid shop: ${validation.errors.join(', ')}`)
  }
  return shop
}
function createTavern(props: Partial<Tavern>): Tavern {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.TAVERN,
    category: POICategory.SOCIAL
  })
  const tavern = {
    ...baseBuilding,
    type: BuildingType.TAVERN as const,
    category: POICategory.SOCIAL as const,
    npcCapacity: props.npcCapacity || 12,
    openingHours: props.openingHours || { start: 10, end: 2 },
    services: props.services || [SocialService.FOOD_DRINK, SocialService.INFORMATION],
    specialties: props.specialties || ['ale', 'stew'],
    entertainmentTypes: props.entertainmentTypes || [EntertainmentType.MUSIC, EntertainmentType.GAMBLING]
  } as Tavern
  const validation = validateSocialBuilding(tavern)
  if (!validation.isValid) {
    throw new Error(`Invalid tavern: ${validation.errors.join(', ')}`)
  }
  return tavern
}
function createGuildHall(props: Partial<GuildHall>): GuildHall {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.GUILD_HALL,
    category: POICategory.SOCIAL
  })
  const guildHall = {
    ...baseBuilding,
    type: BuildingType.GUILD_HALL as const,
    category: POICategory.SOCIAL as const,
    npcCapacity: props.npcCapacity || 8,
    openingHours: props.openingHours || { start: 8, end: 20 },
    services: props.services || [SocialService.FACTION_SERVICES, SocialService.QUEST_GIVING],
    guildType: props.guildType || 'adventurers',
    membershipLevels: props.membershipLevels || ['novice', 'member', 'veteran', 'leader'],
    facilities: props.facilities || ['meeting hall', 'training room']
  } as GuildHall
  const validation = validateSocialBuilding(guildHall)
  if (!validation.isValid) {
    throw new Error(`Invalid guild hall: ${validation.errors.join(', ')}`)
  }
  return guildHall
}
function createNPCHome(props: Partial<NPCHome>): NPCHome {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.NPC_HOME,
    category: POICategory.SOCIAL
  })
  const npcHome = {
    ...baseBuilding,
    type: BuildingType.NPC_HOME as const,
    category: POICategory.SOCIAL as const,
    npcCapacity: props.npcCapacity || 4,
    openingHours: props.openingHours || { start: 0, end: 24 },
    services: props.services || [],
    residentCount: props.residentCount || 3,
    socialStatus: props.socialStatus || SocialStatus.MODEST
  } as NPCHome
  const validation = validateSocialBuilding(npcHome)
  if (!validation.isValid) {
    throw new Error(`Invalid NPC home: ${validation.errors.join(', ')}`)
  }
  return npcHome
}
function createEnemyLair(props: Partial<EnemyLair>): EnemyLair {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.ENEMY_LAIR,
    category: POICategory.DUNGEON
  })
  const lair = {
    ...baseBuilding,
    type: BuildingType.ENEMY_LAIR as const,
    category: POICategory.DUNGEON as const,
    difficulty: props.difficulty || DifficultyRating.MEDIUM,
    requiredLevel: props.requiredLevel || 1,
    rewards: props.rewards || [RewardType.EXPERIENCE],
    enemyTypes: props.enemyTypes || [],
    enemyCount: props.enemyCount || 1,
    bossPresent: props.bossPresent || false
  } as EnemyLair
  const validation = validateDungeonStructure(lair)
  if (!validation.isValid) {
    throw new Error(`Invalid enemy lair: ${validation.errors.join(', ')}`)
  }
  return lair
}
function createPuzzleRoom(props: Partial<PuzzleRoom>): PuzzleRoom {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.PUZZLE_ROOM,
    category: POICategory.DUNGEON
  })
  const room = {
    ...baseBuilding,
    type: BuildingType.PUZZLE_ROOM as const,
    category: POICategory.DUNGEON as const,
    difficulty: props.difficulty || DifficultyRating.MEDIUM,
    requiredLevel: props.requiredLevel || 1,
    rewards: props.rewards || [RewardType.EXPERIENCE],
    puzzleType: props.puzzleType || PuzzleType.RIDDLE,
    solutionSteps: props.solutionSteps || 1,
    timeLimit: props.timeLimit
  } as PuzzleRoom
  const validation = validateDungeonStructure(room)
  if (!validation.isValid) {
    throw new Error(`Invalid puzzle room: ${validation.errors.join(', ')}`)
  }
  return room
}
function createRuins(props: Partial<Ruins>): Ruins {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.RUINS,
    category: POICategory.EXPLORATION
  })
  const ruins = {
    ...baseBuilding,
    type: BuildingType.RUINS as const,
    category: POICategory.EXPLORATION as const,
    discoveryDC: props.discoveryDC || 10,
    interactionType: props.interactionType || [InteractionType.INVESTIGATE],
    seasonalAvailability: props.seasonalAvailability || Object.values(Season),
    civilization: props.civilization || 'Unknown',
    age: props.age || 1000,
    preservationState: props.preservationState || PreservationState.WEATHERED,
    artifactTypes: props.artifactTypes || [ArtifactType.POTTERY]
  } as Ruins
  const validation = validateExplorationFeature(ruins)
  if (!validation.isValid) {
    throw new Error(`Invalid ruins: ${validation.errors.join(', ')}`)
  }
  return ruins
}
function createResourceNode(props: Partial<ResourceNode>): ResourceNode {
  const baseBuilding = createBuildingBase({
    ...props,
    type: BuildingType.RESOURCE_NODE,
    category: POICategory.EXPLORATION
  })
  const node = {
    ...baseBuilding,
    type: BuildingType.RESOURCE_NODE as const,
    category: POICategory.EXPLORATION as const,
    discoveryDC: props.discoveryDC || 12,
    interactionType: props.interactionType || [InteractionType.GATHER],
    seasonalAvailability: props.seasonalAvailability || Object.values(Season),
    resourceType: props.resourceType || ResourceType.ORE,
    quantity: props.quantity || 1,
    respawnTime: props.respawnTime || 24,
    toolsRequired: props.toolsRequired || []
  } as ResourceNode
  const validation = validateExplorationFeature(node)
  if (!validation.isValid) {
    throw new Error(`Invalid resource node: ${validation.errors.join(', ')}`)
  }
  return node
} 