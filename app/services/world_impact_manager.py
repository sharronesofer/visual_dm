from typing import Dict, Any, List
from app.core.models.quest import QuestWorldImpact
from app.core.database import db
from sqlalchemy.exc import SQLAlchemyError

class WorldImpactManager:
    """Manager for tracking and applying world state changes from quest outcomes."""
    def apply_impact(self, quest_id: int, impact_data: Dict[str, Any], world_service) -> None:
        """Apply a world impact and propagate changes via world_service."""
        impact = QuestWorldImpact(quest_id=quest_id, impact_type=impact_data['type'], details=impact_data['details'])
        db.session.add(impact)
        try:
            db.session.commit()
            world_service.apply_impact(impact_data)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError(f"Failed to apply world impact: {e}")

    def get_impacts_for_quest(self, quest_id: int) -> List[QuestWorldImpact]:
        """Get all world impacts for a given quest."""
        return db.session.query(QuestWorldImpact).filter_by(quest_id=quest_id).all() 