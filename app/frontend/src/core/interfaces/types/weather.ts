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