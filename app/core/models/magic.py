"""
Magic system models.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, JSON, ForeignKey, Enum as SQLEnum
from datetime import datetime
from app.core.database import db

class SpellSchool(str, Enum):
    """Spell schools enumeration."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"
    ARCANE = "arcane"  # Generic arcane magic
    DIVINE = "divine"  # Divine/clerical magic
    NATURE = "nature"  # Druidic/natural magic
    PSIONIC = "psionic"  # Mental/psychic magic

class Spell(db.Model):
    """Model for spells."""
    __tablename__ = 'spells'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    level: Mapped[int] = mapped_column(Integer, default=0)
    school: Mapped[SpellSchool] = mapped_column(SQLEnum(SpellSchool))
    casting_time: Mapped[str] = mapped_column(String(50), default="1 action")
    range: Mapped[str] = mapped_column(String(50), default="self")
    components: Mapped[Dict] = mapped_column(JSON, default=dict)
    duration: Mapped[str] = mapped_column(String(50), default="instantaneous")
    concentration: Mapped[bool] = mapped_column(default=False)
    ritual: Mapped[bool] = mapped_column(default=False)
    effects: Mapped[List[Dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    characters = relationship('Character', secondary='character_spells', back_populates='spells')

    def to_dict(self) -> Dict:
        """Convert the spell to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'school': self.school.value,
            'casting_time': self.casting_time,
            'range': self.range,
            'components': self.components,
            'duration': self.duration,
            'concentration': self.concentration,
            'ritual': self.ritual,
            'effects': self.effects,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def calculate_effect(self, target: Any) -> Dict:
        """Calculate the effect of the spell on a target."""
        result = {
            'success': True,
            'effects': [],
            'messages': []
        }

        for effect in self.effects:
            effect_type = effect.get('type')
            if effect_type == 'damage':
                # Calculate damage
                import random
                dice = effect.get('dice', '1d6').split('d')
                num_dice = int(dice[0])
                die_size = int(dice[1])
                damage = sum(random.randint(1, die_size) for _ in range(num_dice))
                result['effects'].append({
                    'type': 'damage',
                    'amount': damage,
                    'damage_type': effect.get('damage_type', 'magical')
                })
                result['messages'].append(f"Deals {damage} {effect.get('damage_type', 'magical')} damage")
            elif effect_type == 'heal':
                # Calculate healing
                import random
                dice = effect.get('dice', '1d8').split('d')
                num_dice = int(dice[0])
                die_size = int(dice[1])
                healing = sum(random.randint(1, die_size) for _ in range(num_dice))
                result['effects'].append({
                    'type': 'heal',
                    'amount': healing
                })
                result['messages'].append(f"Heals for {healing} hit points")
            elif effect_type == 'status':
                # Apply status effect
                result['effects'].append({
                    'type': 'status',
                    'status': effect.get('status'),
                    'duration': effect.get('duration', 1)
                })
                result['messages'].append(f"Applies {effect.get('status')} status for {effect.get('duration', 1)} rounds")

        return result 