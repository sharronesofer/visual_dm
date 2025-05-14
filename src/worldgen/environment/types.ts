export type WeatherType = 'clear' | 'rain' | 'snow' | 'fog' | 'storm' | 'windy';

export interface WeatherPattern {
  type: WeatherType;
  intensity: number; // 0-1
  region: string;
  duration: number; // in minutes
}

export type HazardType = 'flood' | 'avalanche' | 'radiation' | 'fire' | 'storm';

export interface Hazard {
  id: string;
  type: HazardType;
  region: string;
  x: number;
  y: number;
  severity: number; // 0-1
  active: boolean;
}

export interface Region {
  id: string;
  name: string;
  climate: string;
}

export interface EnvironmentalState {
  weather: WeatherPattern;
  hazards: Hazard[];
  season: string;
  time: number;
} 