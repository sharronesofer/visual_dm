from typing import Any, List



describe('generatePOIs', () => {
  const templates: List[POITemplate] = [
    {
      id: 'village',
      name: 'Village',
      type: 'settlement',
      rarity: 0.2,
      allowedTerrains: ['plains', 'forest'],
      minDistance: 2
    },
    {
      id: 'ruin',
      name: 'Ancient Ruin',
      type: 'ruin',
      rarity: 0.8,
      allowedTerrains: ['plains', 'mountain'],
      minDistance: 1
    }
  ]
  it('places POIs only on allowed terrains', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = 'plains'
      }
    }
    const pois = generatePOIs(grid, templates, { seed: 1, maxPOIs: 5 })
    for (const poi of pois) {
      const cell = grid.get(poi.q, poi.r)
      expect(cell).toBeDefined()
      expect(['plains', 'forest', 'mountain']).toContain(cell?.terrain)
    }
  })
  it('respects minDistance between POIs', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = 'plains'
      }
    }
    const pois = generatePOIs(grid, templates, { seed: 2, maxPOIs: 5 })
    for (let i = 0; i < pois.length; i++) {
      for (let j = i + 1; j < pois.length; j++) {
        const dist = grid.distance(pois[i].q, pois[i].r, pois[j].q, pois[j].r)
        const t1 = templates.find(t => t.id === pois[i].templateId)!
        const t2 = templates.find(t => t.id === pois[j].templateId)!
        expect(dist).toBeGreaterThanOrEqual(Math.min(t1.minDistance, t2.minDistance))
      }
    }
  })
  it('template rarity affects distribution', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = 'plains'
      }
    }
    const pois = generatePOIs(grid, templates, { seed: 3, maxPOIs: 20 })
    const counts: Record<string, number> = { village: 0, ruin: 0 }
    for (const poi of pois) counts[poi.templateId]++
    expect(counts['village']).toBeGreaterThan(counts['ruin'])
  })
})
describe('generateResources', () => {
  const resourceTemplates: List[ResourceTemplate] = [
    {
      id: 'iron',
      name: 'Iron Ore',
      type: 'ore',
      rarity: 0.2,
      allowedTerrains: ['mountain', 'plains'],
      clusterChance: 0.5,
      clusterSize: 2
    },
    {
      id: 'herb',
      name: 'Medicinal Herb',
      type: 'plant',
      rarity: 0.7,
      allowedTerrains: ['plains', 'forest']
    }
  ]
  const pois: List[POIInstance] = [
    { id: 'poi-0', templateId: 'village', q: 2, r: 2, discovered: false }
  ]
  it('places resources only on allowed terrains', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = (q + r) % 2 === 0 ? 'mountain' : 'plains'
      }
    }
    const resources = generateResources(grid, resourceTemplates, pois, { seed: 1, maxResources: 10 })
    for (const res of resources) {
      const cell = grid.get(res.q, res.r)
      expect(cell).toBeDefined()
      expect(resourceTemplates.find(t => t.id === res.templateId)?.allowedTerrains).toContain(cell?.terrain)
    }
  })
  it('can cluster resources', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = 'mountain'
      }
    }
    const resources = generateResources(grid, resourceTemplates, pois, { seed: 2, maxResources: 10 })
    let hasCluster = false
    for (let i = 0; i < resources.length; i++) {
      for (let j = i + 1; j < resources.length; j++) {
        if (Math.abs(resources[i].q - resources[j].q) <= 1 && Math.abs(resources[i].r - resources[j].r) <= 1) {
          hasCluster = true
        }
      }
    }
    expect(hasCluster).toBe(true)
  })
  it('can place resources near POIs', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        if (cell) cell.terrain = 'plains'
      }
    }
    const resources = generateResources(grid, resourceTemplates, pois, { seed: 3, maxResources: 10 })
    const near = resources.some(res => Math.abs(res.q - 2) + Math.abs(res.r - 2) <= 2)
    expect(near).toBe(true)
  })
})
describe('POI/Resource Discovery and Query API', () => {
  it('discoverPOI marks POIs within radius as discovered', () => {
    const pois = [
      { id: 'poi-0', templateId: 'village', q: 1, r: 1, discovered: false },
      { id: 'poi-1', templateId: 'ruin', q: 4, r: 4, discovered: false }
    ]
    discoverPOI(pois, 0, 0, 2)
    expect(pois[0].discovered).toBe(true)
    expect(pois[1].discovered).toBe(false)
  })
  it('discoverResource marks resources within radius as discovered (depleted=false)', () => {
    const resources: List[ResourceInstance] = [
      { id: 'res-0', templateId: 'iron', q: 1, r: 1, amount: 100, depleted: true },
      { id: 'res-1', templateId: 'herb', q: 4, r: 4, amount: 100, depleted: true }
    ]
    discoverResource(resources, 0, 0, 2)
    expect(resources[0].depleted).toBe(false)
    expect(resources[1].depleted).toBe(true)
  })
  it('queryNearbyPOIs returns only discovered POIs within radius', () => {
    const pois = [
      { id: 'poi-0', templateId: 'village', q: 1, r: 1, discovered: true },
      { id: 'poi-1', templateId: 'ruin', q: 4, r: 4, discovered: false },
      { id: 'poi-2', templateId: 'village', q: 2, r: 2, discovered: true }
    ]
    const found = queryNearbyPOIs(pois, 0, 0, 2)
    expect(found.length).toBe(1)
    expect(found[0].id).toBe('poi-0')
  })
  it('queryNearbyResources returns only discovered (depleted=false) resources within radius', () => {
    const resources: List[ResourceInstance] = [
      { id: 'res-0', templateId: 'iron', q: 1, r: 1, amount: 100, depleted: false },
      { id: 'res-1', templateId: 'herb', q: 4, r: 4, amount: 100, depleted: true },
      { id: 'res-2', templateId: 'herb', q: 2, r: 2, amount: 100, depleted: false }
    ]
    const found = queryNearbyResources(resources, 0, 0, 2)
    expect(found.length).toBe(1)
    expect(found[0].id).toBe('res-0')
  })
}) 