from typing import Any, List


describe('RegionTerrainGenerator', () => {
  it('assigns terrain types to all cells', () => {
    const grid = new HexGrid(10, 10)
    generateRegionTerrain(grid, { seed: 123 })
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        expect(cell?.terrain).toBeDefined()
      }
    }
  })
  it('produces different results for different seeds', () => {
    const grid1 = new HexGrid(5, 5)
    const grid2 = new HexGrid(5, 5)
    generateRegionTerrain(grid1, { seed: 1 })
    generateRegionTerrain(grid2, { seed: 2 })
    let different = false
    for (let r = 0; r < 5; r++) {
      for (let q = 0; q < 5; q++) {
        if (grid1.get(q, r)?.terrain !== grid2.get(q, r)?.terrain) {
          different = true
        }
      }
    }
    expect(different).toBe(true)
  })
  it('can generate all terrain types', () => {
    const grid = new HexGrid(20, 20)
    generateRegionTerrain(grid, { seed: 999, waterThreshold: 0.05, mountainThreshold: 0.7, forestThreshold: 0.4, desertThreshold: 0.1, urbanChance: 0.2 })
    const terrains = new Set()
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        terrains.add(grid.get(q, r)?.terrain)
      }
    }
    expect(terrains.has('water')).toBe(true)
    expect(terrains.has('mountain')).toBe(true)
    expect(terrains.has('forest')).toBe(true)
    expect(terrains.has('desert')).toBe(true)
    expect(terrains.has('urban')).toBe(true)
    expect(terrains.has('plains')).toBe(true)
  })
})
describe('assignRegionWeather', () => {
  it('assigns weather to all cells', () => {
    const grid = new HexGrid(10, 10)
    assignRegionWeather(grid, { seed: 123 })
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        const cell = grid.get(q, r)
        expect(cell?.weather).toBeDefined()
      }
    }
  })
  it('produces different weather for different seeds', () => {
    const grid1 = new HexGrid(5, 5)
    const grid2 = new HexGrid(5, 5)
    assignRegionWeather(grid1, { seed: 1 })
    assignRegionWeather(grid2, { seed: 2 })
    let different = false
    for (let r = 0; r < 5; r++) {
      for (let q = 0; q < 5; q++) {
        if (grid1.get(q, r)?.weather !== grid2.get(q, r)?.weather) {
          different = true
        }
      }
    }
    expect(different).toBe(true)
  })
  it('can assign all weather types', () => {
    const grid = new HexGrid(20, 20)
    const allTypes: List[WeatherType] = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
    assignRegionWeather(grid, { seed: 999, weatherTypes: allTypes, numFronts: 6 })
    const weathers = new Set()
    for (let r = 0; r < grid.height; r++) {
      for (let q = 0; q < grid.width; q++) {
        weathers.add(grid.get(q, r)?.weather)
      }
    }
    for (const type of allTypes) {
      expect(weathers.has(type)).toBe(true)
    }
  })
})
describe('Fog of War / Discovery Utilities', () => {
  it('setRegionDiscovery marks specified cells as discovered', () => {
    const grid = new HexGrid(5, 5)
    setRegionDiscovery(grid, [{q: 1, r: 1}, {q: 2, r: 2}])
    expect(grid.get(1, 1)?.discovered).toBe(true)
    expect(grid.get(2, 2)?.discovered).toBe(true)
    expect(grid.get(0, 0)?.discovered).toBe(false)
  })
  it('revealRegionFrom marks all cells within radius as discovered', () => {
    const grid = new HexGrid(5, 5)
    revealRegionFrom(grid, 2, 2, 1)
    expect(grid.get(2, 2)?.discovered).toBe(true)
    expect(grid.get(1, 2)?.discovered).toBe(true)
    expect(grid.get(2, 1)?.discovered).toBe(true)
    expect(grid.get(3, 2)?.discovered).toBe(true)
    expect(grid.get(2, 3)?.discovered).toBe(true)
    expect(grid.get(0, 0)?.discovered).toBe(false)
  })
  it('isCellVisible returns true only for discovered cells', () => {
    const grid = new HexGrid(3, 3)
    setRegionDiscovery(grid, [{q: 0, r: 0}])
    expect(isCellVisible(grid, 0, 0)).toBe(true)
    expect(isCellVisible(grid, 1, 1)).toBe(false)
  })
})
describe('hexGridToMapData', () => {
  it('converts a HexGrid to MapData with correct properties', () => {
    const grid = new HexGrid(3, 3)
    generateRegionTerrain(grid, { seed: 42 })
    assignRegionWeather(grid, { seed: 42 })
    setRegionDiscovery(grid, [{q: 0, r: 0}, {q: 1, r: 1}])
    const mapData = hexGridToMapData(grid)
    expect(mapData.size.width).toBe(3)
    expect(mapData.size.height).toBe(3)
    const tile00 = mapData.tiles[0][0]
    expect(tile00.position).toEqual({x: 0, y: 0})
    expect(tile00.explored).toBe(true)
    expect(tile00.visible).toBe(true)
    expect(tile00.weather).toBeDefined()
    const tile02 = mapData.tiles[0][2]
    expect(tile02.explored).toBe(false)
    expect(tile02.visible).toBe(false)
  })
}) 