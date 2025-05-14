from typing import Any, Dict



  collectMetrics,
  chiSquareTest,
  kolmogorovSmirnovTest,
  generateHeatMap,
  exportMetrics,
  POIMetrics,
} from '../statistics'
describe('statistics utilities', () => {
  const samplePOIs = [
    { type: 'dungeon', position: Dict[str, Any] },
    { type: 'dungeon', position: Dict[str, Any] },
    { type: 'city', position: Dict[str, Any] },
    { type: 'city', position: Dict[str, Any] },
    { type: 'city', position: Dict[str, Any] },
  ]
  it('collectMetrics computes correct type and position counts', () => {
    const metrics = collectMetrics(samplePOIs)
    expect(metrics.typeCounts).toEqual({ dungeon: 2, city: 3 })
    expect(metrics.positionCounts).toEqual({ '1,2': 2, '2,2': 1, '3,4': 2 })
    expect(metrics.total).toBe(5)
    expect(metrics.density).toBeCloseTo(5 / 3)
  })
  it('chiSquareTest returns correct chi2 for known values', () => {
    const observed = [10, 20, 30]
    const expected = [15, 15, 30]
    const { chi2 } = chiSquareTest(observed, expected)
    expect(chi2).toBeCloseTo(3.333, 2)
  })
  it('kolmogorovSmirnovTest returns correct d for uniform sample', () => {
    const sample = [0.1, 0.4, 0.5, 0.7, 0.9]
    const cdf = (x: float) => x 
    const { d } = kolmogorovSmirnovTest(sample, cdf)
    expect(d).toBeLessThan(0.5)
  })
  it('generateHeatMap produces correct 2D array', () => {
    const pois = [
      { position: Dict[str, Any] },
      { position: Dict[str, Any] },
      { position: Dict[str, Any] },
      { position: Dict[str, Any] },
    ]
    const heatMap = generateHeatMap(pois, 2, 2)
    expect(heatMap).toEqual([
      [2, 1],
      [1, 0],
    ])
  })
  it('exportMetrics outputs correct JSON and CSV', () => {
    const metrics: POIMetrics = {
      typeCounts: Dict[str, Any],
      positionCounts: Dict[str, Any],
      density: 1.5,
      total: 5,
    }
    const json = exportMetrics(metrics, 'json')
    expect(json).toContain('dungeon')
    expect(json).toContain('city')
    const csv = exportMetrics(metrics, 'csv')
    expect(csv).toContain('type,count')
    expect(csv).toContain('dungeon,2')
    expect(csv).toContain('city,3')
  })
  it('handles empty input gracefully', () => {
    const metrics = collectMetrics([])
    expect(metrics.typeCounts).toEqual({})
    expect(metrics.positionCounts).toEqual({})
    expect(metrics.total).toBe(0)
    expect(metrics.density).toBeNaN()
    const heatMap = generateHeatMap([], 2, 2)
    expect(heatMap).toEqual([
      [0, 0],
      [0, 0],
    ])
  })
})