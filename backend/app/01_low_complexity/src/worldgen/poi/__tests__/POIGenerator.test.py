from typing import Any



describe('POIGenerator', () => {
  it('should generate valid POI content for a shop', () => {
    const generator = new POIGenerator()
    const content = generator.generate('shop')
    expect(content.template.type).toBe('shop')
    expect(Array.isArray(content.loot)).toBe(true)
    expect(Array.isArray(content.npcs)).toBe(true)
    expect(content.loot.length).toBeGreaterThan(0)
    expect(content.npcs.length).toBeGreaterThan(0)
  })
}) 