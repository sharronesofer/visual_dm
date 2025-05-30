from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
import sys


# Import EventBase and EventDispatcher with fallbacks
try:
    from backend.systems.events import EventBase, EventDispatcher
except ImportError:
    # Fallback for tests or when events system isn't available
    class EventBase:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
    
    class EventDispatcher:
        @classmethod
        def get_instance(cls):
            return cls()
        
        def dispatch(self, event):
            pass
        
        def publish(self, event):
            pass
        
        def emit(self, event):
            pass

# Add the backend.systems.combat module to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.systems.combat.clean_events import clean_events


class TestCleanEvents(unittest.TestCase):
    """Test cases for the clean_events utility script"""

    def setUp(self):
        """Set up test fixtures"""
        self.sample_content = '''from backend.app.core.events.event_dispatcher import EventDispatcher
from backend.app.core.events.event_types import CombatEvent

def some_function():
    EventDispatcher.dispatch(CombatEvent.ATTACK, {"damage": 10})
    EventDispatcher.dispatch(
        CombatEvent.HEAL,
        {
            "amount": 5,
            "target": "player"
        }
    )
    # Dispatch some event
    return True
'''

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_basic_functionality(self, mock_exists, mock_file):
        """Test basic clean_events functionality"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_content
        
        clean_events()
        
        # Verify file operations
        mock_file.assert_any_call("unified_combat_utils.py.backup", "r")
        mock_file.assert_any_call("unified_combat_utils.py", "w")

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_removes_imports(self, mock_exists, mock_file):
        """Test that EventDispatcher imports are removed"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_content
        
        clean_events()
        
        # Get the written content
        written_content = mock_file.return_value.write.call_args[0][0]
        
        # Verify imports are removed
        self.assertNotIn("from backend.app.core.events.event_dispatcher import EventDispatcher", written_content)
        self.assertNotIn("from backend.app.core.events.event_types import CombatEvent", written_content)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_removes_dispatcher_calls(self, mock_exists, mock_file):
        """Test that EventDispatcher calls are removed"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_content
        
        clean_events()
        
        # Get the written content
        written_content = mock_file.return_value.write.call_args[0][0]
        
        # Verify EventDispatcher calls are removed
        self.assertNotIn("EventDispatcher.dispatch", written_content)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_replaces_dispatch_comments(self, mock_exists, mock_file):
        """Test that dispatch comments are replaced"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_content
        
        clean_events()
        
        # Get the written content
        written_content = mock_file.return_value.write.call_args[0][0]
        
        # Verify comment replacement
        self.assertIn("# Event dispatch disabled for now", written_content)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_with_complex_content(self, mock_exists, mock_file):
        """Test clean_events with complex EventDispatcher patterns"""
        complex_content = '''
EventDispatcher.dispatch(CombatEvent.ATTACK, {
    "damage": 10,
    "type": "physical"
})

EventDispatcher.dispatch(CombatEvent.HEAL)

CombatEvent.DAMAGE_DEALT

{
    "complex": "object",
    "with": "values"
}

)
}
'''
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = complex_content
        
        clean_events()
        
        # Get the written content
        written_content = mock_file.return_value.write.call_args[0][0]
        
        # Verify complex patterns are cleaned
        self.assertNotIn("EventDispatcher.dispatch", written_content)
        self.assertNotIn("CombatEvent.", written_content)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_preserves_other_code(self, mock_exists, mock_file):
        """Test that non-EventDispatcher code is preserved"""
        content_with_other_code = '''
def normal_function():
    return "preserved"

class NormalClass:
    def method(self):
        pass

EventDispatcher.dispatch(CombatEvent.ATTACK, {"damage": 10})

variable = "also preserved"
'''
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = content_with_other_code
        
        clean_events()
        
        # Get the written content
        written_content = mock_file.return_value.write.call_args[0][0]
        
        # Verify normal code is preserved
        self.assertIn("def normal_function():", written_content)
        self.assertIn("class NormalClass:", written_content)
        self.assertIn('variable = "also preserved"', written_content)
        
        # Verify EventDispatcher code is removed
        self.assertNotIn("EventDispatcher.dispatch", written_content)

    @patch('builtins.print')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_prints_completion_message(self, mock_exists, mock_file, mock_print):
        """Test that completion message is printed"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = self.sample_content
        
        clean_events()
        
        mock_print.assert_called_with("Completely cleaned all EventDispatcher references")

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_clean_events_empty_file(self, mock_exists, mock_file):
        """Test clean_events with empty file"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = ""
        
        clean_events()
        
        # Should not raise any errors
        mock_file.assert_any_call("unified_combat_utils.py.backup", "r")
        mock_file.assert_any_call("unified_combat_utils.py", "w")

    @patch('backend.systems.combat.clean_events.clean_events')
    def test_main_execution(self, mock_clean_events):
        """Test main execution path"""
        # Import and execute the main block
        from backend.systems.combat import clean_events
        
        # Simulate running as main
        with patch('__main__.__name__', '__main__'):
            exec(compile(open(backend.systems.combat.clean_events.__file__).read(), 
                        backend.systems.combat.clean_events.__file__, 'exec'))


def test_module_imports():
    """Test that the module can be imported without errors"""
    from backend.systems.combat import clean_events
    assert hasattr(backend.systems.combat.clean_events, 'clean_events')


if __name__ == '__main__':
    unittest.main() 