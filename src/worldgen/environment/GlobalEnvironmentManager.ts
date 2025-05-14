import { EnvironmentalState } from './types';
import { WeatherSystem } from './WeatherSystem';
import { HazardSystem } from './HazardSystem';

export class GlobalEnvironmentManager {
  private weatherSystem = new WeatherSystem();
  private hazardSystem = new HazardSystem();

  generate(region: string, season: string, time: number): EnvironmentalState {
    const weather = this.weatherSystem.generate(region);
    const hazards = this.hazardSystem.generate(region);
    return {
      weather,
      hazards,
      season,
      time
    };
  }
} 