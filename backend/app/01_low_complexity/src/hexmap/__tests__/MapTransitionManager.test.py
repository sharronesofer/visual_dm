from typing import Any, List



describe('MapTransitionManager', () => {
  it('generates tactical map from region grid and caches it', () => {
    const region = new HexGrid(3, 3)
    region.get(1, 1)!.terrain = 'forest'
    const manager = new MapTransitionManager()
    const tactical1 = manager.generateTacticalMap(region, {q: 1, r: 1}, 'test-key')
    expect(tactical1).toBeInstanceOf(TacticalHexGrid)
    const tactical2 = manager.generateTacticalMap(region, {q: 1, r: 1}, 'test-key')
    expect(tactical2).toBe(tactical1)
  })
  it('transfers units to tactical grid', () => {
    const region = new HexGrid(2, 2)
    const manager = new MapTransitionManager()
    const tactical = manager.generateTacticalMap(region, {q: 0, r: 0}, 'units-key')
    const units = [
      { id: 'u1', q: 0, r: 0 },
      { id: 'u2', q: 1, r: 1 }
    ]
    manager.transferUnitsToTactical(units, tactical)
    expect(tactical.get(0, 0)!.unitOccupants).toContain('u1')
    expect(tactical.get(1, 1)!.unitOccupants).toContain('u2')
  })
  it('fires event hooks on transition', () => {
    const region = new HexGrid(2, 2)
    const manager = new MapTransitionManager()
    const events: List[string] = []
    manager.on('onTransitionStart', () => events.push('start'))
    manager.on('onTacticalMapGenerated', () => events.push('generated'))
    manager.generateTacticalMap(region, {q: 0, r: 0}, 'event-key')
    expect(events).toEqual(['start', 'generated'])
  })
}) 