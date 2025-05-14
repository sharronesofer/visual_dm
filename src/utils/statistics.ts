// Statistical analysis and metrics utilities for POI generation

export type POIMetrics = {
  typeCounts: Record<string, number>;
  positionCounts: Record<string, number>;
  density: number;
  total: number;
};

export function collectMetrics(pois: any[]): POIMetrics {
  const typeCounts: Record<string, number> = {};
  const positionCounts: Record<string, number> = {};
  let total = 0;
  pois.forEach(poi => {
    typeCounts[poi.type] = (typeCounts[poi.type] || 0) + 1;
    const posKey = `${poi.position.x},${poi.position.y}`;
    positionCounts[posKey] = (positionCounts[posKey] || 0) + 1;
    total++;
  });
  const density = total / Object.keys(positionCounts).length;
  return { typeCounts, positionCounts, density, total };
}

export function chiSquareTest(
  observed: number[],
  expected: number[]
): { chi2: number; pValue: number } {
  let chi2 = 0;
  for (let i = 0; i < observed.length; i++) {
    if (expected[i] > 0) {
      chi2 += Math.pow(observed[i] - expected[i], 2) / expected[i];
    }
  }
  // pValue calculation omitted for brevity (requires chi2 distribution table or library)
  return { chi2, pValue: NaN };
}

export function kolmogorovSmirnovTest(
  sample: number[],
  cdf: (x: number) => number
): { d: number; pValue: number } {
  const sorted = [...sample].sort((a, b) => a - b);
  let d = 0;
  for (let i = 0; i < sorted.length; i++) {
    const empirical = (i + 1) / sorted.length;
    const theoretical = cdf(sorted[i]);
    d = Math.max(d, Math.abs(empirical - theoretical));
  }
  // pValue calculation omitted for brevity
  return { d, pValue: NaN };
}

export function generateHeatMap(pois: any[], width: number, height: number): number[][] {
  const heatMap = Array.from({ length: height }, () => Array(width).fill(0));
  pois.forEach(poi => {
    if (
      poi.position &&
      poi.position.x >= 0 &&
      poi.position.y >= 0 &&
      poi.position.x < width &&
      poi.position.y < height
    ) {
      heatMap[poi.position.y][poi.position.x] += 1;
    }
  });
  return heatMap;
}

export function exportMetrics(metrics: POIMetrics, format: 'json' | 'csv' = 'json'): string {
  if (format === 'json') {
    return JSON.stringify(metrics, null, 2);
  } else {
    const rows = [
      'type,count',
      ...Object.entries(metrics.typeCounts).map(([type, count]) => `${type},${count}`),
    ];
    return rows.join('\n');
  }
}
