import { WeatherPattern, WeatherType } from './types';

const weatherTypes: WeatherType[] = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy'];

export class WeatherSystem {
  generate(region: string): WeatherPattern {
    const type = weatherTypes[Math.floor(Math.random() * weatherTypes.length)];
    const intensity = Math.random();
    const duration = 30 + Math.floor(Math.random() * 90); // 30-120 min
    return {
      type,
      intensity,
      region,
      duration
    };
  }
} 