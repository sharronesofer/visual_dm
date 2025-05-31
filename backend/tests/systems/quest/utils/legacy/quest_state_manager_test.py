import pytest
from datetime import timedelta
from quests.quest_state_manager import QuestStateManager
from quests.models import QuestState

def test_state_transitions():
    manager = QuestStateManager('q1', {'title': 'Test Quest'})
    assert manager.state == QuestState.LOCKED
    manager.transition_state(QuestState.AVAILABLE)
    assert manager.state == QuestState.AVAILABLE
    manager.transition_state(QuestState.ACTIVE)
    assert manager.state == QuestState.ACTIVE
    manager.transition_state(QuestState.PARTIALLY_COMPLETE)
    assert manager.state == QuestState.PARTIALLY_COMPLETE
    manager.transition_state(QuestState.COMPLETE)
    assert manager.state == QuestState.COMPLETE
    with pytest.raises(ValueError):
        manager.transition_state(QuestState.LOCKED)  # Invalid backward transition

def test_versioning():
    manager = QuestStateManager('q2', {'title': 'Versioned Quest'})
    initial_version_count = len(manager.versions)
    manager.data['title'] = 'Updated Title'
    manager.save_version()
    assert len(manager.versions) == initial_version_count + 1
    assert manager.versions[-1].diff['title'] == 'Updated Title'

def test_progress_tracking():
    manager = QuestStateManager('q3', {'title': 'Progress Quest'})
    manager.progress.objectives = {'obj1': 3, 'obj2': 2}
    # Initialize progress for all objectives
    for obj in manager.progress.objectives:
        manager.progress.progress[obj] = 0
    manager.update_progress('obj1', 1)
    assert manager.progress.progress['obj1'] == 1
    assert manager.percent_complete() == pytest.approx(1/6)
    manager.update_progress('obj1', 3)
    manager.update_progress('obj2', 2)
    assert manager.progress.is_complete()
    assert manager.percent_complete() == 1.0

def test_reward_claim_and_expiry():
    manager = QuestStateManager('q4', {'title': 'Reward Quest'})
    assert not manager.reward.is_claimed()
    manager.claim_reward()
    assert manager.reward.is_claimed()
    manager = QuestStateManager('q5', {'title': 'Expire Quest'})
    manager.expire()
    assert manager.state == QuestState.EXPIRED
    assert manager.reward.is_expired()

def test_archiving_and_restoration():
    manager = QuestStateManager('q6', {'title': 'Archive Quest'})
    manager.archive_quest()
    assert manager.archive is not None
    manager.data['title'] = 'Changed'
    manager.restore_from_archive()
    assert manager.data['title'] == 'Archive Quest' 
