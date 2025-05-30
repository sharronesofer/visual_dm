from typing import Any


describe('regionToTactical', () => {
  it('extracts correct terrain, elevation, and weather', () => {
    const grid = new HexGrid(5, 5)
    for (let r = 0; r < 5; r++) for (let q = 0; q < 5; q++) {
      const cell = grid.get(q, r)!
      cell.terrain = (q + r) % 2 === 0 ? 'plains' : 'forest'
      cell.elevation = q + r
      cell.weather = 'rain'
    }
    const tactical = regionToTactical(grid, 2, 2, 3)
    for (let r = 0; r < 3; r++) for (let q = 0; q < 3; q++) {
      const tCell = tactical.get(q, r)!
      const gCell = grid.get(q + 1, r + 1)!
      expect(tCell.terrain).toBe(gCell.terrain)
      expect(tCell.elevation).toBe(gCell.elevation)
      expect(tCell.weather).toBe('rain')
    }
  })
  it('creates correct tactical grid size and center mapping', () => {
    const grid = new HexGrid(7, 7)
    const tactical = regionToTactical(grid, 3, 3, 5)
    expect(tactical.width).toBe(5)
    expect(tactical.height).toBe(5)
    const tCenter = tactical.get(2, 2)!
    const gCenter = grid.get(3, 3)!
    expect(tCenter.terrain).toBe(gCenter.terrain)
  })
  it('handles edge case at region grid border', () => {
    const grid = new HexGrid(3, 3)
    for (let r = 0; r < 3; r++) for (let q = 0; q < 3; q++) grid.get(q, r)!.terrain = 'plains'
    const tactical = regionToTactical(grid, 0, 0, 3)
    expect(tactical.get(1, 1)!.terrain).toBe('plains')
  })
}) 