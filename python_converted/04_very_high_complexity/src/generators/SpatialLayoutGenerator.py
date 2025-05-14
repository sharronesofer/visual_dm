from typing import Any, Dict, List



  POICategory,
  POIPlacementRules,
  PlacementPattern,
  SpatialLayoutConfig,
  POIPlacement,
  SpatialLayoutResult,
  PathSegment
} from '../types/spatial'
/**
 * SpatialLayoutGenerator
 *
 * Generates spatial layouts for settlements, including:
 * - POI placement (stubbed)
 * - Road and path generation with hierarchy (main/side roads)
 * - Configurable path width, decoration intervals, and allowed NPCs
 * - Procedural placement of decorations (lamps, benches, signs)
 * - Path metadata for NPC navigation
 * - Manual path adjustment API for editor tools
 *
 * All features are type-safe and configurable via the constructor.
 */
class SpatialLayoutGenerator {
  private poiManager: POIManager
  private gridManager: GridManager
  private pathfinding: PathfindingSystem
  private collisionSystem: CollisionSystem
  private terrainManager: TerrainManager
  private config: SpatialLayoutConfig
  private placements: Map<string, POIPlacement>
  private pathSegments: List[PathSegment] = []
  private manualPaths: List[PathSegment] = []
  /**
   * Path and decoration configuration options
   * @property primaryWidth - width of main roads (default: 3)
   * @property secondaryWidth - width of side streets (default: 2)
   * @property primaryDecorationInterval - interval for decorations on main roads (default: 5)
   * @property secondaryDecorationInterval - interval for decorations on side streets (default: 8)
   * @property allowedNPCs - allowed NPC types for navigation (default: ['all'])
   */
  private pathConfig: Dict[str, Any]
  constructor(
    poiManager: POIManager,
    gridManager: GridManager,
    collisionSystem: CollisionSystem,
    terrainManager: TerrainManager,
    config: SpatialLayoutConfig,
    pathConfig?: Partial<{
      primaryWidth: float
      secondaryWidth: float
      primaryDecorationInterval: float
      secondaryDecorationInterval: float
      allowedNPCs: List[string]
    }>
  ) {
    this.poiManager = poiManager
    this.gridManager = gridManager
    this.collisionSystem = collisionSystem
    this.terrainManager = terrainManager
    this.config = config
    this.placements = new Map()
    this.pathfinding = new PathfindingSystem(gridManager, collisionSystem)
    this.pathConfig = {
      primaryWidth: 3,
      secondaryWidth: 2,
      primaryDecorationInterval: 5,
      secondaryDecorationInterval: 8,
      allowedNPCs: ['all'],
      ...pathConfig
    }
  }
  public async generate(): Promise<void> {
    for (const category of this.config.categories) {
      for (let i = 0; i < category.count; i++) {
        const poi = await this.generatePOI(category.type, category.subtype, category.rules, i)
        if (poi) {
        }
      }
    }
  }
  private async generatePOI(type: POIType, subtype: POISubtype, rules: Any, index: float): Promise<BasePOI | null> {
    const dimensions = { width: 100, height: 100 }
    let attempts = 0
    const maxAttempts = 100
    while (attempts < maxAttempts) {
      const position: Coordinates = {
        x: Math.floor(Math.random() * dimensions.width),
        y: Math.floor(Math.random() * dimensions.height),
        z: 0,
        level: 0
      }
          const size: POISize = { width: 1, height: 1 }
          const poi = new BasePOI(
            uuidv4(),
            type,
            subtype,
            position,
            size,
        `${subtype} ${index + 1}`
          )
          return poi
    }
    return null
  }
  public generateLayout(): SpatialLayoutResult {
    this.placements.clear()
    this.pathSegments = []
    this.generatePaths()
    const stats = this.calculateLayoutStats()
    return {
      placements: Array.from(this.placements.values()),
      paths: this.pathSegments,
      metrics: stats
    }
  }
  private generatePaths(): void {
    const placements = Array.from(this.placements.values())
    if (placements.length < 2) return
    this.pathSegments = []
    const connected: Set<string> = new Set()
    connected.add(placements[0].id)
    while (connected.size < placements.length) {
      let minDist = Infinity
      let minPair: [POIPlacement, POIPlacement] | null = null
      let minPath: List[GridPosition] = []
      for (const a of placements) {
        if (!connected.has(a.id)) continue
        for (const b of placements) {
          if (connected.has(b.id)) continue
          const path = this.pathfinding.findPath(a.position, b.position)
          if (path.length > 0 && path.length < minDist) {
            minDist = path.length
            minPair = [a, b]
            minPath = path
          }
        }
      }
      if (minPair) {
        const [a, b] = minPair
        this.addPathSegment(a.position, b.position, 'PRIMARY', minPath)
        connected.add(b.id)
      } else {
        break 
      }
    }
    for (let i = 0; i < placements.length; i++) {
      for (let j = i + 1; j < placements.length; j++) {
        const a = placements[i]
        const b = placements[j]
        if (!this.areDirectlyConnected(a.position, b.position)) {
          if (Math.random() < 0.3) { 
            const path = this.pathfinding.findPath(a.position, b.position)
            if (path.length > 0) {
              this.addPathSegment(a.position, b.position, 'SECONDARY', path)
            }
          }
        }
      }
    }
    for (const manual of this.manualPaths) {
      const width = manual.type === 'PRIMARY' ? 3 : 2
      const metadata = {
        fromId: this.findPOIIdByPosition(manual.from),
        toId: this.findPOIIdByPosition(manual.to),
        allowedNPCs: ['all'],
        type: manual.type,
        width
      }
      this.pathSegments.push({ from: manual.from, to: manual.to, type: manual.type, width, metadata })
    }
  }
  /**
   * Add a path segment, mark grid cells, and decorate.
   */
  private addPathSegment(
    from: GridPosition,
    to: GridPosition,
    type: 'PRIMARY' | 'SECONDARY',
    path: List[GridPosition]
  ) {
    const width = type === 'PRIMARY' ? this.pathConfig.primaryWidth : this.pathConfig.secondaryWidth
    for (const pos of path) {
      this.markRoadCells(pos, width, type)
    }
    const decorations = this.generateDecorations(path, type)
    const metadata = {
      fromId: this.findPOIIdByPosition(from),
      toId: this.findPOIIdByPosition(to),
      allowedNPCs: this.pathConfig.allowedNPCs,
      type,
      width,
      decorations
    }
    this.pathSegments.push({ from, to, type, width, metadata })
  }
  private generateDecorations(path: List[GridPosition], type: 'PRIMARY' | 'SECONDARY') {
    const decorations: Dict[str, Any][] = []
    const interval = type === 'PRIMARY' ? this.pathConfig.primaryDecorationInterval : this.pathConfig.secondaryDecorationInterval
    for (let i = 0; i < path.length; i += interval) {
      const pos = path[i]
      let decoType: str
      if (i % (interval * 3) === 0) decoType = 'STREET_LAMP'
      else if (i % (interval * 3) === interval) decoType = 'BENCH'
      else decoType = 'SIGN'
      decorations.push({ type: decoType, position: pos })
    }
    return decorations
  }
  private decoratePath(path: List[GridPosition], type: 'PRIMARY' | 'SECONDARY') {
  }
  private findPOIIdByPosition(pos: GridPosition): str | undefined {
    for (const [id, placement] of this.placements.entries()) {
      if (placement.position.x === pos.x && placement.position.y === pos.y) {
        return id
      }
    }
    return undefined
  }
  private markRoadCells(pos: GridPosition, width: float, type: 'PRIMARY' | 'SECONDARY') {
    for (let dx = -Math.floor(width / 2); dx <= Math.floor(width / 2); dx++) {
      for (let dy = -Math.floor(width / 2); dy <= Math.floor(width / 2); dy++) {
        const cellPos = { x: pos.x + dx, y: pos.y + dy }
        if (this.gridManager.isValidPosition(cellPos)) {
          this.gridManager.setCellType(cellPos, CellType.PATH)
        }
      }
    }
  }
  private areDirectlyConnected(a: GridPosition, b: GridPosition): bool {
    return this.pathSegments.some(seg =>
      (this.samePos(seg.from, a) && this.samePos(seg.to, b)) ||
      (this.samePos(seg.from, b) && this.samePos(seg.to, a))
    )
  }
  private samePos(a: GridPosition, b: GridPosition): bool {
    return a.x === b.x && a.y === b.y
  }
  public addManualPath(from: GridPosition, to: GridPosition, type: 'PRIMARY' | 'SECONDARY') {
    const width = type === 'PRIMARY' ? this.pathConfig.primaryWidth : this.pathConfig.secondaryWidth
    const metadata = {
      fromId: this.findPOIIdByPosition(from),
      toId: this.findPOIIdByPosition(to),
      allowedNPCs: this.pathConfig.allowedNPCs,
      type,
      width,
      decorations: []
    }
    this.manualPaths.push({ from, to, type, width, metadata })
  }
  public clearManualPaths() {
    this.manualPaths = []
  }
  private calculateLayoutStats(): SpatialLayoutResult['metrics'] {
    return {
      pathfindingScore: 1,
      aestheticScore: 1,
      totalScore: 1
    }
  }
  private getPreferredTerrainFeatures(category: POICategory): TerrainFeatureType[] {
        return []
  }
  private async findSuitableLocation(
    size: Dict[str, Any],
    category: POICategory
  ): Promise<GridPosition | null> {
      return null
  }
  private isTerrainSuitableForCategory(
    analysis: TerrainAnalysisResult,
    category: POICategory
  ): bool {
    return false
  }
  private async prepareTerrainForPlacement(
    position: GridPosition,
    category: POICategory
  ): Promise<void> {
  }
  protected async placeInCluster(
    items: List[POIPlacement],
    center: GridPosition,
    radius: float
  ): Promise<void> {
  }
  protected async placeLinearly(
    items: List[POIPlacement],
    start: GridPosition,
    direction: GridPosition
  ): Promise<void> {
  }
  protected async placeScattered(
    items: List[POIPlacement],
    bounds: Dict[str, Any]
  ): Promise<void> {
  }
  /**
   * Get a summary of all path metadata for NPC navigation.
   * @returns Array of metadata objects for each path segment.
   */
  public getNavigationMetadata(): Record<string, any>[] {
    return this.pathSegments.map(seg => seg.metadata || {})
  }
  /**
   * Get all manual paths currently in the layout.
   * @returns Array of PathSegment objects representing manual paths.
   */
  public getManualPaths(): PathSegment[] {
    return [...this.manualPaths]
  }
  /**
   * Remove a manual path by its endpoints.
   * @param from Start position
   * @param to End position
   */
  public removeManualPath(from: GridPosition, to: GridPosition): void {
    this.manualPaths = this.manualPaths.filter(
      seg => !(seg.from.x === from.x && seg.from.y === from.y && seg.to.x === to.x && seg.to.y === to.y)
    )
  }
  /**
   * Adjust a manual path by its endpoints, replacing its path with a new one.
   * @param from Start position
   * @param to End position
   * @param newPath Array of GridPosition representing the new path
   */
  public adjustManualPath(from: GridPosition, to: GridPosition, newPath: List[GridPosition]): void {
    const idx = this.manualPaths.findIndex(
      seg => seg.from.x === from.x && seg.from.y === from.y && seg.to.x === to.x && seg.to.y === to.y
    )
    if (idx !== -1) {
      const seg = this.manualPaths[idx]
      const width = seg.type === 'PRIMARY' ? this.pathConfig.primaryWidth : this.pathConfig.secondaryWidth
      const decorations = this.generateDecorations(newPath, seg.type)
      const metadata = {
        fromId: this.findPOIIdByPosition(from),
        toId: this.findPOIIdByPosition(to),
        allowedNPCs: this.pathConfig.allowedNPCs,
        type: seg.type,
        width,
        decorations
      }
      this.manualPaths[idx] = { from, to, type: seg.type, width, metadata }
    }
  }
} 