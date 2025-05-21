from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .models import (
    QuestState, QuestStateTransition, QuestVersion, QuestTimestampMixin, QuestRelationship,
    QuestProgress, QuestReward, QuestArchive
)
from backend.systems.integration.event_bus import integration_event_bus
from backend.systems.integration.state_sync import state_sync_manager
from backend.systems.integration.validation import validation_manager
from backend.systems.integration.monitoring import integration_logger, integration_metrics, integration_alerting

class QuestStateManager(QuestTimestampMixin):
    """
    Main entry point for enhanced quest state management system.
    Coordinates state transitions, versioning, progress, rewards, archiving, and API integration.
    """
    def __init__(self, quest_id: str, initial_data: Dict[str, Any]):
        self.quest_id = quest_id
        self.state = QuestState.LOCKED
        self.versions = []  # List[QuestVersion]
        self.transitions = []  # List[QuestStateTransition]
        self.relationship = QuestRelationship(quest_id)
        self.progress = QuestProgress(quest_id)
        self.reward = QuestReward(quest_id)
        self.archive: Optional[QuestArchive] = None
        self.set_created()
        self.data = initial_data
        self.save_version(author=initial_data.get('author', None))

    async def transition_state(self, to_state: QuestState, reason: Optional[str] = None):
        # Validate transition
        if not validation_manager.validate('quest_state_transition', {'from': self.state, 'to': to_state}):
            raise ValueError(f"Invalid state transition: {self.state} -> {to_state}")
        transition = QuestStateTransition(self.state, to_state, reason=reason)
        self.transitions.append(transition)
        self.state = to_state
        self.update_timestamp()
        self.save_version()
        # Integration hooks
        await integration_event_bus.dispatch('quest_state_changed', quest_id=self.quest_id, to_state=to_state, reason=reason)
        await state_sync_manager.notify_state_change('quest', {'quest_id': self.quest_id, 'state': to_state})
        await integration_logger.log(20, f"Quest {self.quest_id} transitioned to {to_state}")
        await integration_metrics.record('quest_state_transition', 1)

    def save_version(self, author: Optional[str] = None):
        version_id = len(self.versions) + 1
        version = QuestVersion(version_id, self.quest_id, self.data.copy(), author=author)
        if self.versions:
            version.diff = version.compute_diff(self.versions[-1].data)
        self.versions.append(version)

    async def update_progress(self, objective_id: str, value: Any):
        self.progress.update_progress(objective_id, value)
        self.update_timestamp()
        self.save_version()
        # Integration hooks
        await integration_event_bus.dispatch('quest_progress_updated', quest_id=self.quest_id, objective_id=objective_id, value=value)
        await state_sync_manager.notify_state_change('quest', {'quest_id': self.quest_id, 'progress': self.progress})
        await integration_logger.log(20, f"Quest {self.quest_id} progress updated: {objective_id} -> {value}")
        await integration_metrics.record('quest_progress_update', 1)

    async def claim_reward(self):
        self.reward.claim()
        self.save_version()
        # Integration hooks
        await integration_event_bus.dispatch('quest_reward_claimed', quest_id=self.quest_id)
        await integration_logger.log(20, f"Quest {self.quest_id} reward claimed")
        await integration_metrics.record('quest_reward_claim', 1)

    async def expire(self):
        self.transition_state(QuestState.EXPIRED, reason="Expired by system or schedule.")
        self.reward.expire()
        self.save_version()
        # Integration hooks
        await integration_event_bus.dispatch('quest_expired', quest_id=self.quest_id)
        await integration_logger.log(20, f"Quest {self.quest_id} expired")
        await integration_metrics.record('quest_expire', 1)

    async def archive_quest(self):
        self.archive = QuestArchive(self.quest_id, self.data.copy())
        self.save_version()
        # Integration hooks
        await integration_event_bus.dispatch('quest_archived', quest_id=self.quest_id)
        await integration_logger.log(20, f"Quest {self.quest_id} archived")
        await integration_metrics.record('quest_archive', 1)

    async def restore_from_archive(self):
        if self.archive:
            self.data = self.archive.restore()
            self.save_version()
            # Integration hooks
            await integration_event_bus.dispatch('quest_restored', quest_id=self.quest_id)
            await integration_logger.log(20, f"Quest {self.quest_id} restored from archive")
            await integration_metrics.record('quest_restore', 1)

    def add_prerequisite(self, prereq_id: str):
        self.relationship.add_prerequisite(prereq_id)

    def add_child(self, child_id: str):
        self.relationship.add_child(child_id)

    def is_expired(self) -> bool:
        return super().is_expired()

    def percent_complete(self) -> float:
        # Always reflect the current objectives and progress
        return self.progress.percent_complete() 
