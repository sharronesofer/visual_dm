import { WeatherSystem } from '../../systems/WeatherSystem';
import { WeatherType, WeatherIntensity, WeatherState, WeatherParams } from '../../types/weather';

describe('WeatherSystem', () => {
  let weatherSystem: WeatherSystem;

  beforeEach(() => {
    weatherSystem = new WeatherSystem();
  });

  describe('Weather Management', () => {
    it('should initialize and update region weather', () => {
      const params: WeatherParams = {
        season: 'spring',
        terrain: { plains: 1 }
      };

      weatherSystem.initializeRegion('region1', params);
      const weather = weatherSystem.getRegionWeather('region1');
      
      expect(weather).not.toBeNull();
      if (weather) {
        expect(weather.current).toBeDefined();
        expect(weather.current.type).toBeDefined();
        expect(weather.current.intensity).toBeDefined();
        expect(weather.current.effects).toBeInstanceOf(Array);
      }
    });

    it('should respect seasonal and terrain conditions', () => {
      // Initialize summer desert region
      weatherSystem.initializeRegion('summer_region', {
        season: 'summer',
        terrain: { desert: 1 }
      });

      // Initialize winter mountain region
      weatherSystem.initializeRegion('winter_region', {
        season: 'winter',
        terrain: { mountain: 1 }
      });

      const summerWeather = weatherSystem.getRegionWeather('summer_region');
      const winterWeather = weatherSystem.getRegionWeather('winter_region');

      expect(summerWeather).not.toBeNull();
      expect(winterWeather).not.toBeNull();

      if (summerWeather && winterWeather) {
        // Summer desert region should have appropriate weather types
        expect(['clear', 'sandstorm', 'heatwave']).toContain(summerWeather.current.type);

        // Winter mountain region should have appropriate weather types
        expect(['snow', 'blizzard', 'clear']).toContain(winterWeather.current.type);
      }
    });

    it('should generate appropriate effects based on conditions', () => {
      weatherSystem.initializeRegion('storm_region', {
        season: 'autumn',
        terrain: { plains: 1 },
        previousWeather: {
          type: 'storm',
          intensity: 'heavy',
          duration: 1000,
          effects: [],
          visualEffects: {}
        }
      });

      const weather = weatherSystem.getRegionWeather('storm_region');
      expect(weather).not.toBeNull();

      if (weather) {
        const effects = weather.current.effects;
        expect(effects.some(e => e.type === 'visibility')).toBeTruthy();
        expect(effects.some(e => e.type === 'movement')).toBeTruthy();
      }
    });
  });

  describe('Region Management', () => {
    it('should track weather for multiple regions', () => {
      weatherSystem.initializeRegion('region1', {
        season: 'summer',
        terrain: { plains: 1 }
      });

      weatherSystem.initializeRegion('region2', {
        season: 'summer',
        terrain: { desert: 1 }
      });

      const weather1 = weatherSystem.getRegionWeather('region1');
      const weather2 = weatherSystem.getRegionWeather('region2');

      expect(weather1).not.toBeNull();
      expect(weather2).not.toBeNull();
      
      if (weather1 && weather2) {
        expect(weather1).not.toEqual(weather2);
      }
    });

    it('should update weather based on time', () => {
      weatherSystem.initializeRegion('time_test', {
        season: 'summer',
        terrain: { plains: 1 }
      });

      const initial = weatherSystem.getRegionWeather('time_test');
      expect(initial).not.toBeNull();

      if (initial) {
        const initialTime = initial.lastUpdated;

        // Start weather system and wait for update
        weatherSystem.start();
        
        // Wait for one update cycle
        return new Promise<void>(resolve => {
          setTimeout(() => {
            const updated = weatherSystem.getRegionWeather('time_test');
            expect(updated).not.toBeNull();

            if (updated) {
              expect(updated.lastUpdated).toBeGreaterThan(initialTime);
            }

            weatherSystem.stop();
            resolve();
          }, 1000);
        });
      }
    });
  });

  describe('Performance', () => {
    it('should handle rapid weather updates efficiently', () => {
      const startTime = performance.now();
      
      for (let i = 0; i < 100; i++) {
        weatherSystem.initializeRegion(`perf_test_${i}`, {
          season: 'summer',
          terrain: { plains: 1 }
        });
      }

      const endTime = performance.now();
      const duration = endTime - startTime;

      expect(duration).toBeLessThan(1000); // Should take less than 1 second
    });

    it('should efficiently manage many regions', () => {
      const startTime = performance.now();

      // Initialize many regions
      for (let i = 0; i < 100; i++) {
        weatherSystem.initializeRegion(`perf_test_${i}`, {
          season: 'summer',
          terrain: { plains: 1 }
        });
      }

      // Start weather system and wait for update
      weatherSystem.start();
      
      return new Promise<void>(resolve => {
        setTimeout(() => {
          const endTime = performance.now();
          const duration = endTime - startTime;

          expect(duration).toBeLessThan(500); // Should take less than 500ms

          weatherSystem.stop();
          resolve();
        }, 1000);
      });
    });
  });
}); 