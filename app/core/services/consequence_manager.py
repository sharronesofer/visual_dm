"""
Service for managing consequences based on player infractions.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence, ConsequenceType
from app.core.enums import InfractionSeverity
from app.core.database import db

# Default configuration for consequence parameters (could be loaded from config file)
CONSEQUENCE_CONFIG = {
    InfractionSeverity.MINOR: [
        {"type": ConsequenceType.WARNING, "duration": 0},
        {"type": ConsequenceType.FINE, "duration": 0},
    ],
    InfractionSeverity.MODERATE: [
        {"type": ConsequenceType.FINE, "duration": 0},
        {"type": ConsequenceType.ITEM_CONFISCATION, "duration": 0},
        {"type": ConsequenceType.NPC_HOSTILITY, "duration": 60 * 60 * 24},  # 1 day
    ],
    InfractionSeverity.MAJOR: [
        {"type": ConsequenceType.NPC_HOSTILITY, "duration": 60 * 60 * 24 * 3},  # 3 days
        {"type": ConsequenceType.SUSPENSION, "duration": 60 * 60 * 24},  # 1 day
        {"type": ConsequenceType.BOUNTY, "duration": 0},
    ],
    InfractionSeverity.CRITICAL: [
        {"type": ConsequenceType.BAN, "duration": 0},
    ],
}

class ConsequenceManager:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or db.session

    def determine_consequences(self, infraction: Infraction) -> List[Consequence]:
        """Determine consequences for a given infraction based on severity and config."""
        config = CONSEQUENCE_CONFIG.get(infraction.severity, [])
        consequences = []
        for entry in config:
            expires_at = None
            if entry["duration"] > 0:
                expires_at = datetime.utcnow() + timedelta(seconds=entry["duration"])
            consequence = Consequence(
                player_id=infraction.player_id,
                character_id=infraction.character_id,
                infraction_id=infraction.id,
                type=entry["type"],
                severity=infraction.severity,
                active=True,
                issued_at=datetime.utcnow(),
                expires_at=expires_at,
                details=f"Auto-applied for infraction {infraction.id}"
            )
            consequences.append(consequence)
        return consequences

    def apply_consequences(self, infraction: Infraction) -> List[Consequence]:
        """Apply consequences for a given infraction and persist them."""
        consequences = self.determine_consequences(infraction)
        try:
            for consequence in consequences:
                self.session.add(consequence)
            self.session.commit()
            return consequences
        except Exception as e:
            self.session.rollback()
            raise e

    def expire_consequences(self):
        """Expire consequences whose expiration time has passed."""
        now = datetime.utcnow()
        expired = self.session.query(Consequence).filter(
            Consequence.active == True,
            Consequence.expires_at != None,
            Consequence.expires_at <= now
        ).all()
        for consequence in expired:
            consequence.active = False
        self.session.commit()
        return expired

    def get_active_consequences(self, player_id: int) -> List[Consequence]:
        return self.session.query(Consequence).filter_by(player_id=player_id, active=True).all() 