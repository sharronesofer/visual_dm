/**
 * Statistics types used across the application
 */

/** Basic metrics for POI analysis */
export interface POIMetrics {
  typeCounts: Record<string, number>;
  positionCounts: Record<string, number>;
  density: number;
  total: number;
}

/** Represents a data point for time series analysis */
export interface TimeSeriesDataPoint {
  timestamp: number;
  value: number;
  label?: string;
}

/** Configuration for time series analysis */
export interface TimeSeriesConfig {
  interval: number; // Time interval in milliseconds
  aggregation: 'sum' | 'average' | 'min' | 'max';
  smoothing?: number; // Smoothing factor (0-1)
}

/** Result of time series analysis */
export interface TimeSeriesAnalysis {
  data: TimeSeriesDataPoint[];
  trend: 'increasing' | 'decreasing' | 'stable';
  average: number;
  min: number;
  max: number;
}

/** Configuration for histogram generation */
export interface HistogramConfig {
  bins: number;
  range?: [number, number];
  normalize?: boolean;
}

/** Represents a histogram bin */
export interface HistogramBin {
  start: number;
  end: number;
  count: number;
  normalizedCount?: number;
}

/** Result of histogram analysis */
export interface HistogramAnalysis {
  bins: HistogramBin[];
  total: number;
  average: number;
  median: number;
  standardDeviation: number;
}

/** Helper function to create POI metrics */
export const createPOIMetrics = (
  typeCounts: Record<string, number> = {},
  positionCounts: Record<string, number> = {},
  density: number = 0,
  total: number = 0
): POIMetrics => ({
  typeCounts,
  positionCounts,
  density,
  total,
});

/** Helper function to create a time series data point */
export const createTimeSeriesDataPoint = (
  timestamp: number,
  value: number,
  label?: string
): TimeSeriesDataPoint => ({
  timestamp,
  value,
  label,
});

/** Helper function to create a time series configuration */
export const createTimeSeriesConfig = (
  interval: number,
  aggregation: 'sum' | 'average' | 'min' | 'max' = 'average',
  smoothing: number = 0
): TimeSeriesConfig => ({
  interval,
  aggregation,
  smoothing,
});

/** Helper function to create a histogram configuration */
export const createHistogramConfig = (
  bins: number,
  range?: [number, number],
  normalize: boolean = false
): HistogramConfig => ({
  bins,
  range,
  normalize,
});

/** Helper function to create a histogram bin */
export const createHistogramBin = (
  start: number,
  end: number,
  count: number,
  normalizedCount?: number
): HistogramBin => ({
  start,
  end,
  count,
  normalizedCount,
});
