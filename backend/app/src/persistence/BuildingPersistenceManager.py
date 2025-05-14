from typing import Any


/**
 * Configuration options for the BuildingPersistenceManager
 */
class BuildingPersistenceConfig:
    /** Database connection configuration */
  database: Database
    /** Storage prefix for persistence */
  storagePrefix?: str
    /** Debounce time for state updates (ms) */
  debounceTime?: float
    /** Version for data migrations */
  version?: float
    /** Enable transaction support */
  enableTransactions?: bool
/**
 * Helper function to create error metadata
 */
function createErrorMetadata(error: unknown, additionalData: Record<string, any> = {}): LogMetadata {
  const baseMetadata: Record<string, unknown> = {
    ...additionalData
  }
  if (error instanceof Error) {
    baseMetadata.error = error.message
    if (error.stack) {
      baseMetadata.stack = error.stack
    }
  } else {
    baseMetadata.error = String(error)
  }
  return baseMetadata as LogMetadata
}
/**
 * Manages persistence operations for building data
 */
class BuildingPersistenceManager {
  private database: Database
  private logger: Logger
  private persistence: PersistenceHandler
  private enableTransactions: bool
  private config: \'BuildingPersistenceConfig\'
  private spatialIndex: SpatialIndex
  constructor(config: BuildingPersistenceConfig) {
    this.database = config.database
    this.logger = Logger.getInstance().child('BuildingPersistenceManager')
    this.enableTransactions = config.enableTransactions ?? false
    this.config = config
    this.spatialIndex = new SpatialIndex()
    this.persistence = createPersistence({
      prefix: config.storagePrefix || 'vdm_building_',
      debounceTime: config.debounceTime || 1000,
      version: config.version || 1
    })
    this.initializeTables().catch(error => {
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to initialize database tables:', metadata)
      throw error
    })
    this.loadBuildingsIntoSpatialIndex().catch(error => {
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to load buildings into spatial index:', metadata)
    })
  }
  /**
   * Initialize required database tables
   */
  private async initializeTables(): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute(`
        CREATE TABLE IF NOT EXISTS buildings (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          position JSON NOT NULL,
          dimensions JSON NOT NULL,
          metadata JSON,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `)
      await this.database.execute(`
        CREATE TABLE IF NOT EXISTS building_interiors (
          building_id TEXT PRIMARY KEY REFERENCES buildings(id),
          floors INTEGER NOT NULL,
          rooms JSON NOT NULL,
          connections JSON NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `)
      await this.database.execute(`
        CREATE TABLE IF NOT EXISTS building_states (
          building_id TEXT PRIMARY KEY REFERENCES buildings(id),
          state JSON NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `)
      await this.commitTransaction()
      this.logger.info('Database tables initialized successfully')
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to initialize database tables:', metadata)
      throw error
    }
  }
  /**
   * Begin a database transaction if supported
   */
  private async beginTransaction(): Promise<void> {
    if (this.database.beginTransaction && this.enableTransactions) {
      try {
        await this.database.beginTransaction()
        this.logger.debug('Transaction started')
      } catch (error) {
        const metadata = createErrorMetadata(error)
        this.logger.error('Failed to begin transaction:', metadata)
        throw error
      }
    }
  }
  /**
   * Commit a database transaction if supported
   */
  private async commitTransaction(): Promise<void> {
    if (this.database.commitTransaction && this.enableTransactions) {
      try {
        await this.database.commitTransaction()
        this.logger.debug('Transaction committed')
      } catch (error) {
        const metadata = createErrorMetadata(error)
        this.logger.error('Failed to commit transaction:', metadata)
        throw error
      }
    }
  }
  /**
   * Rollback a database transaction if supported
   */
  private async rollbackTransaction(): Promise<void> {
    if (this.database.rollbackTransaction && this.enableTransactions) {
      try {
        await this.database.rollbackTransaction()
        this.logger.debug('Transaction rolled back')
      } catch (error) {
        const metadata = createErrorMetadata(error)
        this.logger.error('Failed to rollback transaction:', metadata)
      }
    }
  }
  /**
   * Load all buildings into spatial index
   */
  private async loadBuildingsIntoSpatialIndex(): Promise<void> {
    try {
      const results = await this.database.query('SELECT * FROM buildings')
      const buildings = results.map(result => this.mapDatabaseToBuilding(result))
      this.spatialIndex.bulkLoad(buildings)
      this.logger.info('Buildings loaded into spatial index', { count: buildings.length })
    } catch (error) {
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to load buildings into spatial index:', metadata)
      throw error
    }
  }
  /**
   * Save building data with persistence and update spatial index
   */
  public async saveBuilding(building: Building): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute(
        `INSERT INTO buildings (id, name, type, position, dimensions, metadata)
         VALUES (?, ?, ?, ?, ?, ?)
         ON CONFLICT (id) DO UPDATE SET
           name = excluded.name,
           type = excluded.type,
           position = excluded.position,
           dimensions = excluded.dimensions,
           metadata = excluded.metadata,
           updated_at = CURRENT_TIMESTAMP`,
        [
          building.id,
          building.name,
          building.type,
          JSON.stringify(building.position),
          JSON.stringify(building.dimensions),
          building.metadata ? JSON.stringify(building.metadata) : null
        ]
      )
      await this.persistence.saveState(`building_${building.id}`, building)
      this.spatialIndex.insert(building)
      await this.commitTransaction()
      this.logger.info('Building saved successfully', { buildingId: building.id })
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error, { buildingId: building.id })
      this.logger.error('Failed to save building:', metadata)
      throw error
    }
  }
  /**
   * Load building data from persistence
   */
  public async loadBuilding(buildingId: str): Promise<Building | null> {
    try {
      const cached = await this.persistence.getStoredState<Building>(`building_${buildingId}`)
      if (cached) {
        this.logger.debug('Building loaded from cache', { buildingId })
        return cached
      }
      const results = await this.database.query(
        `SELECT * FROM buildings WHERE id = ?`,
        [buildingId]
      )
      if (results.length === 0) {
        return null
      }
      const building = this.mapDatabaseToBuilding(results[0])
      await this.persistence.saveState(`building_${buildingId}`, building, true)
      this.logger.info('Building loaded successfully', { buildingId })
      return building
    } catch (error) {
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to load building:', metadata)
      throw error
    }
  }
  /**
   * Map database record to Building object
   */
  private mapDatabaseToBuilding(record: QueryResult[0]): Building {
    return {
      id: record.id,
      name: record.name,
      type: record.type,
      position: JSON.parse(record.position),
      dimensions: JSON.parse(record.dimensions),
      metadata: record.metadata ? JSON.parse(record.metadata) : undefined,
      createdAt: new Date(record.created_at),
      updatedAt: new Date(record.updated_at)
    }
  }
  /**
   * Map database record to BuildingInterior object
   */
  private mapDatabaseToInterior(record: QueryResult[0]): BuildingInterior {
    return JSON.parse(record.interior_data)
  }
  /**
   * Map database record to BuildingState object
   */
  private mapDatabaseToState(record: QueryResult[0]): BuildingState {
    return JSON.parse(record.state)
  }
  /**
   * Get building by ID with optional interior and state
   */
  public async getBuilding(buildingId: str, includeInterior: bool = false, includeState: bool = false): Promise<Building | null> {
    try {
      const results = await this.database.query(
        'SELECT * FROM buildings WHERE id = ?',
        [buildingId]
      )
      if (results.length === 0) {
        return null
      }
      const building = this.mapDatabaseToBuilding(results[0])
      if (includeInterior) {
        const interiorResults = await this.database.query(
          'SELECT * FROM building_interiors WHERE building_id = ?',
          [buildingId]
        )
        if (interiorResults.length > 0) {
          building.interior = this.mapDatabaseToInterior(interiorResults[0])
        }
      }
      if (includeState) {
        const stateResults = await this.database.query(
          'SELECT * FROM building_states WHERE building_id = ?',
          [buildingId]
        )
        if (stateResults.length > 0) {
          building.state = this.mapDatabaseToState(stateResults[0])
        }
      }
      return building
    } catch (error) {
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to get building:', metadata)
      throw error
    }
  }
  /**
   * Get all buildings with optional interior and state
   */
  public async getAllBuildings(includeInterior: bool = false, includeState: bool = false): Promise<Building[]> {
    try {
      const results = await this.database.query('SELECT * FROM buildings')
      const buildings = results.map(result => this.mapDatabaseToBuilding(result))
      if (includeInterior || includeState) {
        await Promise.all(buildings.map(async building => {
          if (includeInterior) {
            const interiorResults = await this.database.query(
              'SELECT * FROM building_interiors WHERE building_id = ?',
              [building.id]
            )
            if (interiorResults.length > 0) {
              building.interior = this.mapDatabaseToInterior(interiorResults[0])
            }
          }
          if (includeState) {
            const stateResults = await this.database.query(
              'SELECT * FROM building_states WHERE building_id = ?',
              [building.id]
            )
            if (stateResults.length > 0) {
              building.state = this.mapDatabaseToState(stateResults[0])
            }
          }
        }))
      }
      return buildings
    } catch (error) {
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to get all buildings:', metadata)
      throw error
    }
  }
  /**
   * Delete building data and remove from spatial index
   */
  public async deleteBuilding(buildingId: str): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute(
        'DELETE FROM buildings WHERE id = ?',
        [buildingId]
      )
      await this.persistence.removeState(`building_${buildingId}`)
      this.spatialIndex.remove(buildingId)
      await this.commitTransaction()
      this.logger.info('Building deleted successfully', { buildingId })
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to delete building:', metadata)
      throw error
    }
  }
  /**
   * Clear all building data and spatial index
   */
  public async clearAllBuildings(): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute('DELETE FROM building_states')
      await this.database.execute('DELETE FROM building_interiors')
      await this.database.execute('DELETE FROM buildings')
      await this.persistence.clearAllStates()
      this.spatialIndex.clear()
      await this.commitTransaction()
      this.logger.info('All building data cleared successfully')
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error)
      this.logger.error('Failed to clear all building data:', metadata)
      throw error
    }
  }
  /**
   * Save building state
   */
  public async saveBuildingState(buildingId: str, state: BuildingState): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute(
        `INSERT INTO building_states (building_id, state)
         VALUES (?, ?)
         ON CONFLICT (building_id) DO UPDATE SET
           state = excluded.state,
           updated_at = CURRENT_TIMESTAMP`,
        [buildingId, JSON.stringify(state)]
      )
      await this.persistence.saveState(`building_state_${buildingId}`, state)
      await this.commitTransaction()
      this.logger.info('Building state saved successfully', { buildingId })
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to save building state:', metadata)
      throw error
    }
  }
  /**
   * Load building state
   */
  public async loadBuildingState(buildingId: str): Promise<BuildingState | null> {
    try {
      const cached = await this.persistence.getStoredState<BuildingState>(`building_state_${buildingId}`)
      if (cached) {
        this.logger.debug('Building state loaded from cache', { buildingId })
        return cached
      }
      const results = await this.database.query(
        `SELECT state FROM building_states WHERE building_id = ?`,
        [buildingId]
      )
      if (results.length === 0) {
        return null
      }
      const state = JSON.parse(results[0].state)
      await this.persistence.saveState(`building_state_${buildingId}`, state, true)
      this.logger.info('Building state loaded successfully', { buildingId })
      return state
    } catch (error) {
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to load building state:', metadata)
      throw error
    }
  }
  /**
   * Save building interior
   */
  public async saveBuildingInterior(buildingId: str, interior: BuildingInterior): Promise<void> {
    try {
      await this.beginTransaction()
      await this.database.execute(
        `INSERT INTO building_interiors (building_id, floors, rooms, connections)
         VALUES (?, ?, ?, ?)
         ON CONFLICT (building_id) DO UPDATE SET
           floors = excluded.floors,
           rooms = excluded.rooms,
           connections = excluded.connections,
           updated_at = CURRENT_TIMESTAMP`,
        [
          buildingId,
          interior.floors,
          JSON.stringify(interior.rooms),
          JSON.stringify(interior.connections)
        ]
      )
      await this.persistence.saveState(`building_interior_${buildingId}`, interior)
      await this.commitTransaction()
      this.logger.info('Building interior saved successfully', { buildingId })
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to save building interior:', metadata)
      throw error
    }
  }
  /**
   * Load building interior
   */
  public async loadBuildingInterior(buildingId: str): Promise<BuildingInterior | null> {
    try {
      const cached = await this.persistence.getStoredState<BuildingInterior>(`building_interior_${buildingId}`)
      if (cached) {
        this.logger.debug('Building interior loaded from cache', { buildingId })
        return cached
      }
      const results = await this.database.query(
        `SELECT floors, rooms, connections FROM building_interiors WHERE building_id = ?`,
        [buildingId]
      )
      if (results.length === 0) {
        return null
      }
      const interior: BuildingInterior = {
        floors: results[0].floors,
        rooms: JSON.parse(results[0].rooms),
        connections: JSON.parse(results[0].connections)
      }
      await this.persistence.saveState(`building_interior_${buildingId}`, interior, true)
      this.logger.info('Building interior loaded successfully', { buildingId })
      return interior
    } catch (error) {
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to load building interior:', metadata)
      throw error
    }
  }
  /**
   * Load complete building data including state and interior
   */
  public async loadCompleteBuildingData(buildingId: str): Promise<Building | null> {
    try {
      const building = await this.loadBuilding(buildingId)
      if (!building) {
        return null
      }
      const [state, interior] = await Promise.all([
        this.loadBuildingState(buildingId),
        this.loadBuildingInterior(buildingId)
      ])
      return {
        ...building,
        state: state || undefined,
        interior: interior || undefined
      }
    } catch (error) {
      const metadata = createErrorMetadata(error, { buildingId })
      this.logger.error('Failed to load complete building data:', metadata)
      throw error
    }
  }
  /**
   * Save complete building data including state and interior
   */
  public async saveCompleteBuildingData(building: Building): Promise<void> {
    try {
      await this.beginTransaction()
      await this.saveBuilding(building)
      if (building.state) {
        await this.saveBuildingState(building.id, building.state)
      }
      if (building.interior) {
        await this.saveBuildingInterior(building.id, building.interior)
      }
      await this.commitTransaction()
      this.logger.info('Complete building data saved successfully', { buildingId: building.id })
    } catch (error) {
      await this.rollbackTransaction()
      const metadata = createErrorMetadata(error, { buildingId: building.id })
      this.logger.error('Failed to save complete building data:', metadata)
      throw error
    }
  }
  /**
   * Search for buildings within bounds
   */
  public searchBuildings(bounds: SearchBounds): Building[] {
    return this.spatialIndex.search(bounds)
  }
  /**
   * Find nearest buildings to a point
   */
  public findNearestBuildings(x: float, y: float, k: float = 5): Building[] {
    return this.spatialIndex.findNearest(x, y, k)
  }
} 