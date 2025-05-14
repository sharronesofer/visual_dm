import { WeatherSystem } from '../../systems/WeatherSystem';
import { WeatherEffectSystem } from '../../systems/WeatherEffectSystem';
import { NetworkManager } from '../../systems/NetworkManager';
import { PerformanceProfiler } from '../../utils/PerformanceProfiler';
import { WeatherType, WeatherIntensity, WeatherState, WeatherParams } from '../../types/weather';
import { performance } from 'perf_hooks';

describe('Weather Synchronization and Performance', () => {
  let weatherSystem: WeatherSystem;
  let effectSystem: WeatherEffectSystem;
  let networkManager: NetworkManager;
  let profiler: PerformanceProfiler;

  beforeEach(() => {
    weatherSystem = new WeatherSystem();
    effectSystem = new WeatherEffectSystem();
    networkManager = new NetworkManager();
    profiler = new PerformanceProfiler();
  });

  afterEach(() => {
    weatherSystem.stop();
    networkManager.disconnect();
  });

  describe('State Synchronization', () => {
    it('should efficiently serialize weather state', () => {
      // Set up initial weather state
      const initialState: WeatherState = {
        type: WeatherType.RAIN,
        intensity: WeatherIntensity.HEAVY,
        duration: 300,
        effects: ['reduced_visibility', 'wet_ground']
      };

      weatherSystem.setState(initialState);

      // Measure serialization performance
      const startTime = performance.now();
      const stateData = weatherSystem.serializeState();
      const serializationTime = performance.now() - startTime;

      // Check performance
      expect(serializationTime).toBeLessThan(1); // 1ms threshold
      expect(JSON.stringify(stateData).length).toBeLessThan(1024); // 1KB threshold
    });

    it('should generate and apply delta updates correctly', () => {
      // Initial state
      const initialState: WeatherState = {
        type: WeatherType.CLEAR,
        intensity: WeatherIntensity.LIGHT,
        duration: 300,
        effects: []
      };

      // Updated state
      const updatedState: WeatherState = {
        type: WeatherType.RAIN,
        intensity: WeatherIntensity.HEAVY,
        duration: 300,
        effects: ['reduced_visibility', 'wet_ground']
      };

      weatherSystem.setState(initialState);
      const baseState = weatherSystem.serializeState();

      weatherSystem.setState(updatedState);
      const delta = weatherSystem.generateStateDelta(baseState);

      // Verify delta is smaller than full state
      const fullState = weatherSystem.serializeState();
      expect(JSON.stringify(delta).length).toBeLessThan(
        JSON.stringify(fullState).length
      );

      // Test applying delta
      const testSystem = new WeatherSystem();
      testSystem.setState(initialState);
      testSystem.applyStateDelta(delta);

      expect(testSystem.getState()).toEqual(updatedState);
    });

    it('should synchronize weather state across network', () => {
      const mockBroadcast = jest.spyOn(networkManager, 'broadcastWeatherUpdate');
      const mockClients = [
        { id: 'client1', send: jest.fn() },
        { id: 'client2', send: jest.fn() }
      ];

      networkManager.setConnectedClients(mockClients);

      // Trigger weather change
      weatherSystem.setWeather(WeatherType.SNOW, WeatherIntensity.HEAVY);
      weatherSystem.syncWeatherState();

      // Verify broadcast
      expect(mockBroadcast).toHaveBeenCalledTimes(1);
      const broadcastData = mockBroadcast.mock.calls[0][0];
      expect(broadcastData).toHaveProperty('weatherType');
      expect(broadcastData).toHaveProperty('intensity');
      expect(JSON.stringify(broadcastData).length).toBeLessThan(1024);
    });
  });

  describe('Performance Optimization', () => {
    it('should scale particle effects based on distance', () => {
      // Test particle counts at different distances
      const closeParticles = weatherSystem.getParticleCount(10);
      const mediumParticles = weatherSystem.getParticleCount(50);
      const farParticles = weatherSystem.getParticleCount(100);

      // Verify LOD scaling
      expect(closeParticles).toBeGreaterThan(mediumParticles);
      expect(mediumParticles).toBeGreaterThan(farParticles);
    });

    it('should maintain acceptable memory usage', () => {
      const initialMemory = profiler.getMemoryUsage();

      // Create multiple weather systems
      const systems: WeatherSystem[] = [];
      for (let i = 0; i < 10; i++) {
        const sys = new WeatherSystem();
        sys.setWeather(WeatherType.RAIN, WeatherIntensity.HEAVY);
        systems.push(sys);
      }

      const finalMemory = profiler.getMemoryUsage();
      const memoryDelta = finalMemory - initialMemory;

      // Check memory impact
      expect(memoryDelta).toBeLessThan(50 * 1024 * 1024); // 50MB threshold
    });

    it('should complete weather updates within frame budget', async () => {
      const updateTimes: number[] = [];

      // Measure multiple update cycles
      for (let i = 0; i < 100; i++) {
        const startTime = performance.now();
        weatherSystem.update(16.67); // Simulate 60 FPS frame time
        const updateTime = performance.now() - startTime;
        updateTimes.push(updateTime);
      }

      const avgUpdateTime = updateTimes.reduce((a, b) => a + b) / updateTimes.length;
      const maxUpdateTime = Math.max(...updateTimes);

      // Verify performance
      expect(avgUpdateTime).toBeLessThan(16.67); // 60 FPS threshold
      expect(maxUpdateTime).toBeLessThan(33.33); // 30 FPS threshold
    });

    it('should handle rapid weather transitions efficiently', async () => {
      const transitionCount = 50;
      const transitions: number[] = [];

      // Perform rapid weather changes
      for (let i = 0; i < transitionCount; i++) {
        const startTime = performance.now();
        
        weatherSystem.setWeather(
          i % 2 === 0 ? WeatherType.RAIN : WeatherType.CLEAR,
          WeatherIntensity.MODERATE
        );
        
        const transitionTime = performance.now() - startTime;
        transitions.push(transitionTime);

        // Small delay to simulate game loop
        await new Promise(resolve => setTimeout(resolve, 16));
      }

      const avgTransitionTime = transitions.reduce((a, b) => a + b) / transitions.length;
      expect(avgTransitionTime).toBeLessThan(5); // 5ms threshold for transitions
    });
  });
}); 