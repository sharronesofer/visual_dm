import unittest
import time
from unittest.mock import MagicMock, patch
from app.core.models.weather_system import WeatherSystem
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.models.network_manager import NetworkManager
from app.core.enums import WeatherType, WeatherIntensity
from app.utils.profiling import PerformanceProfiler

class TestWeatherSyncPerformance(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        self.weather_system = WeatherSystem(self.time_system, self.season_system)
        self.network_manager = NetworkManager()
        self.profiler = PerformanceProfiler()
        
    def test_weather_state_serialization(self):
        """Test that weather state can be efficiently serialized for network transmission."""
        # Set up initial weather state
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        
        # Serialize state
        start_time = time.perf_counter()
        state_data = self.weather_system.serialize_state()
        serialization_time = time.perf_counter() - start_time
        
        # Check serialization performance
        self.assertLess(serialization_time, 0.001,  # 1ms threshold
                       "Weather state serialization took too long")
        
        # Verify data size is within acceptable limits
        state_size = len(str(state_data).encode('utf-8'))
        self.assertLess(state_size, 1024,  # 1KB threshold
                       "Serialized weather state is too large")
        
    def test_delta_updates(self):
        """Test that delta updates are properly generated and applied."""
        # Set up initial state
        self.weather_system.current_weather = WeatherType.CLEAR
        initial_state = self.weather_system.serialize_state()
        
        # Make some changes
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        
        # Generate delta
        delta = self.weather_system.generate_state_delta(initial_state)
        
        # Verify delta is smaller than full state
        full_state = self.weather_system.serialize_state()
        self.assertLess(len(str(delta).encode('utf-8')),
                       len(str(full_state).encode('utf-8')),
                       "Delta update is not smaller than full state")
        
        # Test applying delta
        test_system = WeatherSystem(self.time_system, self.season_system)
        test_system.apply_state_delta(delta)
        
        # Verify state matches
        self.assertEqual(test_system.current_weather, self.weather_system.current_weather)
        self.assertEqual(test_system.weather_intensity, self.weather_system.weather_intensity)
        
    @patch('app.core.models.network_manager.NetworkManager.broadcast_weather_update')
    def test_network_synchronization(self, mock_broadcast):
        """Test that weather updates are properly synchronized across network."""
        # Set up mock clients
        client1 = MagicMock()
        client2 = MagicMock()
        self.network_manager.connected_clients = [client1, client2]
        
        # Trigger weather change
        self.weather_system.current_weather = WeatherType.SNOW
        self.weather_system.sync_weather_state()
        
        # Verify broadcast was called with correct data
        mock_broadcast.assert_called_once()
        broadcast_data = mock_broadcast.call_args[0][0]
        
        # Check data format and size
        self.assertIn('weather_type', broadcast_data)
        self.assertIn('intensity', broadcast_data)
        self.assertLess(len(str(broadcast_data).encode('utf-8')), 1024)
        
    def test_particle_system_performance(self):
        """Test that particle system performance scales appropriately with distance."""
        # Test close-range particles
        close_particles = self.weather_system.get_particle_count(distance=10)
        
        # Test medium-range particles
        medium_particles = self.weather_system.get_particle_count(distance=50)
        
        # Test far-range particles
        far_particles = self.weather_system.get_particle_count(distance=100)
        
        # Verify particle count decreases with distance
        self.assertGreater(close_particles, medium_particles)
        self.assertGreater(medium_particles, far_particles)
        
    def test_memory_usage(self):
        """Test that weather system memory usage stays within acceptable limits."""
        with self.profiler.measure_memory():
            # Create multiple weather systems
            weather_systems = []
            for _ in range(10):
                ws = WeatherSystem(self.time_system, self.season_system)
                ws.current_weather = WeatherType.RAIN
                ws.weather_intensity = WeatherIntensity.HEAVY
                weather_systems.append(ws)
                
            # Force garbage collection to get accurate memory usage
            import gc
            gc.collect()
            
            # Check memory usage
            memory_usage = self.profiler.get_memory_usage()
            self.assertLess(memory_usage, 50 * 1024 * 1024,  # 50MB threshold
                          "Weather system memory usage exceeds limit")
            
    def test_weather_update_performance(self):
        """Test that weather updates complete within performance budget."""
        update_times = []
        
        # Measure multiple update cycles
        for _ in range(100):
            start_time = time.perf_counter()
            self.weather_system.update(1.0)  # 1 second update
            update_time = time.perf_counter() - start_time
            update_times.append(update_time)
        
        # Calculate average and maximum update times
        avg_update_time = sum(update_times) / len(update_times)
        max_update_time = max(update_times)
        
        # Verify performance
        self.assertLess(avg_update_time, 0.016,  # 16ms (60 FPS) threshold
                       "Average weather update time exceeds performance budget")
        self.assertLess(max_update_time, 0.033,  # 33ms (30 FPS) threshold
                       "Maximum weather update time exceeds performance budget") 