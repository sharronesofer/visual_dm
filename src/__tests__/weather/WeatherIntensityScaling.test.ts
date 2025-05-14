import { WeatherSystem } from '../../systems/WeatherSystem';
import { WeatherEffectSystem } from '../../systems/WeatherEffectSystem';
import { CombatSystem } from '../../systems/CombatSystem';
import { Character } from '../../entities/Character';
import { WeatherType, WeatherIntensity, WeatherEffect, WeatherParams, WeatherState, StatusEffect } from '../../types/weather';
import { MovementState } from '../../types/movement';
import { CombatStats } from '../../types/combat';

describe('Weather Intensity Scaling', () => {
  let weatherSystem: WeatherSystem;
  let effectSystem: WeatherEffectSystem;

  beforeEach(() => {
    weatherSystem = new WeatherSystem();
    effectSystem = new WeatherEffectSystem();
  });

  describe('Effect Scaling', () => {
    it('should scale movement effects proportionally with intensity', () => {
      const regionId = 'test-region';
      const baseMovementState: MovementState = {
        speed: 100,
        staminaCost: 10
      };

      const params: WeatherParams = {
        region: regionId,
        season: 'winter',
        terrain: { plains: 1 }
      };

      // Initialize region
      weatherSystem.initializeRegion(regionId, params);
      const weather = weatherSystem.getRegionWeather(regionId);
      expect(weather).not.toBeNull();

      if (weather) {
        // Get current effects
        const effects = weather.current.effects;
        const movementEffects = effects.filter(e => e.type === 'movement');

        if (movementEffects.length > 0) {
          // Test that movement penalties scale with intensity
          const modifiedState = effectSystem.modifyMovementStats(regionId, baseMovementState);
          expect(modifiedState.speed).not.toBe(baseMovementState.speed);
          expect(modifiedState.staminaCost).not.toBe(baseMovementState.staminaCost);

          // Verify scaling matches intensity multipliers
          const intensity = weather.current.intensity;
          const expectedMultiplier = {
            light: 0.5,
            moderate: 1.0,
            heavy: 1.5,
            extreme: 2.0
          }[intensity];

          const effect = movementEffects[0];
          const expectedSpeedModifier = 1 + (effect.value * expectedMultiplier);
          expect(modifiedState.speed / baseMovementState.speed).toBeCloseTo(expectedSpeedModifier, 2);
        }
      }
    });

    it('should scale visual effects with intensity', () => {
      const regionId = 'test-region';
      const params: WeatherParams = {
        region: regionId,
        season: 'winter',
        terrain: { plains: 1 }
      };

      // Initialize region
      weatherSystem.initializeRegion(regionId, params);
      const weather = weatherSystem.getRegionWeather(regionId);
      expect(weather).not.toBeNull();

      if (weather) {
        const { visualEffects, intensity } = weather.current;
        expect(visualEffects).toBeDefined();

        // Test lighting adjustments based on intensity
        if (visualEffects.lighting) {
          const intensityValue = {
            light: 0.25,
            moderate: 0.5,
            heavy: 0.75,
            extreme: 1.0
          }[intensity];

          // Different weather types adjust brightness differently
          switch (weather.current.type) {
            case 'rain':
              expect(visualEffects.lighting.brightness).toBeCloseTo(1.0 - intensityValue * 0.3, 2);
              expect(visualEffects.lighting.color).toBe('#8FA5B3');
              break;
            case 'storm':
              expect(visualEffects.lighting.brightness).toBeCloseTo(1.0 - intensityValue * 0.5, 2);
              expect(visualEffects.lighting.color).toBe('#4A545C');
              break;
            case 'snow':
              expect(visualEffects.lighting.brightness).toBeCloseTo(1.0 + intensityValue * 0.2, 2);
              expect(visualEffects.lighting.color).toBe('#E8F0FF');
              break;
            case 'fog':
              expect(visualEffects.lighting.brightness).toBeCloseTo(1.0 - intensityValue * 0.2, 2);
              expect(visualEffects.lighting.color).toBe('#D4D4D4');
              break;
          }
        }

        // Test particle system presence
        if (['rain', 'storm', 'snow', 'blizzard', 'sandstorm'].includes(weather.current.type)) {
          expect(visualEffects.particleSystem).toBeDefined();
        }

        // Test shader presence
        expect(visualEffects.shader).toBeDefined();
      }
    });

    it('should scale sound effects with intensity', () => {
      const regionId = 'test-region';
      const intensities: WeatherIntensity[] = ['light', 'moderate', 'heavy', 'extreme'];
      
      const testWeatherTypes: WeatherType[] = ['rain', 'storm', 'snow', 'blizzard'];
      
      testWeatherTypes.forEach(weatherType => {
        intensities.forEach((intensity) => {
          const weather: WeatherState = {
            type: weatherType,
            intensity,
            duration: 1000,
            effects: [],
            visualEffects: weatherSystem['getVisualEffects'](weatherType, intensity)
          };

          effectSystem.setRegionEffects(regionId, weather);
          const effects = effectSystem.getRegionEffects(regionId);

          // Verify sound effects are present and scale with intensity
          const soundEffect = effects.find(e => e.type === 'status' && e.description.includes('sound'));
          expect(soundEffect).toBeDefined();
          if (soundEffect) {
            expect(Math.abs(soundEffect.value)).toBeCloseTo(
              intensity === 'light' ? 0.25 :
              intensity === 'moderate' ? 0.5 :
              intensity === 'heavy' ? 0.75 : 1.0,
              1
            );
          }
        });
      });
    });

    it('should scale visibility effects proportionally with intensity', () => {
      const regionId = 'test-region';
      const baseVisibilityRange = 100;

      const intensities: WeatherIntensity[] = ['light', 'moderate', 'heavy', 'extreme'];
      const multipliers = {
        light: 0.5,
        moderate: 1.0,
        heavy: 1.5,
        extreme: 2.0
      };

      // Test each intensity level with fog (highest visibility impact)
      intensities.forEach(intensity => {
        const params: WeatherParams = {
          region: regionId,
          biome: 'temperate',
          season: 'spring',
          altitude: 0,
          forceWeather: {
            type: 'fog',
            intensity
          }
        };

        weatherSystem.initializeRegion(regionId, params);
        const weather = weatherSystem.getRegionWeather(regionId);
        expect(weather).not.toBeNull();

        if (weather) {
          effectSystem.setRegionEffects(regionId, weather.current);

          // Base visibility penalty for fog is -0.6
          const expectedMultiplier = 1 + (-0.6 * multipliers[intensity]);
          const modifiedVisibility = effectSystem.calculateVisibilityRange(regionId, baseVisibilityRange);

          expect(modifiedVisibility).toBeCloseTo(baseVisibilityRange * expectedMultiplier, 1);
        }
      });
    });

    it('should handle transitions between intensity levels smoothly', () => {
      const regionId = 'test-region';
      const params: WeatherParams = {
        season: 'spring',
        terrain: { plains: 1 }
      };

      // Initialize region
      weatherSystem.initializeRegion(regionId, params);
      
      // Start weather system to allow transitions
      weatherSystem.start();

      return new Promise<void>(resolve => {
        setTimeout(() => {
          const weather = weatherSystem.getRegionWeather(regionId);
          expect(weather).not.toBeNull();

          if (weather) {
            // Verify weather has transitioned
            expect(weather.lastUpdated).toBeGreaterThan(0);
            
            // Check effects are still properly scaled
            const effects = weatherSystem.getRegionEffects(regionId);
            expect(effects.length).toBeGreaterThan(0);
          }

          weatherSystem.stop();
          resolve();
        }, 1000);
      });
    });
  });

  describe('Weather Duration', () => {
    it('should adjust duration based on intensity', () => {
      const testCases: Array<[WeatherType, WeatherIntensity]> = [
        ['clear', 'light'],
        ['rain', 'moderate'],
        ['storm', 'heavy'],
        ['blizzard', 'extreme']
      ];

      testCases.forEach(([type, intensity]) => {
        const params: WeatherParams = {
          region: 'test',
          biome: 'temperate',
          season: 'spring',
          altitude: 0,
          forceWeather: {
            type,
            intensity
          }
        };

        weatherSystem.initializeRegion('test', params);
        const weather = weatherSystem.getRegionWeather('test');

        expect(weather).not.toBeNull();
        if (weather) {
          const duration = weather.current.duration;

          // Duration should be within reasonable bounds
          expect(duration).toBeGreaterThanOrEqual(300);  // At least 5 minutes
          expect(duration).toBeLessThanOrEqual(7200);    // At most 2 hours

          // More intense weather should have shorter duration
          if (intensity === 'extreme' || intensity === 'heavy') {
            const lightParams = { ...params };
            lightParams.forceWeather = { type, intensity: 'light' };
            weatherSystem.initializeRegion('test-light', lightParams);
            const lightWeather = weatherSystem.getRegionWeather('test-light');

            if (lightWeather) {
              expect(lightWeather.current.duration).toBeGreaterThan(duration);
            }
          }
        }
      });
    });
  });

  describe('Effect Transitions', () => {
    it('should transition effects smoothly between intensities', () => {
      const params: WeatherParams = {
        region: 'test',
        biome: 'temperate',
        season: 'spring',
        altitude: 0,
        forceWeather: {
          type: 'rain',
          intensity: 'light'
        }
      };

      weatherSystem.initializeRegion('test', params);
      const initialWeather = weatherSystem.getRegionWeather('test');
      expect(initialWeather).not.toBeNull();

      if (initialWeather) {
        const initialMovementEffect = initialWeather.current.effects.find(e => e.type === 'movement');
        expect(initialMovementEffect).toBeDefined();

        // Change to heavy intensity
        weatherSystem.updateRegionWeather('test', {
          ...params,
          forceWeather: {
            type: 'rain',
            intensity: 'heavy'
          }
        });

        // Get mid-transition state
        const midTransitionWeather = weatherSystem.getRegionWeather('test');
        expect(midTransitionWeather).not.toBeNull();

        if (midTransitionWeather && initialMovementEffect) {
          const midTransitionMovementEffect = midTransitionWeather.current.effects.find(e => e.type === 'movement');
          expect(midTransitionMovementEffect).toBeDefined();

          if (midTransitionMovementEffect) {
            // Mid-transition value should be between initial and final values
            const initialValue = initialMovementEffect.value;
            const finalValue = -0.2 * 1.5; // Base * heavy multiplier
            expect(midTransitionMovementEffect.value).toBeLessThan(initialValue);
            expect(midTransitionMovementEffect.value).toBeGreaterThan(finalValue);
          }
        }
      }
    });
  });

  describe('Combat Effect Scaling', () => {
    let combatSystem: CombatSystem;
    let character: Character;

    beforeEach(() => {
      combatSystem = new CombatSystem();
      character = new Character();
    });

    it('should scale combat modifiers with weather intensity', () => {
      const regionId = 'test-region';
      const testCases: Array<{
        type: WeatherType;
        effects: Record<WeatherIntensity, { accuracy: number; evasion: number; }>
      }> = [
        {
          type: 'rain',
          effects: {
            light: { accuracy: -0.05, evasion: 0.05 },
            moderate: { accuracy: -0.10, evasion: 0.10 },
            heavy: { accuracy: -0.20, evasion: 0.15 },
            extreme: { accuracy: -0.30, evasion: 0.20 }
          }
        },
        {
          type: 'fog',
          effects: {
            light: { accuracy: -0.10, evasion: 0.10 },
            moderate: { accuracy: -0.20, evasion: 0.15 },
            heavy: { accuracy: -0.30, evasion: 0.20 },
            extreme: { accuracy: -0.40, evasion: 0.25 }
          }
        }
      ];

      testCases.forEach(({ type, effects }) => {
        Object.entries(effects).forEach(([intensity, expected]) => {
          const weather: WeatherState = {
            type,
            intensity: intensity as WeatherIntensity,
            duration: 1000,
            effects: []
          };

          weatherSystem.setRegionWeather(regionId, weather);
          const combatStats = combatSystem.calculateCombatStats(character, regionId);

          expect(combatStats.accuracyModifier).toBeCloseTo(expected.accuracy, 2);
          expect(combatStats.evasionModifier).toBeCloseTo(expected.evasion, 2);
        });
      });
    });

    it('should apply appropriate combat penalties in extreme conditions', () => {
      const regionId = 'test-region';
      const extremeWeather: WeatherState = {
        type: 'blizzard',
        intensity: 'extreme',
        duration: 1000,
        effects: []
      };

      weatherSystem.setRegionWeather(regionId, extremeWeather);
      const combatStats = combatSystem.calculateCombatStats(character, regionId);

      // Extreme conditions should significantly impact combat
      expect(combatStats.accuracyModifier).toBeLessThan(-0.4);
      expect(combatStats.evasionModifier).toBeGreaterThan(0.2);
      expect(combatStats.damageModifier).toBeLessThan(0.8);
    });
  });

  describe('Status Effect Scaling', () => {
    let character: Character;

    beforeEach(() => {
      character = new Character();
    });

    it('should scale status effect intensity with weather intensity', () => {
      const regionId = 'test-region';
      const testCases: Array<{
        type: WeatherType;
        effects: Record<WeatherIntensity, Record<string, number>>;
      }> = [
        {
          type: 'rain',
          effects: {
            light: { wet: 0.3, chilled: 0.0 },
            moderate: { wet: 0.6, chilled: 0.2 },
            heavy: { wet: 0.8, chilled: 0.4 },
            extreme: { wet: 1.0, chilled: 0.6 }
          }
        },
        {
          type: 'snow',
          effects: {
            light: { chilled: 0.3, frozen: 0.0 },
            moderate: { chilled: 0.6, frozen: 0.2 },
            heavy: { chilled: 0.8, frozen: 0.4 },
            extreme: { chilled: 1.0, frozen: 0.6 }
          }
        }
      ];

      testCases.forEach(({ type, effects }) => {
        Object.entries(effects).forEach(([intensity, expected]) => {
          const weather: WeatherState = {
            type,
            intensity: intensity as WeatherIntensity,
            duration: 1000,
            effects: []
          };

          weatherSystem.setRegionWeather(regionId, weather);
          const statusEffects = effectSystem.calculateStatusEffects(character, regionId);

          Object.entries(expected).forEach(([effect, value]) => {
            const statusEffect = statusEffects.find(e => e.type === effect.toUpperCase());
            expect(statusEffect?.intensity).toBeCloseTo(value, 2);
          });
        });
      });
    });

    it('should stack multiple weather-induced status effects', () => {
      const regionId = 'test-region';
      const weather: WeatherState = {
        type: 'storm',
        intensity: 'extreme',
        duration: 1000,
        effects: []
      };

      weatherSystem.setRegionWeather(regionId, weather);
      const statusEffects = effectSystem.calculateStatusEffects(character, regionId);

      // Storm should apply both wet and chilled effects
      const wetEffect = statusEffects.find(e => e.type === 'WET');
      const chilledEffect = statusEffects.find(e => e.type === 'CHILLED');

      expect(wetEffect).toBeDefined();
      expect(chilledEffect).toBeDefined();
      expect(wetEffect?.intensity).toBeGreaterThan(0.8);
      expect(chilledEffect?.intensity).toBeGreaterThan(0.4);
    });
  });

  describe('Environmental Interaction', () => {
    it('should scale weather effects based on environmental conditions', () => {
      const regionId = 'test-region';
      const testCases: Array<{
        weather: WeatherType;
        intensity: WeatherIntensity;
        season: string;
        expected: {
          temperatureModifier: number;
          humidityModifier: number;
        };
      }> = [
        {
          weather: 'rain',
          intensity: 'heavy',
          season: 'summer',
          expected: {
            temperatureModifier: -4.0,
            humidityModifier: 0.6
          }
        },
        {
          weather: 'snow',
          intensity: 'heavy',
          season: 'winter',
          expected: {
            temperatureModifier: -8.0,
            humidityModifier: 0.3
          }
        }
      ];

      testCases.forEach(({ weather, intensity, season, expected }) => {
        const params: WeatherParams = {
          region: regionId,
          season,
          terrain: { plains: 1 }
        };

        const weatherState: WeatherState = {
          type: weather,
          intensity,
          duration: 1000,
          effects: []
        };

        weatherSystem.initializeRegion(regionId, params);
        weatherSystem.setRegionWeather(regionId, weatherState);
        const effects = weatherSystem.getRegionEffects(regionId);

        const tempEffect = effects.find(e => e.type === 'temperature');
        const humidityEffect = effects.find(e => e.type === 'humidity');

        expect(tempEffect?.value).toBeCloseTo(expected.temperatureModifier, 1);
        expect(humidityEffect?.value).toBeCloseTo(expected.humidityModifier, 1);
      });
    });
  });
}); 