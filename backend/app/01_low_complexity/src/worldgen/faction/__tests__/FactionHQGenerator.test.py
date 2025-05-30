from typing import Any



describe('FactionHQGenerator', () => {
  it('should generate a valid HQ layout for a guild', () => {
    const generator = new FactionHQGenerator()
    const layout = generator.generate('guild')
    expect(Array.isArray(layout.rooms)).toBe(true)
    expect(Array.isArray(layout.npcs)).toBe(true)
    expect(Array.isArray(layout.security)).toBe(true)
    expect(layout.rooms.length).toBeGreaterThan(0)
    expect(layout.npcs.length).toBeGreaterThan(0)
    expect(layout.security.length).toBeGreaterThan(0)
    expect(layout.style.name).toBe('Guild Hall')
    expect(Array.isArray(layout.decor)).toBe(true)
  })
}) 