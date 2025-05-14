"""
Service for managing player infractions and punitive consequences.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.models.infraction import Infraction
from app.core.enums import InfractionType, InfractionSeverity
from app.core.database import db
from app.core.services.consequence_manager import ConsequenceManager

class InfractionService:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or db.session

    def record_infraction(self, player_id: int, character_id: int, type: InfractionType, severity: InfractionSeverity, location: Optional[str] = None, target_npc_id: Optional[int] = None, details: Optional[str] = None) -> Infraction:
        infraction = Infraction(
            player_id=player_id,
            character_id=character_id,
            type=type,
            severity=severity,
            location=location,
            target_npc_id=target_npc_id,
            details=details,
            resolved=False
        )
        try:
            self.session.add(infraction)
            self.session.commit()
            # Apply consequences automatically
            manager = ConsequenceManager(self.session)
            manager.apply_consequences(infraction)
            return infraction
        except Exception as e:
            self.session.rollback()
            raise e

    def get_player_infractions(self, player_id: int, resolved: Optional[bool] = None) -> List[Infraction]:
        query = self.session.query(Infraction).filter_by(player_id=player_id)
        if resolved is not None:
            query = query.filter_by(resolved=resolved)
        return query.order_by(Infraction.timestamp.desc()).all()

    def resolve_infraction(self, infraction_id: int) -> bool:
        infraction = self.session.query(Infraction).get(infraction_id)
        if not infraction:
            return False
        infraction.resolved = True
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e

    @staticmethod
    def calculate_severity(type: InfractionType, frequency: int = 1) -> InfractionSeverity:
        # Example logic: escalate severity based on type and frequency
        if type in [InfractionType.ATTACK_FRIENDLY_NPC, InfractionType.THEFT]:
            if frequency >= 3:
                return InfractionSeverity.MAJOR
            elif frequency == 2:
                return InfractionSeverity.MODERATE
            else:
                return InfractionSeverity.MINOR
        elif type in [InfractionType.PROPERTY_DAMAGE, InfractionType.TRESPASSING]:
            return InfractionSeverity.MODERATE if frequency > 1 else InfractionSeverity.MINOR
        elif type in [InfractionType.CHEATING, InfractionType.EXPLOIT, InfractionType.HARASSMENT]:
            return InfractionSeverity.CRITICAL
        return InfractionSeverity.MINOR 