from typing import Any, Dict, Union


{ ExplorationSubtype }
class ResourceNode:
    id: str
    type: Union['mineral', 'herb', 'artifact', 'wildlife']
    properties: Dict[str, Any]
class Discovery:
    id: str
    type: Union['lore', 'secret', 'vista', 'challenge']
    properties: Dict[str, Any]
/**
 * Specialized POI class for exploration-type locations
 */
class ExplorationPOI extends BasePOI {
  private resourceNodes: Map<string, ResourceNode>
  private discoveries: Map<string, Discovery>
  private explorationProgress: float
  private environmentalChallenges: Set<string>
  constructor(
    id: str,
    name: str,
    subtype: ExplorationSubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    super(id, name, POIType.EXPLORATION, subtype, coordinates, thematicElements)
    this.resourceNodes = new Map<string, ResourceNode>()
    this.discoveries = new Map<string, Discovery>()
    this.explorationProgress = 0
    this.environmentalChallenges = new Set<string>()
    this.boundingBox = { width: 3, height: 1, depth: 3 } 
    this.canExpand = true
    this.expansionRules = [
      {
        direction: 'north',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'south',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'east',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'west',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      }
    ]
    this.initializeBySubtype(subtype)
  }
  addResourceNode(node: ResourceNode): void {
    this.resourceNodes.set(node.id, node)
    this.features.push({
      id: node.id,
      type: `resource_${node.type}`,
      properties: node.properties
    })
    this.trackChange('modification', `Added ${node.type} resource node: ${node.id}`)
  }
  removeResourceNode(nodeId: str): bool {
    const removed = this.resourceNodes.delete(nodeId)
    if (removed) {
      this.features = this.features.filter(f => f.id !== nodeId)
      this.trackChange('modification', `Removed resource node: ${nodeId}`)
    }
    return removed
  }
  getResourceNode(nodeId: str): \'ResourceNode\' | undefined {
    return this.resourceNodes.get(nodeId)
  }
  harvestResource(nodeId: str): bool {
    const node = this.resourceNodes.get(nodeId)
    if (node && node.properties.quantity > 0) {
      node.properties.quantity--
      node.properties.lastHarvested = Date.now()
      this.trackChange('modification', `Harvested resource: ${nodeId}`)
      if (node.properties.quantity === 0 && node.properties.isDepletable) {
        this.removeResourceNode(nodeId)
      }
      return true
    }
    return false
  }
  addDiscovery(discovery: Discovery): void {
    this.discoveries.set(discovery.id, discovery)
    this.features.push({
      id: discovery.id,
      type: `discovery_${discovery.type}`,
      properties: discovery.properties
    })
    this.trackChange('modification', `Added ${discovery.type} discovery: ${discovery.id}`)
  }
  removeDiscovery(discoveryId: str): bool {
    const removed = this.discoveries.delete(discoveryId)
    if (removed) {
      this.features = this.features.filter(f => f.id !== discoveryId)
      this.trackChange('modification', `Removed discovery: ${discoveryId}`)
    }
    return removed
  }
  getDiscovery(discoveryId: str): \'Discovery\' | undefined {
    return this.discoveries.get(discoveryId)
  }
  revealDiscovery(discoveryId: str, requiredItem?: str): bool {
    const discovery = this.discoveries.get(discoveryId)
    if (discovery && !discovery.properties.isRevealed) {
      if (discovery.properties.requiresItem && discovery.properties.requiresItem !== requiredItem) {
        return false
      }
      discovery.properties.isRevealed = true
      this.explorationProgress = this.calculateExplorationProgress()
      this.trackChange('modification', `Revealed discovery: ${discoveryId}`)
      return true
    }
    return false
  }
  addEnvironmentalChallenge(challenge: str): void {
    this.environmentalChallenges.add(challenge)
    this.trackChange('modification', `Added environmental challenge: ${challenge}`)
  }
  removeEnvironmentalChallenge(challenge: str): bool {
    const removed = this.environmentalChallenges.delete(challenge)
    if (removed) {
      this.trackChange('modification', `Removed environmental challenge: ${challenge}`)
    }
    return removed
  }
  getEnvironmentalChallenges(): string[] {
    return Array.from(this.environmentalChallenges)
  }
  getExplorationProgress(): float {
    return this.explorationProgress
  }
  serialize(): Record<string, unknown> {
    return {
      ...super.serialize(),
      resourceNodes: Array.from(this.resourceNodes.entries()),
      discoveries: Array.from(this.discoveries.entries()),
      explorationProgress: this.explorationProgress,
      environmentalChallenges: Array.from(this.environmentalChallenges)
    }
  }
  deserialize(data: Record<string, unknown>): void {
    super.deserialize(data)
    if (Array.isArray(data.resourceNodes)) {
      this.resourceNodes = new Map(data.resourceNodes)
    }
    if (Array.isArray(data.discoveries)) {
      this.discoveries = new Map(data.discoveries)
    }
    if (typeof data.explorationProgress === 'number') {
      this.explorationProgress = data.explorationProgress
    }
    if (Array.isArray(data.environmentalChallenges)) {
      this.environmentalChallenges = new Set(data.environmentalChallenges)
    }
  }
  validateThematicCoherence(): bool {
    return super.validateThematicCoherence() && this.validateExplorationTheme()
  }
  private validateExplorationTheme(): bool {
    return (
      this.validateResourceDistribution() &&
      this.validateDiscoveryPlacement() &&
      this.validateEnvironmentalChallenges()
    )
  }
  private validateResourceDistribution(): bool {
    const resourceTypes = new Set(Array.from(this.resourceNodes.values()).map(node => node.type))
    switch (this.subtype as ExplorationSubtype) {
      case ExplorationSubtype.WILDERNESS:
        return resourceTypes.has('herb') || resourceTypes.has('wildlife')
      case ExplorationSubtype.LANDMARK:
        return resourceTypes.has('artifact')
      case ExplorationSubtype.MOUNTAIN:
        return resourceTypes.has('mineral')
      default:
        return true
    }
  }
  private validateDiscoveryPlacement(): bool {
    for (const discovery of this.discoveries.values()) {
      if (discovery.properties.significance < 1 || discovery.properties.significance > 10) {
        return false
      }
    }
    return true
  }
  private validateEnvironmentalChallenges(): bool {
    return this.environmentalChallenges.size > 0
  }
  private calculateExplorationProgress(): float {
    const totalDiscoveries = this.discoveries.size
    if (totalDiscoveries === 0) return 0
    const revealedDiscoveries = Array.from(this.discoveries.values())
      .filter(d => d.properties.isRevealed).length
    return (revealedDiscoveries / totalDiscoveries) * 100
  }
  private initializeBySubtype(subtype: ExplorationSubtype): void {
    switch (subtype) {
      case ExplorationSubtype.WILDERNESS:
        this.boundingBox = { width: 4, height: 1, depth: 4 } 
        this.addEnvironmentalChallenge('weather')
        this.addEnvironmentalChallenge('terrain')
        break
      case ExplorationSubtype.LANDMARK:
        this.thematicElements.lighting = 'dim'
        this.addEnvironmentalChallenge('structural_integrity')
        break
      case ExplorationSubtype.MOUNTAIN:
        this.thematicElements.lighting = 'dark'
        this.boundingBox.height = 2
        this.addEnvironmentalChallenge('altitude')
        this.addEnvironmentalChallenge('weather')
        break
      case ExplorationSubtype.GROVE:
        this.thematicElements.dangerLevel = Math.min(3, this.thematicElements.dangerLevel)
        this.addEnvironmentalChallenge('wildlife')
        break
      default:
        break
    }
  }
} 