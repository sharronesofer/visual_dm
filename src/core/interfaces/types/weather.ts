// Weather system types and interfaces

export type WeatherType =
  | 'clear'
  | 'rain'
  | 'storm'
  | 'snow'
  | 'fog'
  | 'sandstorm'
  | 'heatwave'
  | 'blizzard';

export type WeatherIntensity = 'light' | 'moderate' | 'heavy' | 'extreme';

export interface WeatherEffect {
  type: 'visibility' | 'movement' | 'combat' | 'status';
  value: number; // Modifier value
  description: string;
}

export interface WeatherState {
  type: WeatherType;
  intensity: WeatherIntensity;
  duration: number; // In game time units
  effects: WeatherEffect[];
  visualEffects: {
    particleSystem?: string;
    shader?: string;
    lighting?: {
      brightness: number;
      color: string;
    };
  };
}

export interface RegionWeather {
  current: WeatherState;
  forecast: WeatherState[]; // Future weather states
  lastUpdated: number; // Timestamp
}

export interface WeatherSystemState {
  regions: Record<string, RegionWeather>; // Region ID -> Weather data
  globalEffects: WeatherEffect[];
  transitionState?: {
    from: WeatherState;
    to: WeatherState;
    progress: number; // 0-1
  };
}

// Weather generation parameters
export interface WeatherParams {
  region: string;
  biome: 'temperate' | 'desert' | 'tundra' | 'coastal' | 'tropical';
  season: 'spring' | 'summer' | 'fall' | 'winter';
  altitude: number;
  forceWeather?: {
    type: WeatherType;
    intensity: WeatherIntensity;
  };
}

// Weather system configuration
export interface WeatherConfig {
  transitionDuration: number; // How long weather transitions take
  updateInterval: number; // How often to update weather
  forecastLength: number; // How many future weather states to generate
  intensityThresholds: Record<WeatherIntensity, number>;
  seasonalWeights: Record<string, Record<WeatherType, number>>;
  terrainWeights: Record<string, Record<WeatherType, number>>;
}

// --- Weather System Performance Monitoring ---

export interface WeatherPerformanceData {
  timestamp: number;
  frameTime: number; // ms
  memoryUsage: number; // percent
  gpuUsage?: number; // percent, optional if available
  heapUsage?: number; // bytes, optional
  [metric: string]: number | undefined;
}

export interface WeatherPerformanceThresholds {
  frameTime: number; // ms
  memoryUsage: number; // percent
  gpuUsage?: number; // percent
  heapUsage?: number; // bytes
  [metric: string]: number | undefined;
}

// --- Fallback System Types ---
export enum FallbackTier {
  NORMAL = 'normal',
  DEGRADED = 'degraded',
  EMERGENCY = 'emergency',
}

export interface WeatherFallbackConfig {
  thresholds: {
    frameTime: { degraded: number; emergency: number };
    memory: { degraded: number; emergency: number };
    gpu?: { degraded: number; emergency: number };
  };
  hysteresis: number;
  recoveryDelayMs: number;
  perEffectOverrides?: Record<string, Partial<WeatherFallbackConfig>>;
}

// --- Resource Management Configuration ---

/**
 * WeatherResourceConfig: Centralized configuration for all weather resource management systems.
 * Serializable and supports hardware tier presets.
 */
export interface WeatherResourceConfig {
  poolSizes: Record<string, number>; // effectType -> pool size
  lodThresholds: {
    frameTime: Record<string, number>; // LOD level -> ms
    memoryUsage: Record<string, number>; // LOD level -> %
    gpuUsage?: Record<string, number>; // LOD level -> %
  };
  fallbackThresholds: {
    frameTime: { degraded: number; emergency: number };
    memory: { degraded: number; emergency: number };
    gpu?: { degraded: number; emergency: number };
  };
  assetPreloadCount: number;
  cullingDistances: Record<string, number>; // effectType -> max distance
  enableDebugOverlays: boolean;
  [key: string]: any;
}

/**
 * Preset configurations for different hardware tiers.
 */
export const WEATHER_RESOURCE_PRESETS: Record<string, WeatherResourceConfig> = {
  ultra: {
    poolSizes: { rain: 2000, snow: 1600, fog: 800 },
    lodThresholds: {
      frameTime: { ultra: 12, high: 16, medium: 24, low: 33, verylow: 40 },
      memoryUsage: { ultra: 50, high: 60, medium: 80, low: 90, verylow: 95 },
      gpuUsage: { ultra: 50, high: 60, medium: 80, low: 90, verylow: 95 },
    },
    fallbackThresholds: {
      frameTime: { degraded: 40, emergency: 60 },
      memory: { degraded: 90, emergency: 98 },
      gpu: { degraded: 90, emergency: 98 },
    },
    assetPreloadCount: 10,
    cullingDistances: { rain: 200, snow: 180, fog: 120 },
    enableDebugOverlays: false,
  },
  high: {
    poolSizes: { rain: 1000, snow: 800, fog: 400 },
    lodThresholds: {
      frameTime: { ultra: 16, high: 20, medium: 28, low: 36, verylow: 44 },
      memoryUsage: { ultra: 60, high: 70, medium: 85, low: 92, verylow: 97 },
      gpuUsage: { ultra: 60, high: 70, medium: 85, low: 92, verylow: 97 },
    },
    fallbackThresholds: {
      frameTime: { degraded: 44, emergency: 64 },
      memory: { degraded: 92, emergency: 99 },
      gpu: { degraded: 92, emergency: 99 },
    },
    assetPreloadCount: 6,
    cullingDistances: { rain: 120, snow: 100, fog: 80 },
    enableDebugOverlays: false,
  },
  medium: {
    poolSizes: { rain: 500, snow: 400, fog: 200 },
    lodThresholds: {
      frameTime: { ultra: 20, high: 24, medium: 32, low: 40, verylow: 48 },
      memoryUsage: { ultra: 70, high: 80, medium: 90, low: 95, verylow: 98 },
      gpuUsage: { ultra: 70, high: 80, medium: 90, low: 95, verylow: 98 },
    },
    fallbackThresholds: {
      frameTime: { degraded: 48, emergency: 68 },
      memory: { degraded: 95, emergency: 99 },
      gpu: { degraded: 95, emergency: 99 },
    },
    assetPreloadCount: 3,
    cullingDistances: { rain: 80, snow: 60, fog: 40 },
    enableDebugOverlays: false,
  },
  low: {
    poolSizes: { rain: 100, snow: 80, fog: 40 },
    lodThresholds: {
      frameTime: { ultra: 24, high: 28, medium: 36, low: 44, verylow: 52 },
      memoryUsage: { ultra: 80, high: 90, medium: 95, low: 98, verylow: 99 },
      gpuUsage: { ultra: 80, high: 90, medium: 95, low: 98, verylow: 99 },
    },
    fallbackThresholds: {
      frameTime: { degraded: 52, emergency: 72 },
      memory: { degraded: 98, emergency: 100 },
      gpu: { degraded: 98, emergency: 100 },
    },
    assetPreloadCount: 1,
    cullingDistances: { rain: 40, snow: 30, fog: 20 },
    enableDebugOverlays: false,
  },
}; 