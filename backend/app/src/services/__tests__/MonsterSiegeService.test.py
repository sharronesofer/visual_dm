from typing import Any


describe('MonsterSiegeService', () => {
  let service: MonsterSiegeService
  beforeEach(() => {
    service = MonsterSiegeService.getInstance()
  })
  it('generates attacks for eligible POIs', () => {
    const pois = [
      new POI('1', 'Village A', [0, 0], 'village', 'region1', 'active'),
      new POI('2', 'Village B', [1, 1], 'village', 'region1', 'inactive'),
      new POI('3', 'Town C', [2, 2], 'town', 'region2', 'active'),
    ]
    const attacks = service.triggerAttacks(pois, { seed: 42, attackChance: 1 }) 
    expect(attacks.length).toBe(2)
    expect(attacks[0].poiId).toBe('1')
    expect(attacks[1].poiId).toBe('3')
    expect(attacks[0].monsterTypes).toContain('goblin')
  })
  it('does not generate attacks for ineligible POIs', () => {
    const pois = [
      new POI('1', 'Village A', [0, 0], 'village', 'region1', 'inactive'),
    ]
    const attacks = service.triggerAttacks(pois, { seed: 123, attackChance: 1 })
    expect(attacks.length).toBe(0)
  })
  it('is deterministic with a seed', () => {
    const pois = [new POI('1', 'Village A', [0, 0], 'village', 'region1', 'active')]
    const attacks1 = service.triggerAttacks(pois, { seed: 99, attackChance: 1 })
    const attacks2 = service.triggerAttacks(pois, { seed: 99, attackChance: 1 })
    expect(attacks1[0].direction).toBe(attacks2[0].direction)
    expect(attacks1[0].strength).toBe(attacks2[0].strength)
  })
  it('resolves attack with outcome: defended', async () => {
    const pois = [new POI('A', 'Stronghold', [0, 0], 'fort', 'region', 'active')]
    const [attack] = service.triggerAttacks(pois, { seed: 1, attackChance: 1 })
    attack.strength = 5
    const result = await service.resolveAttack(attack.id)
    expect(result.outcome).toBe('defended')
    expect(result.combatLog[0]).toMatch(/Defenders held off/)
    expect(attack.resolved).toBe(true)
  })
  it('resolves attack with outcome: close_defeat', async () => {
    const pois = [new POI('B', 'Border Town', [0, 0], 'town', 'region', 'active')]
    const [attack] = service.triggerAttacks(pois, { seed: 2, attackChance: 1 })
    const originalRandom = Math.random
    try {
      Math.random = jest.fn().mockReturnValue(0.4) 
      attack.strength = 12
      const result = await service.resolveAttack(attack.id)
      expect(result.outcome).toBe('close_defeat')
      expect(attack.resolved).toBe(true)
      expect(result.combatLog.length).toBeGreaterThan(0)
      const poi = pois[0]
      expect(poi.metadata!.damageLevel).toBeGreaterThan(0)
      expect(poi.metadata!.factionStrength).toBeLessThan(100)
    } finally {
      Math.random = originalRandom
    }
  })
  it('resolves attack with outcome: decisive_defeat', async () => {
    const pois = [new POI('C', 'Outpost', [0, 0], 'outpost', 'region', 'active')]
    const [attack] = service.triggerAttacks(pois, { seed: 3, attackChance: 1 })
    attack.strength = 50
    const result = await service.resolveAttack(attack.id)
    expect(result.outcome).toBe('decisive_defeat')
    expect(attack.resolved).toBe(true)
  })
  it('throws if attack not found', async () => {
    await expect(service.resolveAttack('nonexistent')).rejects.toThrow('Attack not found')
  })
  it('throws if attack already resolved', async () => {
    const pois = [new POI('D', 'Village', [0, 0], 'village', 'region', 'active')]
    const [attack] = service.triggerAttacks(pois, { seed: 4, attackChance: 1 })
    attack.strength = 10
    await service.resolveAttack(attack.id)
    await expect(service.resolveAttack(attack.id)).rejects.toThrow('Attack already resolved')
  })
  it('updates POI state after attack', async () => {
    const poi = new POI('E', 'TestPOI', [0, 0], 'village', 'region', 'active', {})
    const service = MonsterSiegeService.getInstance()
    const [attack] = service.triggerAttacks([poi], { seed: 5, attackChance: 1 })
    attack.strength = 1 
    await service.resolveAttack(attack.id)
    const meta = poi.metadata!
    expect(meta.factionStrength).toBeLessThan(100)
    expect(meta.damageLevel).toBeGreaterThan(0)
    expect(poi.type).toBe('monster_den')
    expect(meta.stateHistory.length).toBeGreaterThan(0)
  })
  it('recovers POI over time', () => {
    const poi = new POI('F', 'RecoverPOI', [0, 0], 'monster_den', 'region', 'active', {
      factionStrength: 10,
      damageLevel: 80,
      recoveryRate: 20,
    })
    const service = MonsterSiegeService.getInstance()
    service.processPoiRecovery(poi)
    const meta = poi.metadata!
    expect(meta.factionStrength).toBe(30)
    expect(meta.damageLevel).toBe(60)
    poi.setType('monster_den')
    poi.setMetadata({ ...meta, factionStrength: 70, damageLevel: 10, recoveryRate: 20 })
    service.processPoiRecovery(poi)
    expect(poi.type).toBe('village')
  })
}) 