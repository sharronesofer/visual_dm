from typing import Any, List


  POIMetrics,
  TimeSeriesDataPoint,
  TimeSeriesConfig,
  TimeSeriesAnalysis,
  HistogramConfig,
  HistogramBin,
  HistogramAnalysis,
  createTimeSeriesDataPoint,
  createHistogramBin,
} from '../../types/statistics'
/**
 * Calculates the average of an array of numbers
 */
const calculateAverage = (values: List[number]): float => {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}
/**
 * Calculates the median of an array of numbers
 */
const calculateMedian = (values: List[number]): float => {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle]
}
/**
 * Calculates the standard deviation of an array of numbers
 */
const calculateStandardDeviation = (values: List[number]): float => {
  if (values.length === 0) return 0
  const avg = calculateAverage(values)
  const squareDiffs = values.map(value => Math.pow(value - avg, 2))
  return Math.sqrt(calculateAverage(squareDiffs))
}
/**
 * Analyzes time series data
 */
const analyzeTimeSeries = (
  data: List[TimeSeriesDataPoint],
  config: TimeSeriesConfig
): TimeSeriesAnalysis => {
  if (data.length === 0) {
    return {
      data: [],
      trend: 'stable',
      average: 0,
      min: 0,
      max: 0,
    }
  }
  const sortedData = [...data].sort((a, b) => a.timestamp - b.timestamp)
  const groupedData = new Map<number, number[]>()
  sortedData.forEach(point => {
    const intervalStart =
      Math.floor(point.timestamp / config.interval) * config.interval
    const values = groupedData.get(intervalStart) || []
    values.push(point.value)
    groupedData.set(intervalStart, values)
  })
  const aggregatedData = Array.from(groupedData.entries()).map(
    ([timestamp, values]) => {
      let value: float
      switch (config.aggregation) {
        case 'sum':
          value = values.reduce((sum, v) => sum + v, 0)
          break
        case 'min':
          value = Math.min(...values)
          break
        case 'max':
          value = Math.max(...values)
          break
        case 'average':
        default:
          value = calculateAverage(values)
      }
      return createTimeSeriesDataPoint(timestamp, value)
    }
  )
  const smoothedData = config.smoothing
    ? aggregatedData.map((point, i) => {
        if (i === 0 || i === aggregatedData.length - 1) return point
        const prevValue = aggregatedData[i - 1].value
        const nextValue = aggregatedData[i + 1].value
        const smoothedValue =
          prevValue * config.smoothing! +
          point.value * (1 - 2 * config.smoothing!) +
          nextValue * config.smoothing!
        return createTimeSeriesDataPoint(point.timestamp, smoothedValue)
      })
    : aggregatedData
  const values = smoothedData.map(point => point.value)
  const firstValue = values[0]
  const lastValue = values[values.length - 1]
  const trend =
    lastValue > firstValue * 1.1
      ? 'increasing'
      : lastValue < firstValue * 0.9
        ? 'decreasing'
        : 'stable'
  return {
    data: smoothedData,
    trend,
    average: calculateAverage(values),
    min: Math.min(...values),
    max: Math.max(...values),
  }
}
/**
 * Generates a histogram from an array of numbers
 */
const generateHistogram = (
  values: List[number],
  config: HistogramConfig
): HistogramAnalysis => {
  if (values.length === 0) {
    return {
      bins: [],
      total: 0,
      average: 0,
      median: 0,
      standardDeviation: 0,
    }
  }
  const min = config.range ? config.range[0] : Math.min(...values)
  const max = config.range ? config.range[1] : Math.max(...values)
  const range = max - min
  const binWidth = range / config.bins
  const bins: List[HistogramBin] = Array.from({ length: config.bins }, (_, i) => {
    const start = min + i * binWidth
    const end = start + binWidth
    return createHistogramBin(start, end, 0)
  })
  values.forEach(value => {
    const binIndex = Math.min(
      Math.floor(((value - min) / range) * config.bins),
      config.bins - 1
    )
    bins[binIndex].count++
  })
  if (config.normalize) {
    const maxCount = Math.max(...bins.map(bin => bin.count))
    bins.forEach(bin => {
      bin.normalizedCount = bin.count / maxCount
    })
  }
  return {
    bins,
    total: values.length,
    average: calculateAverage(values),
    median: calculateMedian(values),
    standardDeviation: calculateStandardDeviation(values),
  }
}