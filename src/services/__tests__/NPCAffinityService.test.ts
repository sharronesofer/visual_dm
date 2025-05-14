import { NPCAffinityService } from '../NPCAffinityService';
import { RelationshipType } from '../../types/npc/affinity';

describe('NPCAffinityService', () => {
  let service: NPCAffinityService;
  beforeEach(() => {
    service = NPCAffinityService.getInstance();
    // Clear affinities for isolation
    (service as any).affinities.clear();
  });

  it('creates and retrieves affinity records', () => {
    const affinity = service.getAffinity('npc1', 'npc2');
    expect(affinity.npcId1).toBe('npc1');
    expect(affinity.npcId2).toBe('npc2');
    expect(affinity.score).toBe(0);
    expect(affinity.relationship).toBe(RelationshipType.STRANGER);
  });

  it('updates affinity and relationship type', () => {
    let affinity = service.updateAffinity('npc1', 'npc2', 25);
    expect(affinity.score).toBe(25);
    expect(affinity.relationship).toBe(RelationshipType.ACQUAINTANCE);
    affinity = service.updateAffinity('npc1', 'npc2', 30);
    expect(affinity.relationship).toBe(RelationshipType.FRIEND);
    affinity = service.updateAffinity('npc1', 'npc2', 50);
    expect(affinity.relationship).toBe(RelationshipType.CLOSE_FRIEND);
    affinity = service.updateAffinity('npc1', 'npc2', -200);
    expect(affinity.relationship).toBe(RelationshipType.ENEMY);
  });

  it('returns all affinities for an NPC', () => {
    service.updateAffinity('npc1', 'npc2', 10);
    service.updateAffinity('npc1', 'npc3', 5);
    service.updateAffinity('npc4', 'npc1', -5);
    const all = service.getAllAffinitiesForNPC('npc1');
    expect(all.length).toBe(3);
  });

  it('decays affinities and updates relationship type', () => {
    service.updateAffinity('npc1', 'npc2', 60);
    service.decayAffinities(20);
    const affinity = service.getAffinity('npc1', 'npc2');
    expect(affinity.score).toBe(40);
    expect(affinity.relationship).toBe(RelationshipType.ACQUAINTANCE);
  });

  it('processes daily interactions with ~10% probability', () => {
    const service = NPCAffinityService.getInstance();
    (service as any).affinities.clear();
    
    // Mock the random function to make this test deterministic
    const originalRandom = Math.random;
    const mockInteractions: Record<string, boolean> = {};
    
    try {
      // Mock Math.random to return controlled values
      Math.random = jest.fn().mockImplementation(() => {
        return 0.09; // Just below 0.1 (10%) to force interactions
      });
      
      // 10 NPCs in one POI: 45 pairs
      const npcsByPoi = { 'poi1': Array.from({ length: 10 }, (_, i) => `npc${i}`) };
      
      // Run the interactions with mocked random
      const interactionsCount = service.processInteractions(npcsByPoi);
      
      // With our mocked 9% chance, all interactions should occur
      // This verifies that the interaction probability logic works correctly
      expect(interactionsCount).toBe(45); // All 45 possible pairs should interact
      
      // Verify some affinity records were actually created
      const allAffinities = Array.from((service as any).affinities.values());
      expect(allAffinities.length).toBeGreaterThan(0);
      
      // Test with 11% (above threshold) to ensure no interactions
      Math.random = jest.fn().mockImplementation(() => {
        return 0.11; // Just above 0.1 (10%) to prevent interactions
      });
      
      (service as any).affinities.clear();
      const noInteractionsCount = service.processInteractions(npcsByPoi);
      expect(noInteractionsCount).toBe(0); // No interactions should occur
      
    } finally {
      // Restore the original Math.random
      Math.random = originalRandom;
    }
  });

  it('processes interactions deterministically with a seed', () => {
    const service = NPCAffinityService.getInstance();
    (service as any).affinities.clear();
    const npcsByPoi = { 'poi1': ['npc1', 'npc2', 'npc3'] };
    const count1 = service.processInteractions(npcsByPoi, { seed: 42 });
    (service as any).affinities.clear();
    const count2 = service.processInteractions(npcsByPoi, { seed: 42 });
    expect(count1).toBe(count2);
  });

  it('updates affinity scores during interactions', () => {
    const service = NPCAffinityService.getInstance();
    (service as any).affinities.clear();
    const npcsByPoi = { 'poi1': ['npcA', 'npcB'] };
    service.processInteractions(npcsByPoi, { seed: 1 });
    const affinity = service.getAffinity('npcA', 'npcB');
    // Score should be in [-2, 2] or 0 if no interaction
    expect(affinity.score).toBeGreaterThanOrEqual(-2);
    expect(affinity.score).toBeLessThanOrEqual(2);
  });
}); 