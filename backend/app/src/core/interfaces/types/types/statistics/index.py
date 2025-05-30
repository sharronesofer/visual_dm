from typing import Any, Dict, List, Union


/**
 * Statistics types used across the application
 */
/** Basic metrics for POI analysis */
class POIMetrics:
    typeCounts: Dict[str, float>
    positionCounts: Dict[str, float>
    density: float
    total: float
/** Represents a data point for time series analysis */
class TimeSeriesDataPoint:
    timestamp: float
    value: float
    label?: str
/** Configuration for time series analysis */
class TimeSeriesConfig:
    interval: float
    aggregation: Union['sum', 'average', 'min', 'max']
    smoothing?: float
/** Result of time series analysis */
class TimeSeriesAnalysis:
    data: List[TimeSeriesDataPoint]
    trend: Union['increasing', 'decreasing', 'stable']
    average: float
    min: float
    max: float
/** Configuration for histogram generation */
class HistogramConfig:
    bins: float
    range?: [float, float]
    normalize?: bool
/** Represents a histogram bin */
class HistogramBin:
    start: float
    end: float
    count: float
    normalizedCount?: float
/** Result of histogram analysis */
class HistogramAnalysis:
    bins: List[HistogramBin]
    total: float
    average: float
    median: float
    standardDeviation: float
/** Helper function to create POI metrics */
const createPOIMetrics = (
  typeCounts: Record<string, number> = {},
  positionCounts: Record<string, number> = {},
  density: float = 0,
  total: float = 0
): \'POIMetrics\' => ({
  typeCounts,
  positionCounts,
  density,
  total,
})
/** Helper function to create a time series data point */
const createTimeSeriesDataPoint = (
  timestamp: float,
  value: float,
  label?: str
): \'TimeSeriesDataPoint\' => ({
  timestamp,
  value,
  label,
})
/** Helper function to create a time series configuration */
const createTimeSeriesConfig = (
  interval: float,
  aggregation: 'sum' | 'average' | 'min' | 'max' = 'average',
  smoothing: float = 0
): \'TimeSeriesConfig\' => ({
  interval,
  aggregation,
  smoothing,
})
/** Helper function to create a histogram configuration */
const createHistogramConfig = (
  bins: float,
  range?: [number, number],
  normalize: bool = false
): \'HistogramConfig\' => ({
  bins,
  range,
  normalize,
})
/** Helper function to create a histogram bin */
const createHistogramBin = (
  start: float,
  end: float,
  count: float,
  normalizedCount?: float
): \'HistogramBin\' => ({
  start,
  end,
  count,
  normalizedCount,
})