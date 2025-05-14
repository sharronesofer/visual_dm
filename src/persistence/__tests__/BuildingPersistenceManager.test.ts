import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BuildingPersistenceManager } from '../BuildingPersistenceManager';
import { Database, QueryResult } from '../../types/database';
import { Building, BuildingInterior, BuildingState } from '../../types/buildings';
import { Logger } from '../../utils/logger';

// Mock the database
const mockDatabase = {
  execute: vi.fn(async () => {}),
  query: vi.fn(async () => [] as QueryResult),
  beginTransaction: vi.fn(async () => {}),
  commitTransaction: vi.fn(async () => {}),
  rollbackTransaction: vi.fn(async () => {})
} as unknown as jest.Mocked<Database>;

// Mock the logger
vi.mock('../../utils/logger', () => ({
  Logger: {
    getInstance: vi.fn().mockReturnValue({
      child: vi.fn().mockReturnValue({
        debug: vi.fn(),
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn()
      })
    })
  }
}));

describe('BuildingPersistenceManager', () => {
  let manager: BuildingPersistenceManager;
  let testBuilding: Building;
  let testInterior: BuildingInterior;
  let testState: BuildingState;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Create test building
    testBuilding = {
      id: 'test-building-1',
      name: 'Test Building',
      type: 'residential',
      position: { x: 0, y: 0, z: 0 },
      dimensions: { width: 10, height: 20, length: 10 },
      metadata: {
        description: 'A test building',
        owner: 'Test Owner'
      }
    };

    // Create test interior
    testInterior = {
      floors: 2,
      rooms: [
        {
          id: 'room-1',
          name: 'Living Room',
          type: 'living',
          floor: 1,
          dimensions: { width: 5, height: 3, length: 5 },
          position: { x: 0, y: 0, z: 0 }
        }
      ],
      connections: [
        {
          from: 'room-1',
          to: 'room-2',
          type: 'door'
        }
      ]
    };

    // Create test state
    testState = {
      condition: 100,
      occupancy: 0,
      power: {
        connected: true,
        consumption: 0
      },
      temperature: 20
    };

    // Initialize manager
    manager = new BuildingPersistenceManager({
      database: mockDatabase,
      storagePrefix: 'test_',
      enableTransactions: true
    });
  });

  describe('initialization', () => {
    it('should create required database tables', async () => {
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('CREATE TABLE IF NOT EXISTS buildings')
      );
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('CREATE TABLE IF NOT EXISTS building_interiors')
      );
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('CREATE TABLE IF NOT EXISTS building_states')
      );
    });

    it('should handle database initialization errors', async () => {
      mockDatabase.execute.mockRejectedValueOnce(new Error('Table creation failed'));
      
      await expect(new BuildingPersistenceManager({
        database: mockDatabase,
        enableTransactions: true
      })).rejects.toThrow('Table creation failed');
    });
  });

  describe('saveBuilding', () => {
    it('should save building data to database and update spatial index', async () => {
      await manager.saveBuilding(testBuilding);

      expect(mockDatabase.beginTransaction).toHaveBeenCalled();
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO buildings'),
        expect.arrayContaining([
          testBuilding.id,
          testBuilding.name,
          testBuilding.type,
          JSON.stringify(testBuilding.position),
          JSON.stringify(testBuilding.dimensions),
          JSON.stringify(testBuilding.metadata)
        ])
      );
      expect(mockDatabase.commitTransaction).toHaveBeenCalled();
    });

    it('should handle errors and rollback transaction', async () => {
      const error = new Error('Database error');
      mockDatabase.execute.mockRejectedValueOnce(error);

      await expect(manager.saveBuilding(testBuilding)).rejects.toThrow(error);
      expect(mockDatabase.rollbackTransaction).toHaveBeenCalled();
    });
  });

  describe('saveBuildingInterior', () => {
    it('should save interior data to database', async () => {
      await manager.saveBuildingInterior(testBuilding.id, testInterior);

      expect(mockDatabase.beginTransaction).toHaveBeenCalled();
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO building_interiors'),
        expect.arrayContaining([
          testBuilding.id,
          testInterior.floors,
          JSON.stringify(testInterior.rooms),
          JSON.stringify(testInterior.connections)
        ])
      );
      expect(mockDatabase.commitTransaction).toHaveBeenCalled();
    });

    it('should handle errors and rollback transaction', async () => {
      const error = new Error('Database error');
      mockDatabase.execute.mockRejectedValueOnce(error);

      await expect(manager.saveBuildingInterior(testBuilding.id, testInterior)).rejects.toThrow(error);
      expect(mockDatabase.rollbackTransaction).toHaveBeenCalled();
    });
  });

  describe('saveBuildingState', () => {
    it('should save state data to database', async () => {
      await manager.saveBuildingState(testBuilding.id, testState);

      expect(mockDatabase.beginTransaction).toHaveBeenCalled();
      expect(mockDatabase.execute).toHaveBeenCalledWith(
        expect.stringContaining('INSERT INTO building_states'),
        expect.arrayContaining([
          testBuilding.id,
          JSON.stringify(testState)
        ])
      );
      expect(mockDatabase.commitTransaction).toHaveBeenCalled();
    });

    it('should handle errors and rollback transaction', async () => {
      const error = new Error('Database error');
      mockDatabase.execute.mockRejectedValueOnce(error);

      await expect(manager.saveBuildingState(testBuilding.id, testState)).rejects.toThrow(error);
      expect(mockDatabase.rollbackTransaction).toHaveBeenCalled();
    });
  });

  describe('loadCompleteBuildingData', () => {
    it('should load complete building data including state and interior', async () => {
      mockDatabase.query
        // Building query
        .mockResolvedValueOnce([{
          id: testBuilding.id,
          name: testBuilding.name,
          type: testBuilding.type,
          position: JSON.stringify(testBuilding.position),
          dimensions: JSON.stringify(testBuilding.dimensions),
          metadata: JSON.stringify(testBuilding.metadata),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }])
        // State query
        .mockResolvedValueOnce([{
          building_id: testBuilding.id,
          state: JSON.stringify(testState)
        }])
        // Interior query
        .mockResolvedValueOnce([{
          building_id: testBuilding.id,
          floors: testInterior.floors,
          rooms: JSON.stringify(testInterior.rooms),
          connections: JSON.stringify(testInterior.connections)
        }]);

      const building = await manager.loadCompleteBuildingData(testBuilding.id);
      expect(building).toBeTruthy();
      expect(building?.id).toBe(testBuilding.id);
      expect(building?.state).toEqual(testState);
      expect(building?.interior).toEqual(testInterior);
    });

    it('should return null if building does not exist', async () => {
      mockDatabase.query.mockResolvedValueOnce([]);

      const building = await manager.loadCompleteBuildingData('nonexistent');
      expect(building).toBeNull();
    });

    it('should handle missing state and interior', async () => {
      mockDatabase.query
        // Building query
        .mockResolvedValueOnce([{
          id: testBuilding.id,
          name: testBuilding.name,
          type: testBuilding.type,
          position: JSON.stringify(testBuilding.position),
          dimensions: JSON.stringify(testBuilding.dimensions),
          metadata: JSON.stringify(testBuilding.metadata),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }])
        // State query - empty
        .mockResolvedValueOnce([])
        // Interior query - empty
        .mockResolvedValueOnce([]);

      const building = await manager.loadCompleteBuildingData(testBuilding.id);
      expect(building).toBeTruthy();
      expect(building?.id).toBe(testBuilding.id);
      expect(building?.state).toBeUndefined();
      expect(building?.interior).toBeUndefined();
    });
  });

  describe('clearAllBuildings', () => {
    it('should clear all building data from database and spatial index', async () => {
      await manager.clearAllBuildings();

      expect(mockDatabase.beginTransaction).toHaveBeenCalled();
      expect(mockDatabase.execute).toHaveBeenCalledWith('DELETE FROM building_states');
      expect(mockDatabase.execute).toHaveBeenCalledWith('DELETE FROM building_interiors');
      expect(mockDatabase.execute).toHaveBeenCalledWith('DELETE FROM buildings');
      expect(mockDatabase.commitTransaction).toHaveBeenCalled();
    });

    it('should handle errors and rollback transaction', async () => {
      const error = new Error('Database error');
      mockDatabase.execute.mockRejectedValueOnce(error);

      await expect(manager.clearAllBuildings()).rejects.toThrow(error);
      expect(mockDatabase.rollbackTransaction).toHaveBeenCalled();
    });
  });

  describe('spatial queries', () => {
    it('should find buildings within bounds', async () => {
      const bounds = {
        minX: -5,
        minY: -5,
        maxX: 5,
        maxY: 5
      };

      const buildings = manager.searchBuildings(bounds);
      expect(Array.isArray(buildings)).toBe(true);
    });

    it('should find nearest buildings', async () => {
      const buildings = manager.findNearestBuildings(0, 0, 5);
      expect(Array.isArray(buildings)).toBe(true);
    });
  });

  describe('error handling and edge cases', () => {
    it('should handle invalid building data', async () => {
      const invalidBuilding = {
        ...testBuilding,
        position: null,
        dimensions: undefined
      };

      await expect(manager.saveBuilding(invalidBuilding as any)).rejects.toThrow();
    });

    it('should handle concurrent operations gracefully', async () => {
      // Simulate concurrent saves
      const promises = [
        manager.saveBuilding(testBuilding),
        manager.saveBuilding({...testBuilding, name: 'Concurrent Save'})
      ];
      
      await expect(Promise.all(promises)).resolves.not.toThrow();
    });

    it('should validate building ID format', async () => {
      const invalidIdBuilding = {
        ...testBuilding,
        id: ''  // Empty ID
      };

      await expect(manager.saveBuilding(invalidIdBuilding)).rejects.toThrow();
    });

    it('should handle database connection loss during transaction', async () => {
      // Simulate connection loss during transaction
      mockDatabase.execute.mockImplementationOnce(() => {
        throw new Error('Connection lost');
      });

      await expect(manager.saveBuilding(testBuilding)).rejects.toThrow('Connection lost');
      expect(mockDatabase.rollbackTransaction).toHaveBeenCalled();
    });

    it('should handle partial building data loading', async () => {
      mockDatabase.query
        // Building exists
        .mockResolvedValueOnce([{
          id: testBuilding.id,
          name: testBuilding.name,
          type: testBuilding.type,
          position: JSON.stringify(testBuilding.position),
          dimensions: JSON.stringify(testBuilding.dimensions),
          metadata: JSON.stringify(testBuilding.metadata),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }])
        // State query fails
        .mockRejectedValueOnce(new Error('State query failed'))
        // Interior loads normally
        .mockResolvedValueOnce([{
          building_id: testBuilding.id,
          floors: testInterior.floors,
          rooms: JSON.stringify(testInterior.rooms),
          connections: JSON.stringify(testInterior.connections)
        }]);

      await expect(manager.loadCompleteBuildingData(testBuilding.id)).rejects.toThrow('State query failed');
    });
  });

  describe('data validation', () => {
    it('should validate building position bounds', async () => {
      const outOfBoundsBuilding = {
        ...testBuilding,
        position: { x: Number.MAX_SAFE_INTEGER + 1, y: 0, z: 0 }
      };

      await expect(manager.saveBuilding(outOfBoundsBuilding)).rejects.toThrow();
    });

    it('should validate building dimensions', async () => {
      const zeroDimensionsBuilding = {
        ...testBuilding,
        dimensions: { width: 0, height: 0, length: 0 }
      };

      await expect(manager.saveBuilding(zeroDimensionsBuilding)).rejects.toThrow();
    });

    it('should validate interior room connections', async () => {
      const invalidConnections = {
        ...testInterior,
        connections: [
          {
            from: 'nonexistent-room',
            to: 'room-1',
            type: 'door'
          }
        ]
      };

      await expect(manager.saveBuildingInterior(testBuilding.id, invalidConnections)).rejects.toThrow();
    });

    it('should validate building state values', async () => {
      const invalidState = {
        ...testState,
        condition: -1, // Invalid negative condition
        temperature: 'hot' // Invalid temperature type
      };

      await expect(manager.saveBuildingState(testBuilding.id, invalidState as any)).rejects.toThrow();
    });
  });
}); 