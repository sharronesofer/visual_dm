from typing import Any



describe('Viewport', () => {
  it('initializes and exposes properties correctly', () => {
    const vp = new Viewport([0, 0], 100, 200, 1)
    expect(vp.center).toEqual([0, 0])
    expect(vp.width).toBe(100)
    expect(vp.height).toBe(200)
    expect(vp.zoom).toBe(1)
    expect(typeof vp.minX).toBe('number')
    expect(typeof vp.maxX).toBe('number')
    expect(typeof vp.minY).toBe('number')
    expect(typeof vp.maxY).toBe('number')
  })
  it('updates boundaries on pan (setCenter)', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    const oldMinX = vp.minX
    vp.setCenter([50, 50])
    expect(vp.minX).toBe(oldMinX + 50)
    expect(vp.center).toEqual([50, 50])
  })
  it('updates boundaries on zoom', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    const oldMinX = vp.minX
    vp.setZoom(1)
    expect(vp.minX).toBeGreaterThan(oldMinX) 
    expect(vp.zoom).toBe(1)
  })
  it('updates boundaries on resize', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    const oldMinX = vp.minX
    vp.setSize(200, 200)
    expect(vp.minX).toBeLessThan(oldMinX) 
    expect(vp.width).toBe(200)
    expect(vp.height).toBe(200)
  })
  it('containsPoint works for points inside and outside', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    expect(vp.containsPoint([0, 0])).toBe(true)
    expect(vp.containsPoint([1000, 1000])).toBe(false)
  })
  it('intersectsRect works for overlapping and non-overlapping rects', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    expect(
      vp.intersectsRect({ minX: -10, minY: -10, maxX: 10, maxY: 10 })
    ).toBe(true)
    expect(
      vp.intersectsRect({ minX: 1000, minY: 1000, maxX: 1100, maxY: 1100 })
    ).toBe(false)
  })
  it('expandByBuffer increases the viewport size', () => {
    const vp = new Viewport([0, 0], 100, 100, 0)
    const expanded = vp.expandByBuffer(1)
    expect(expanded.minX).toBeLessThan(vp.minX)
    expect(expanded.maxX).toBeGreaterThan(vp.maxX)
    expect(expanded.minY).toBeLessThan(vp.minY)
    expect(expanded.maxY).toBeGreaterThan(vp.maxY)
  })
  it('handles zero size and extreme zoom', () => {
    const vp = new Viewport([0, 0], 0, 0, 0)
    expect(vp.minX).toBe(0)
    expect(vp.maxX).toBe(0)
    expect(vp.minY).toBe(0)
    expect(vp.maxY).toBe(0)
    const extreme = new Viewport([0, 0], 100, 100, 20)
    expect(extreme.minX).toBeCloseTo(0, 2)
    expect(extreme.maxX).toBeCloseTo(0, 2)
    expect(extreme.minY).toBeCloseTo(0, 2)
    expect(extreme.maxY).toBeCloseTo(0, 2)
  })
  it('handles negative coordinates', () => {
    const vp = new Viewport([-100, -100], 100, 100, 0)
    expect(vp.center).toEqual([-100, -100])
    expect(vp.containsPoint([-100, -100])).toBe(true)
    expect(vp.containsPoint([0, 0])).toBe(false)
  })
})