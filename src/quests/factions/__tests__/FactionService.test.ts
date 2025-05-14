import { FactionService } from '../FactionService';
import { FactionData } from '../types';
import { FactionType } from '../../../types/factions/faction';

describe('FactionService', () => {
  const mockFactions: FactionData[] = [
    {
      id: FactionType.MERCHANTS,
      name: 'Merchants',
      description: 'Trade-focused faction',
      relationships: {
        [FactionType.WARRIORS]: 10,
        [FactionType.SCHOLARS]: 0,
        [FactionType.NOBLES]: -20,
        [FactionType.OUTLAWS]: -100,
        [FactionType.RELIGIOUS]: 0,
        [FactionType.NEUTRAL]: 0,
        [FactionType.MERCHANTS]: 100
      },
      values: { wealth: 100, power: 20 },
      resources: { gold: 1000, goods: 500 },
      standing: 50,
      tier: 2
    },
    {
      id: FactionType.WARRIORS,
      name: 'Warriors',
      description: 'Combat-focused faction',
      relationships: {
        [FactionType.MERCHANTS]: 10,
        [FactionType.SCHOLARS]: 0,
        [FactionType.NOBLES]: 0,
        [FactionType.OUTLAWS]: -50,
        [FactionType.RELIGIOUS]: 0,
        [FactionType.NEUTRAL]: 0,
        [FactionType.WARRIORS]: 100
      },
      values: { power: 100, honor: 80 },
      resources: { weapons: 200, gold: 300 },
      standing: 40,
      tier: 2
    }
  ];

  it('initializes and retrieves factions', () => {
    const service = new FactionService(mockFactions);
    const merchants = service.getFaction(FactionType.MERCHANTS);
    expect(merchants).toBeDefined();
    expect(merchants!.name).toBe('Merchants');
    expect(merchants!.relationships.get(FactionType.WARRIORS)).toBe(10);
  });

  it('updates relationships and enforces boundaries', () => {
    const service = new FactionService(mockFactions);
    service.updateRelationship(FactionType.MERCHANTS, FactionType.WARRIORS, 95);
    const merchants = service.getFaction(FactionType.MERCHANTS)!;
    const warriors = service.getFaction(FactionType.WARRIORS)!;
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(100);
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(100);
    // Test lower bound
    service.updateRelationship(FactionType.MERCHANTS, FactionType.WARRIORS, -300);
    expect(merchants.relationships.get(FactionType.WARRIORS)).toBe(-100);
    expect(warriors.relationships.get(FactionType.MERCHANTS)).toBe(-100);
  });

  it('updates and retrieves resources', () => {
    const service = new FactionService(mockFactions);
    service.updateResource(FactionType.MERCHANTS, 'gold', 500);
    expect(service.getResource(FactionType.MERCHANTS, 'gold')).toBe(1500);
    service.updateResource(FactionType.MERCHANTS, 'gold', -2000);
    expect(service.getResource(FactionType.MERCHANTS, 'gold')).toBe(-500);
  });

  it('serializes and deserializes faction data', () => {
    const service = new FactionService(mockFactions);
    const serialized = service.serialize();
    expect(serialized.length).toBe(2);
    // All FactionType keys should be present in relationships
    for (const f of serialized) {
      for (const key of Object.values(FactionType)) {
        expect(f.relationships).toHaveProperty(key);
      }
    }
    // Test deserialization
    const newService = new FactionService();
    newService.deserialize(serialized);
    expect(newService.getFaction(FactionType.MERCHANTS)).toBeDefined();
    expect(newService.getFaction(FactionType.WARRIORS)).toBeDefined();
  });

  it('throws on missing factions', () => {
    const service = new FactionService(mockFactions);
    expect(() => service.getFaction(FactionType.SCHOLARS)).not.toThrow(); // undefined is ok
    expect(() => service.updateRelationship(FactionType.MERCHANTS, FactionType.SCHOLARS, 10)).toThrow();
    expect(() => service.updateResource(FactionType.SCHOLARS, 'gold', 10)).toThrow();
    expect(() => service.getResource(FactionType.SCHOLARS, 'gold')).toThrow();
  });

  it('getRelationships returns all relationships as a plain object', () => {
    const service = new FactionService(mockFactions);
    const rels = service.getRelationships(FactionType.MERCHANTS);
    expect(rels[FactionType.WARRIORS]).toBe(10);
    expect(rels[FactionType.NOBLES]).toBe(-20);
  });
}); 