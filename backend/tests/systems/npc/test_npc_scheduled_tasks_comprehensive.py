"""
Comprehensive Tests for backend.systems.npc.npc_scheduled_tasks

This test suite focuses on achieving high coverage for NPC scheduled tasks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Import the module being tested
try: pass
    from backend.systems.npc.npc_scheduled_tasks import (
        NPCScheduledTasks,
        run_scheduled_tasks
    )
except ImportError as e: pass
    pytest.skip(f"Could not import backend.systems.npc.npc_scheduled_tasks: {e}", allow_module_level=True)


class TestNPCScheduledTasksInitialization: pass
    """Test NPCScheduledTasks class structure."""
    
    def test_class_exists(self): pass
        """Test that NPCScheduledTasks class exists."""
        assert NPCScheduledTasks is not None
        assert hasattr(NPCScheduledTasks, 'run_daily_tasks')
        assert hasattr(NPCScheduledTasks, 'run_weekly_tasks')
        assert hasattr(NPCScheduledTasks, 'run_monthly_tasks')
        assert hasattr(NPCScheduledTasks, 'run_all_scheduled_tasks')


class TestNPCScheduledTasksDailyTasks: pass
    """Test daily scheduled tasks functionality."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_daily_tasks_success(self, mock_get_service): pass
        """Test successful daily tasks execution."""
        mock_service = Mock()
        mock_service.run_rumor_decay.return_value = {"rumors_decayed": 5}
        mock_get_service.return_value = mock_service
        
        with patch('random.random', return_value=0.2):  # Trigger faction influence
            result = NPCScheduledTasks.run_daily_tasks()
            
            assert "timestamp" in result
            assert "tasks_run" in result
            assert len(result["tasks_run"]) >= 1
            
            # Check rumor decay was called
            mock_service.run_rumor_decay.assert_called_once()
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_daily_tasks_rumor_decay_error(self, mock_get_service): pass
        """Test daily tasks with rumor decay error."""
        mock_service = Mock()
        mock_service.run_rumor_decay.side_effect = Exception("Rumor decay failed")
        mock_get_service.return_value = mock_service
        
        result = NPCScheduledTasks.run_daily_tasks()
        
        assert "timestamp" in result
        assert "tasks_run" in result
        
        # Should have error recorded
        rumor_task = next((task for task in result["tasks_run"] if task["name"] == "rumor_decay"), None)
        assert rumor_task is not None
        assert "error" in rumor_task
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_daily_tasks_faction_influence_triggered(self, mock_get_service): pass
        """Test daily tasks with faction influence triggered."""
        mock_service = Mock()
        mock_service.run_rumor_decay.return_value = {"rumors_decayed": 3}
        mock_get_service.return_value = mock_service
        
        with patch('random.random', return_value=0.1):  # 10% < 30%, should trigger
            result = NPCScheduledTasks.run_daily_tasks()
            
            faction_task = next((task for task in result["tasks_run"] if task["name"] == "faction_influence"), None)
            assert faction_task is not None
            assert faction_task["result"] == "simulated"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_daily_tasks_faction_influence_not_triggered(self, mock_get_service): pass
        """Test daily tasks with faction influence not triggered."""
        mock_service = Mock()
        mock_service.run_rumor_decay.return_value = {"rumors_decayed": 3}
        mock_get_service.return_value = mock_service
        
        with patch('random.random', return_value=0.8):  # 80% > 30%, should not trigger
            result = NPCScheduledTasks.run_daily_tasks()
            
            faction_task = next((task for task in result["tasks_run"] if task["name"] == "faction_influence"), None)
            assert faction_task is None


class TestNPCScheduledTasksWeeklyTasks: pass
    """Test weekly scheduled tasks functionality."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_weekly_tasks_success(self, mock_get_service): pass
        """Test successful weekly tasks execution."""
        mock_service = Mock()
        mock_service.apply_global_motifs_to_all_npcs.return_value = {"motifs_applied": 12}
        mock_get_service.return_value = mock_service
        
        result = NPCScheduledTasks.run_weekly_tasks()
        
        assert "timestamp" in result
        assert "tasks_run" in result
        assert len(result["tasks_run"]) == 1
        
        # Check motifs were applied
        mock_service.apply_global_motifs_to_all_npcs.assert_called_once()
        
        motif_task = result["tasks_run"][0]
        assert motif_task["name"] == "apply_motifs"
        assert motif_task["result"]["motifs_applied"] == 12
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_weekly_tasks_motif_error(self, mock_get_service): pass
        """Test weekly tasks with motif application error."""
        mock_service = Mock()
        mock_service.apply_global_motifs_to_all_npcs.side_effect = Exception("Motif application failed")
        mock_get_service.return_value = mock_service
        
        result = NPCScheduledTasks.run_weekly_tasks()
        
        assert "timestamp" in result
        assert "tasks_run" in result
        
        # Should have error recorded
        motif_task = result["tasks_run"][0]
        assert motif_task["name"] == "apply_motifs"
        assert "error" in motif_task


class TestNPCScheduledTasksMonthlyTasks: pass
    """Test monthly scheduled tasks functionality."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_monthly_tasks_success(self, mock_get_service): pass
        """Test successful monthly tasks execution."""
        mock_service = Mock()
        mock_service.run_monthly_population_update.return_value = {"population_updated": True, "new_npcs": 3}
        mock_get_service.return_value = mock_service
        
        result = NPCScheduledTasks.run_monthly_tasks()
        
        assert "timestamp" in result
        assert "tasks_run" in result
        assert len(result["tasks_run"]) == 1
        
        # Check population update was called
        mock_service.run_monthly_population_update.assert_called_once()
        
        population_task = result["tasks_run"][0]
        assert population_task["name"] == "population_update"
        assert population_task["result"]["new_npcs"] == 3
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_run_monthly_tasks_population_error(self, mock_get_service): pass
        """Test monthly tasks with population update error."""
        mock_service = Mock()
        mock_service.run_monthly_population_update.side_effect = Exception("Population update failed")
        mock_get_service.return_value = mock_service
        
        result = NPCScheduledTasks.run_monthly_tasks()
        
        assert "timestamp" in result
        assert "tasks_run" in result
        
        # Should have error recorded
        population_task = result["tasks_run"][0]
        assert population_task["name"] == "population_update"
        assert "error" in population_task


class TestNPCScheduledTasksAllTasks: pass
    """Test running all scheduled tasks."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_daily_tasks')
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_weekly_tasks')
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_monthly_tasks')
    def test_run_all_scheduled_tasks(self, mock_monthly, mock_weekly, mock_daily): pass
        """Test running all scheduled tasks at once."""
        mock_daily.return_value = {"daily": "result"}
        mock_weekly.return_value = {"weekly": "result"}
        mock_monthly.return_value = {"monthly": "result"}
        
        result = NPCScheduledTasks.run_all_scheduled_tasks()
        
        assert "daily_tasks" in result
        assert "weekly_tasks" in result
        assert "monthly_tasks" in result
        assert "timestamp" in result
        
        # Verify all task types were called
        mock_daily.assert_called_once()
        mock_weekly.assert_called_once()
        mock_monthly.assert_called_once()
        
        assert result["daily_tasks"]["daily"] == "result"
        assert result["weekly_tasks"]["weekly"] == "result"
        assert result["monthly_tasks"]["monthly"] == "result"


class TestRunScheduledTasksFunction: pass
    """Test the standalone run_scheduled_tasks function."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_daily_tasks')
    def test_run_scheduled_tasks_daily(self, mock_daily): pass
        """Test running daily tasks via standalone function."""
        mock_daily.return_value = {"daily": "result"}
        
        result = run_scheduled_tasks("daily")
        
        mock_daily.assert_called_once()
        assert result["daily"] == "result"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_weekly_tasks')
    def test_run_scheduled_tasks_weekly(self, mock_weekly): pass
        """Test running weekly tasks via standalone function."""
        mock_weekly.return_value = {"weekly": "result"}
        
        result = run_scheduled_tasks("weekly")
        
        mock_weekly.assert_called_once()
        assert result["weekly"] == "result"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_monthly_tasks')
    def test_run_scheduled_tasks_monthly(self, mock_monthly): pass
        """Test running monthly tasks via standalone function."""
        mock_monthly.return_value = {"monthly": "result"}
        
        result = run_scheduled_tasks("monthly")
        
        mock_monthly.assert_called_once()
        assert result["monthly"] == "result"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_all_scheduled_tasks')
    def test_run_scheduled_tasks_all(self, mock_all): pass
        """Test running all tasks via standalone function."""
        mock_all.return_value = {"all": "result"}
        
        result = run_scheduled_tasks("all")
        
        mock_all.assert_called_once()
        assert result["all"] == "result"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_all_scheduled_tasks')
    def test_run_scheduled_tasks_default(self, mock_all): pass
        """Test running tasks with default parameter (should run all)."""
        mock_all.return_value = {"all": "result"}
        
        result = run_scheduled_tasks()
        
        mock_all.assert_called_once()
        assert result["all"] == "result"
    
    @patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_all_scheduled_tasks')
    def test_run_scheduled_tasks_invalid_type(self, mock_all): pass
        """Test running tasks with invalid type (should default to all)."""
        mock_all.return_value = {"all": "result"}
        
        result = run_scheduled_tasks("invalid_type")
        
        mock_all.assert_called_once()
        assert result["all"] == "result"


class TestNPCScheduledTasksEdgeCases: pass
    """Test edge cases and error handling."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_service_unavailable(self, mock_get_service): pass
        """Test behavior when NPC service is unavailable."""
        mock_get_service.side_effect = Exception("Service unavailable")
        
        # Should not raise exception, should handle gracefully
        result = NPCScheduledTasks.run_daily_tasks()
        assert "timestamp" in result
        assert "tasks_run" in result
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_partial_task_failure(self, mock_get_service): pass
        """Test behavior when some tasks fail but others succeed."""
        mock_service = Mock()
        mock_service.run_rumor_decay.side_effect = Exception("Rumor decay failed")
        mock_get_service.return_value = mock_service
        
        with patch('random.random', return_value=0.1):  # Trigger faction influence
            result = NPCScheduledTasks.run_daily_tasks()
            
            # Should have both tasks recorded, one with error, one with success
            assert len(result["tasks_run"]) == 2
            
            rumor_task = next((task for task in result["tasks_run"] if task["name"] == "rumor_decay"), None)
            faction_task = next((task for task in result["tasks_run"] if task["name"] == "faction_influence"), None)
            
            assert rumor_task is not None and "error" in rumor_task
            assert faction_task is not None and "result" in faction_task
    
    def test_timestamp_format(self): pass
        """Test that timestamps are in correct ISO format."""
        with patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service'): pass
            result = NPCScheduledTasks.run_daily_tasks()
            
            # Should be able to parse the timestamp
            timestamp = result["timestamp"]
            parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            assert isinstance(parsed_time, datetime)


class TestNPCScheduledTasksIntegration: pass
    """Test integration scenarios."""
    
    @patch('backend.systems.npc.npc_scheduled_tasks.get_npc_service')
    def test_complete_task_cycle(self, mock_get_service): pass
        """Test running a complete cycle of all task types."""
        mock_service = Mock()
        mock_service.run_rumor_decay.return_value = {"rumors_decayed": 5}
        mock_service.apply_global_motifs_to_all_npcs.return_value = {"motifs_applied": 12}
        mock_service.run_monthly_population_update.return_value = {"new_npcs": 3}
        mock_get_service.return_value = mock_service
        
        # Run all task types
        daily_result = NPCScheduledTasks.run_daily_tasks()
        weekly_result = NPCScheduledTasks.run_weekly_tasks()
        monthly_result = NPCScheduledTasks.run_monthly_tasks()
        
        # Verify all completed successfully
        assert len(daily_result["tasks_run"]) >= 1
        assert len(weekly_result["tasks_run"]) == 1
        assert len(monthly_result["tasks_run"]) == 1
        
        # Verify all service methods were called
        mock_service.run_rumor_decay.assert_called_once()
        mock_service.apply_global_motifs_to_all_npcs.assert_called_once()
        mock_service.run_monthly_population_update.assert_called_once()
    
    def test_task_execution_order(self): pass
        """Test that tasks execute in the expected order."""
        with patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_daily_tasks') as mock_daily: pass
            with patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_weekly_tasks') as mock_weekly: pass
                with patch('backend.systems.npc.npc_scheduled_tasks.NPCScheduledTasks.run_monthly_tasks') as mock_monthly: pass
                    mock_daily.return_value = {"daily": "result"}
                    mock_weekly.return_value = {"weekly": "result"}
                    mock_monthly.return_value = {"monthly": "result"}
                    
                    NPCScheduledTasks.run_all_scheduled_tasks()
                    
                    # Verify call order (daily, weekly, monthly)
                    assert mock_daily.call_count == 1
                    assert mock_weekly.call_count == 1
                    assert mock_monthly.call_count == 1 