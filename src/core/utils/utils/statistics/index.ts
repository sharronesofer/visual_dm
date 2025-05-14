import {
  POIMetrics,
  TimeSeriesDataPoint,
  TimeSeriesConfig,
  TimeSeriesAnalysis,
  HistogramConfig,
  HistogramBin,
  HistogramAnalysis,
  createTimeSeriesDataPoint,
  createHistogramBin,
} from '../../types/statistics';

/**
 * Calculates the average of an array of numbers
 */
export const calculateAverage = (values: number[]): number => {
  if (values.length === 0) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
};

/**
 * Calculates the median of an array of numbers
 */
export const calculateMedian = (values: number[]): number => {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
};

/**
 * Calculates the standard deviation of an array of numbers
 */
export const calculateStandardDeviation = (values: number[]): number => {
  if (values.length === 0) return 0;
  const avg = calculateAverage(values);
  const squareDiffs = values.map(value => Math.pow(value - avg, 2));
  return Math.sqrt(calculateAverage(squareDiffs));
};

/**
 * Analyzes time series data
 */
export const analyzeTimeSeries = (
  data: TimeSeriesDataPoint[],
  config: TimeSeriesConfig
): TimeSeriesAnalysis => {
  if (data.length === 0) {
    return {
      data: [],
      trend: 'stable',
      average: 0,
      min: 0,
      max: 0,
    };
  }

  // Sort data by timestamp
  const sortedData = [...data].sort((a, b) => a.timestamp - b.timestamp);

  // Group data by interval
  const groupedData = new Map<number, number[]>();
  sortedData.forEach(point => {
    const intervalStart =
      Math.floor(point.timestamp / config.interval) * config.interval;
    const values = groupedData.get(intervalStart) || [];
    values.push(point.value);
    groupedData.set(intervalStart, values);
  });

  // Aggregate data points
  const aggregatedData = Array.from(groupedData.entries()).map(
    ([timestamp, values]) => {
      let value: number;
      switch (config.aggregation) {
        case 'sum':
          value = values.reduce((sum, v) => sum + v, 0);
          break;
        case 'min':
          value = Math.min(...values);
          break;
        case 'max':
          value = Math.max(...values);
          break;
        case 'average':
        default:
          value = calculateAverage(values);
      }
      return createTimeSeriesDataPoint(timestamp, value);
    }
  );

  // Apply smoothing if configured
  const smoothedData = config.smoothing
    ? aggregatedData.map((point, i) => {
        if (i === 0 || i === aggregatedData.length - 1) return point;
        const prevValue = aggregatedData[i - 1].value;
        const nextValue = aggregatedData[i + 1].value;
        const smoothedValue =
          prevValue * config.smoothing! +
          point.value * (1 - 2 * config.smoothing!) +
          nextValue * config.smoothing!;
        return createTimeSeriesDataPoint(point.timestamp, smoothedValue);
      })
    : aggregatedData;

  // Calculate trend
  const values = smoothedData.map(point => point.value);
  const firstValue = values[0];
  const lastValue = values[values.length - 1];
  const trend =
    lastValue > firstValue * 1.1
      ? 'increasing'
      : lastValue < firstValue * 0.9
        ? 'decreasing'
        : 'stable';

  return {
    data: smoothedData,
    trend,
    average: calculateAverage(values),
    min: Math.min(...values),
    max: Math.max(...values),
  };
};

/**
 * Generates a histogram from an array of numbers
 */
export const generateHistogram = (
  values: number[],
  config: HistogramConfig
): HistogramAnalysis => {
  if (values.length === 0) {
    return {
      bins: [],
      total: 0,
      average: 0,
      median: 0,
      standardDeviation: 0,
    };
  }

  // Determine range
  const min = config.range ? config.range[0] : Math.min(...values);
  const max = config.range ? config.range[1] : Math.max(...values);
  const range = max - min;
  const binWidth = range / config.bins;

  // Initialize bins
  const bins: HistogramBin[] = Array.from({ length: config.bins }, (_, i) => {
    const start = min + i * binWidth;
    const end = start + binWidth;
    return createHistogramBin(start, end, 0);
  });

  // Count values in each bin
  values.forEach(value => {
    const binIndex = Math.min(
      Math.floor(((value - min) / range) * config.bins),
      config.bins - 1
    );
    bins[binIndex].count++;
  });

  // Normalize if requested
  if (config.normalize) {
    const maxCount = Math.max(...bins.map(bin => bin.count));
    bins.forEach(bin => {
      bin.normalizedCount = bin.count / maxCount;
    });
  }

  return {
    bins,
    total: values.length,
    average: calculateAverage(values),
    median: calculateMedian(values),
    standardDeviation: calculateStandardDeviation(values),
  };
};
