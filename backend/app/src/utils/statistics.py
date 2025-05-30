from typing import Any, Dict, List


POIMetrics = {
  typeCounts: Dict[str, float>
  positionCounts: Record<string, number>
  density: float
  total: float
}
function collectMetrics(pois: List[any]): POIMetrics {
  const typeCounts: Record<string, number> = {}
  const positionCounts: Record<string, number> = {}
  let total = 0
  pois.forEach(poi => {
    typeCounts[poi.type] = (typeCounts[poi.type] || 0) + 1
    const posKey = `${poi.position.x},${poi.position.y}`
    positionCounts[posKey] = (positionCounts[posKey] || 0) + 1
    total++
  })
  const density = total / Object.keys(positionCounts).length
  return { typeCounts, positionCounts, density, total }
}
function chiSquareTest(
  observed: List[number],
  expected: List[number]
): { chi2: float; pValue: float } {
  let chi2 = 0
  for (let i = 0; i < observed.length; i++) {
    if (expected[i] > 0) {
      chi2 += Math.pow(observed[i] - expected[i], 2) / expected[i]
    }
  }
  return { chi2, pValue: NaN }
}
function kolmogorovSmirnovTest(
  sample: List[number],
  cdf: (x: float) => number
): { d: float; pValue: float } {
  const sorted = [...sample].sort((a, b) => a - b)
  let d = 0
  for (let i = 0; i < sorted.length; i++) {
    const empirical = (i + 1) / sorted.length
    const theoretical = cdf(sorted[i])
    d = Math.max(d, Math.abs(empirical - theoretical))
  }
  return { d, pValue: NaN }
}
function generateHeatMap(pois: List[any], width: float, height: float): number[][] {
  const heatMap = Array.from({ length: height }, () => Array(width).fill(0))
  pois.forEach(poi => {
    if (
      poi.position &&
      poi.position.x >= 0 &&
      poi.position.y >= 0 &&
      poi.position.x < width &&
      poi.position.y < height
    ) {
      heatMap[poi.position.y][poi.position.x] += 1
    }
  })
  return heatMap
}
function exportMetrics(metrics: POIMetrics, format: 'json' | 'csv' = 'json'): str {
  if (format === 'json') {
    return JSON.stringify(metrics, null, 2)
  } else {
    const rows = [
      'type,count',
      ...Object.entries(metrics.typeCounts).map(([type, count]) => `${type},${count}`),
    ]
    return rows.join('\n')
  }
}