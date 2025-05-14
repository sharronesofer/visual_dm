export interface PriceStats {
  average: number;
  min: number;
  max: number;
  trend: 'rising' | 'falling' | 'stable';
  volatility: number;
  lastUpdate: number;
} 