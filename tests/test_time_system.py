import unittest
from datetime import datetime, timedelta
from app.core.models.time_system import TimeSystem, TimeEvent, TimeScale
from app.core.enums import TimeOfDay

class TestTimeSystem(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        
    def test_time_scale_progression(self):
        """Test that time progresses correctly at different scales."""
        # Test REALTIME
        self.time_system.set_time_scale(TimeScale.REALTIME)
        initial_time = self.time_system.current_time
        self.time_system.update(60)  # 60 real seconds
        self.assertEqual(
            (self.time_system.current_time - initial_time).total_seconds(),
            60
        )
        
        # Test ACCELERATED
        self.time_system.set_time_scale(TimeScale.ACCELERATED)
        initial_time = self.time_system.current_time
        self.time_system.update(60)  # 60 real seconds = 60 game minutes
        self.assertEqual(
            (self.time_system.current_time - initial_time).total_seconds(),
            3600  # 60 minutes
        )
        
        # Test FAST
        self.time_system.set_time_scale(TimeScale.FAST)
        initial_time = self.time_system.current_time
        self.time_system.update(60)  # 60 real seconds = 60 game hours
        self.assertEqual(
            (self.time_system.current_time - initial_time).total_seconds(),
            216000  # 60 hours
        )
        
    def test_pause_resume(self):
        """Test pausing and resuming time progression."""
        initial_time = self.time_system.current_time
        
        # Test pause
        self.time_system.pause()
        self.time_system.update(60)
        self.assertEqual(self.time_system.current_time, initial_time)
        
        # Test resume
        self.time_system.resume()
        self.time_system.update(60)
        self.assertNotEqual(self.time_system.current_time, initial_time)
        
    def test_time_events(self):
        """Test time event triggering."""
        # Add a test event
        event = TimeEvent(
            id="test1",
            type="test_event",
            trigger_time=self.time_system.current_time + timedelta(hours=1),
            data={"test": "data"}
        )
        self.time_system.add_event(event)
        
        # Advance time but not enough to trigger
        self.time_system.set_time_scale(TimeScale.FAST)
        self.time_system.update(30)  # 30 real seconds = 30 game hours
        triggered = self.time_system._process_events()
        self.assertEqual(len(triggered), 0)
        
        # Advance time enough to trigger
        self.time_system.update(60)  # Another 60 game hours
        triggered = self.time_system._process_events()
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].id, "test1")
        
    def test_recurring_events(self):
        """Test recurring time events."""
        # Add a recurring event
        event = TimeEvent(
            id="recurring1",
            type="test_event",
            trigger_time=self.time_system.current_time + timedelta(hours=1),
            data={"test": "data"},
            recurring=True,
            recurrence_interval=timedelta(hours=2)
        )
        self.time_system.add_event(event)
        
        # Advance time to trigger multiple recurrences
        self.time_system.set_time_scale(TimeScale.FAST)
        self.time_system.update(120)  # 120 game hours
        
        # Event should still exist and have an updated trigger time
        self.assertEqual(len(self.time_system.events), 1)
        recurring_event = self.time_system.events[0]
        self.assertTrue(
            recurring_event.trigger_time > self.time_system.current_time
        )
        
    def test_time_of_day(self):
        """Test time of day calculations."""
        # Test each time of day period
        test_times = [
            (5, TimeOfDay.DAWN),
            (10, TimeOfDay.MORNING),
            (13, TimeOfDay.NOON),
            (15, TimeOfDay.AFTERNOON),
            (18, TimeOfDay.DUSK),
            (22, TimeOfDay.NIGHT),
            (2, TimeOfDay.NIGHT)
        ]
        
        for hour, expected_time in test_times:
            self.time_system.current_time = self.time_system.current_time.replace(
                hour=hour
            )
            self.assertEqual(
                self.time_system.get_time_of_day(),
                expected_time,
                f"Failed for hour {hour}"
            )
            
    def test_advance_time(self):
        """Test manually advancing time."""
        initial_time = self.time_system.current_time
        
        # Add a test event
        event = TimeEvent(
            id="test2",
            type="test_event",
            trigger_time=initial_time + timedelta(days=1, hours=2),
            data={"test": "data"}
        )
        self.time_system.add_event(event)
        
        # Advance time and check event triggering
        triggered = self.time_system.advance_time(days=1, hours=3)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].id, "test2")
        
        # Verify time advancement
        expected_delta = timedelta(days=1, hours=3)
        actual_delta = self.time_system.current_time - initial_time
        self.assertEqual(actual_delta, expected_delta)
        
    def test_time_formatting(self):
        """Test time formatting."""
        test_time = datetime(2024, 3, 15, 14, 30, 45)
        self.time_system.current_time = test_time
        
        # Test without seconds
        expected_format = "2024-03-15 14:30"
        self.assertEqual(
            self.time_system.format_time(include_seconds=False),
            expected_format
        )
        
        # Test with seconds
        expected_format_with_seconds = "2024-03-15 14:30:45"
        self.assertEqual(
            self.time_system.format_time(include_seconds=True),
            expected_format_with_seconds
        )

if __name__ == '__main__':
    unittest.main() 