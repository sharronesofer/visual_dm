import { WeatherSystem } from '../../systems/WeatherSystem';
import { WeatherEffectSystem } from '../../systems/WeatherEffectSystem';
import { GameStateManager } from '../../systems/GameStateManager';
import { SceneManager } from '../../systems/SceneManager';
import { WeatherType, WeatherIntensity, WeatherEffect, WeatherParams, GameView } from '../../types/weather';
import { MovementState } from '../../types/movement';

describe('Weather System Consistency', () => {
  let weatherSystem: WeatherSystem;
  let effectSystem: WeatherEffectSystem;

  beforeEach(() => {
    weatherSystem = new WeatherSystem();
    effectSystem = new WeatherEffectSystem();
  });

  describe('Weather Type Consistency', () => {
    // Python weather types: CLEAR, CLOUDY, OVERCAST, RAIN, HEAVY_RAIN, THUNDERSTORM, SNOW, BLIZZARD, FOG, HAIL
    // TypeScript weather types: clear, rain, storm, snow, fog, sandstorm, heatwave, blizzard
    
    it('should handle common weather types consistently', () => {
      const commonTypes: WeatherType[] = ['clear', 'rain', 'storm', 'snow', 'fog', 'blizzard'];
      
      commonTypes.forEach(type => {
        const params: WeatherParams = {
          region: 'test',
          biome: 'temperate',
          season: 'winter',
          altitude: 0
        };
        
        weatherSystem.initializeRegion('test', params);
        const weather = weatherSystem.getRegionWeather('test');
        
        expect(weather).not.toBeNull();
        if (weather) {
          expect(weather.current.effects).toBeInstanceOf(Array);
          
          // Verify effects are appropriate for the type
          const effects = weather.current.effects;
          
          switch (type) {
            case 'rain':
            case 'storm':
              expect(effects.some(e => e.type === 'movement')).toBeTruthy();
              expect(effects.some(e => e.type === 'visibility')).toBeTruthy();
              break;
              
            case 'snow':
            case 'blizzard':
              expect(effects.some(e => e.type === 'movement')).toBeTruthy();
              expect(effects.some(e => e.type === 'visibility')).toBeTruthy();
              // Snow should have stronger movement penalty than rain
              const snowMovement = effects.find(e => e.type === 'movement')?.value || 0;
              expect(Math.abs(snowMovement)).toBeGreaterThan(0.2); // Rain penalty is 0.2
              break;
              
            case 'fog':
              expect(effects.some(e => e.type === 'visibility')).toBeTruthy();
              const fogVisibility = effects.find(e => e.type === 'visibility')?.value || 0;
              expect(Math.abs(fogVisibility)).toBeGreaterThan(0.3); // Rain visibility penalty is 0.3
              break;
          }
        }
      });
    });
    
    it('should handle unique TypeScript weather types appropriately', () => {
      const uniqueTypes: WeatherType[] = ['sandstorm', 'heatwave'];
      
      uniqueTypes.forEach(type => {
        const params: WeatherParams = {
          region: 'test',
          biome: 'desert',
          season: 'summer',
          altitude: 0,
          forceWeather: {
            type,
            intensity: 'moderate'
          }
        };
        
        weatherSystem.initializeRegion('test', params);
        const weather = weatherSystem.getRegionWeather('test');
        
        expect(weather).not.toBeNull();
        if (weather) {
          const effects = weather.current.effects;
          
          switch (type) {
            case 'sandstorm':
              expect(effects.some(e => e.type === 'movement')).toBeTruthy();
              expect(effects.some(e => e.type === 'visibility')).toBeTruthy();
              expect(effects.some(e => e.type === 'combat')).toBeTruthy();
              break;
              
            case 'heatwave':
              expect(effects.some(e => e.type === 'status')).toBeTruthy();
              break;
          }
        }
      });
    });
  });

  describe('Weather Intensity Consistency', () => {
    it('should scale effects consistently across intensities', () => {
      const testType: WeatherType = 'rain';
      const intensities: WeatherIntensity[] = ['light', 'moderate', 'heavy', 'extreme'];
      const multipliers = {
        light: 0.5,
        moderate: 1.0,
        heavy: 1.5,
        extreme: 2.0
      };
      
      intensities.forEach(intensity => {
        const params: WeatherParams = {
          region: 'test',
          biome: 'temperate',
          season: 'spring',
          altitude: 0,
          forceWeather: {
            type: testType,
            intensity
          }
        };
        
        weatherSystem.initializeRegion('test', params);
        const weather = weatherSystem.getRegionWeather('test');
        
        expect(weather).not.toBeNull();
        if (weather) {
          const effects = weather.current.effects;
          const movementEffect = effects.find(e => e.type === 'movement');
          const visibilityEffect = effects.find(e => e.type === 'visibility');
          
          if (movementEffect) {
            // Base movement penalty for rain is -0.2
            expect(movementEffect.value).toBeCloseTo(-0.2 * multipliers[intensity], 1);
          }
          
          if (visibilityEffect) {
            // Base visibility penalty for rain is -0.3
            expect(visibilityEffect.value).toBeCloseTo(-0.3 * multipliers[intensity], 1);
          }
        }
      });
    });
  });

  describe('Effect Application Consistency', () => {
    it('should apply movement effects consistently', () => {
      const regionId = 'test-region';
      const baseMovementState: MovementState = {
        speed: 100,
        staminaCost: 10,
        jumpHeight: 50,
        climbSpeed: 30,
        swimSpeed: 40,
        terrainPenalty: 1.0
      };
      
      // Test with rain (movement penalty -0.2 at moderate intensity)
      const rainEffects: WeatherEffect[] = [{
        type: 'movement',
        value: -0.2,
        description: 'Rain movement penalty'
      }];
      
      effectSystem.setRegionEffects(regionId, {
        type: 'rain',
        intensity: 'moderate',
        duration: 1000,
        effects: rainEffects,
        visualEffects: {}
      });
      
      const modifiedMovement = effectSystem.modifyMovementStats(regionId, baseMovementState);
      
      // Verify all movement stats are reduced by 20%
      expect(modifiedMovement.speed).toBe(baseMovementState.speed * 0.8);
      expect(modifiedMovement.staminaCost).toBe(baseMovementState.staminaCost * 0.8);
      
      // Check optional properties if they exist in both states
      if (baseMovementState.jumpHeight && modifiedMovement.jumpHeight) {
        expect(modifiedMovement.jumpHeight).toBe(baseMovementState.jumpHeight * 0.8);
      }
      if (baseMovementState.climbSpeed && modifiedMovement.climbSpeed) {
        expect(modifiedMovement.climbSpeed).toBe(baseMovementState.climbSpeed * 0.8);
      }
      if (baseMovementState.swimSpeed && modifiedMovement.swimSpeed) {
        expect(modifiedMovement.swimSpeed).toBe(baseMovementState.swimSpeed * 0.8);
      }
      if (baseMovementState.terrainPenalty && modifiedMovement.terrainPenalty) {
        expect(modifiedMovement.terrainPenalty).toBe(baseMovementState.terrainPenalty * 0.8);
      }
    });
    
    it('should apply visibility effects consistently', () => {
      const regionId = 'test-region';
      const baseRange = 100;
      
      // Test with fog (visibility penalty -0.6 at moderate intensity)
      const fogEffects: WeatherEffect[] = [{
        type: 'visibility',
        value: -0.6,
        description: 'Fog visibility penalty'
      }];
      
      effectSystem.setRegionEffects(regionId, {
        type: 'fog',
        intensity: 'moderate',
        duration: 1000,
        effects: fogEffects,
        visualEffects: {}
      });
      
      const modifiedRange = effectSystem.calculateVisibilityRange(regionId, baseRange);
      
      // Verify visibility is reduced by 60%
      expect(modifiedRange).toBe(baseRange * 0.4);
    });
  });

  describe('Visual Consistency', () => {
    let gameState: GameStateManager;
    let sceneManager: SceneManager;

    beforeEach(() => {
      gameState = new GameStateManager();
      sceneManager = new SceneManager();
    });

    it('should maintain visual consistency across different game views', () => {
      const regionId = 'test-region';
      const testWeather = {
        type: 'rain' as WeatherType,
        intensity: 'heavy' as WeatherIntensity,
        duration: 1000,
        effects: [
          { type: 'visibility', value: -0.3 },
          { type: 'movement', value: -0.2 }
        ]
      };

      weatherSystem.setRegionWeather(regionId, testWeather);
      const initialEffects = weatherSystem.getRegionEffects(regionId);

      // Test different game views
      const views: GameView[] = ['gameplay', 'menu', 'cutscene', 'dialogue'];
      views.forEach(view => {
        gameState.setCurrentView(view);
        weatherSystem.onViewChanged(view);
        const currentEffects = weatherSystem.getRegionEffects(regionId);

        expect(currentEffects).toEqual(initialEffects);
      });
    });

    it('should handle weather transitions smoothly', () => {
      const regionId = 'test-region';
      const startWeather: WeatherType = 'clear';
      const endWeather: WeatherType = 'rain';
      const transitionDuration = 5000; // 5 seconds

      // Start with clear weather
      weatherSystem.setRegionWeather(regionId, {
        type: startWeather,
        intensity: 'moderate',
        duration: 1000,
        effects: []
      });

      // Begin transition
      weatherSystem.transitionWeather(regionId, endWeather, transitionDuration);

      // Check midpoint (2.5 seconds)
      jest.advanceTimersByTime(transitionDuration / 2);
      const midEffects = weatherSystem.getRegionEffects(regionId);

      // Visibility should be halfway between clear (1.0) and rain (0.7)
      expect(midEffects.find(e => e.type === 'visibility')?.value)
        .toBeCloseTo(0.85, 2);

      // Complete transition
      jest.advanceTimersByTime(transitionDuration / 2);
      const finalEffects = weatherSystem.getRegionEffects(regionId);

      // Should match rain effects
      expect(finalEffects.find(e => e.type === 'visibility')?.value)
        .toBeCloseTo(0.7, 2);
    });
  });

  describe('State Persistence', () => {
    it('should persist weather state through scene transitions', () => {
      const regionId = 'test-region';
      const weatherState = {
        type: 'storm' as WeatherType,
        intensity: 'extreme' as WeatherIntensity,
        duration: 1000,
        effects: [
          { type: 'visibility', value: -0.5 },
          { type: 'movement', value: -0.3 }
        ]
      };

      weatherSystem.setRegionWeather(regionId, weatherState);
      const initialState = weatherSystem.serializeState();

      // Test scene change
      weatherSystem.onSceneChange('new_scene');
      const afterSceneState = weatherSystem.serializeState();
      expect(afterSceneState).toEqual(initialState);

      // Test save/load
      const savedState = weatherSystem.serializeState();
      weatherSystem.setRegionWeather(regionId, {
        type: 'clear',
        intensity: 'light',
        duration: 1000,
        effects: []
      });
      weatherSystem.deserializeState(savedState);
      const loadedState = weatherSystem.serializeState();
      expect(loadedState).toEqual(savedState);

      // Test fast travel
      weatherSystem.onFastTravelBegin();
      const duringTravelState = weatherSystem.serializeState();
      expect(duringTravelState).toEqual(initialState);
      weatherSystem.onFastTravelEnd();
      const afterTravelState = weatherSystem.serializeState();
      expect(afterTravelState).toEqual(initialState);
    });

    it('should maintain particle effect consistency during transitions', () => {
      const regionId = 'test-region';
      const weatherState = {
        type: 'snow' as WeatherType,
        intensity: 'heavy' as WeatherIntensity,
        duration: 1000,
        effects: [
          { type: 'visibility', value: -0.4 },
          { type: 'movement', value: -0.25 }
        ]
      };

      weatherSystem.setRegionWeather(regionId, weatherState);
      const initialParticles = weatherSystem.getParticleCount(10);

      // Test view transitions
      weatherSystem.onViewChanged('cutscene');
      const duringCutsceneParticles = weatherSystem.getParticleCount(10);
      expect(duringCutsceneParticles).toBe(initialParticles);

      weatherSystem.onViewChanged('gameplay');
      const afterCutsceneParticles = weatherSystem.getParticleCount(10);
      expect(afterCutsceneParticles).toBe(initialParticles);
    });
  });
}); 