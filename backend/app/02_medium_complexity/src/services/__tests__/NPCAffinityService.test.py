from typing import Any



describe('NPCAffinityService', () => {
  let service: NPCAffinityService
  beforeEach(() => {
    service = NPCAffinityService.getInstance()
    (service as any).affinities.clear()
  })
  it('creates and retrieves affinity records', () => {
    const affinity = service.getAffinity('npc1', 'npc2')
    expect(affinity.npcId1).toBe('npc1')
    expect(affinity.npcId2).toBe('npc2')
    expect(affinity.score).toBe(0)
    expect(affinity.relationship).toBe(RelationshipType.STRANGER)
  })
  it('updates affinity and relationship type', () => {
    let affinity = service.updateAffinity('npc1', 'npc2', 25)
    expect(affinity.score).toBe(25)
    expect(affinity.relationship).toBe(RelationshipType.ACQUAINTANCE)
    affinity = service.updateAffinity('npc1', 'npc2', 30)
    expect(affinity.relationship).toBe(RelationshipType.FRIEND)
    affinity = service.updateAffinity('npc1', 'npc2', 50)
    expect(affinity.relationship).toBe(RelationshipType.CLOSE_FRIEND)
    affinity = service.updateAffinity('npc1', 'npc2', -200)
    expect(affinity.relationship).toBe(RelationshipType.ENEMY)
  })
  it('returns all affinities for an NPC', () => {
    service.updateAffinity('npc1', 'npc2', 10)
    service.updateAffinity('npc1', 'npc3', 5)
    service.updateAffinity('npc4', 'npc1', -5)
    const all = service.getAllAffinitiesForNPC('npc1')
    expect(all.length).toBe(3)
  })
  it('decays affinities and updates relationship type', () => {
    service.updateAffinity('npc1', 'npc2', 60)
    service.decayAffinities(20)
    const affinity = service.getAffinity('npc1', 'npc2')
    expect(affinity.score).toBe(40)
    expect(affinity.relationship).toBe(RelationshipType.ACQUAINTANCE)
  })
  it('processes daily interactions with ~10% probability', () => {
    const service = NPCAffinityService.getInstance()
    (service as any).affinities.clear()
    const originalRandom = Math.random
    const mockInteractions: Record<string, boolean> = {}
    try {
      Math.random = jest.fn().mockImplementation(() => {
        return 0.09 
      })
      const npcsByPoi = { 'poi1': Array.from({ length: 10 }, (_, i) => `npc${i}`) }
      const interactionsCount = service.processInteractions(npcsByPoi)
      expect(interactionsCount).toBe(45) 
      const allAffinities = Array.from((service as any).affinities.values())
      expect(allAffinities.length).toBeGreaterThan(0)
      Math.random = jest.fn().mockImplementation(() => {
        return 0.11 
      })
      (service as any).affinities.clear()
      const noInteractionsCount = service.processInteractions(npcsByPoi)
      expect(noInteractionsCount).toBe(0) 
    } finally {
      Math.random = originalRandom
    }
  })
  it('processes interactions deterministically with a seed', () => {
    const service = NPCAffinityService.getInstance()
    (service as any).affinities.clear()
    const npcsByPoi = { 'poi1': ['npc1', 'npc2', 'npc3'] }
    const count1 = service.processInteractions(npcsByPoi, { seed: 42 })
    (service as any).affinities.clear()
    const count2 = service.processInteractions(npcsByPoi, { seed: 42 })
    expect(count1).toBe(count2)
  })
  it('updates affinity scores during interactions', () => {
    const service = NPCAffinityService.getInstance()
    (service as any).affinities.clear()
    const npcsByPoi = { 'poi1': ['npcA', 'npcB'] }
    service.processInteractions(npcsByPoi, { seed: 1 })
    const affinity = service.getAffinity('npcA', 'npcB')
    expect(affinity.score).toBeGreaterThanOrEqual(-2)
    expect(affinity.score).toBeLessThanOrEqual(2)
  })
}) 