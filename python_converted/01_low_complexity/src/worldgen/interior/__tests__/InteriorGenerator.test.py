from typing import Any



describe('InteriorGenerator', () => {
  it('should generate a valid layout for a residential building', () => {
    const params: InteriorParams = {
      buildingType: 'residential',
      width: 12,
      length: 10,
      height: 3,
      entryPoints: [{ x: 0, y: 0 }]
    }
    const variation = VariationParamsProvider.getDefault()
    const generator = new InteriorGenerator(variation)
    const layout = generator.generate(params)
    expect(Array.isArray(layout.rooms)).toBe(true)
    expect(Array.isArray(layout.furniture)).toBe(true)
    expect(layout.rooms.length).toBeGreaterThan(0)
  })
}) 