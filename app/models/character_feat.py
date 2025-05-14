"""
Character Feat model for tracking character feats.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db_base import Base

class CharacterFeat(Base):
    """Model for character feats."""
    __tablename__ = 'character_feats'

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    feat_id = Column(Integer, ForeignKey('feats.id'), nullable=False)
    level_gained = Column(Integer, nullable=False)

    # Relationships
    character = relationship("Character", back_populates="feats")
    feat = relationship("Feat", back_populates="characters")

    def __repr__(self):
        """String representation of the character feat."""
        return f"<CharacterFeat(character_id={self.character_id}, feat_id={self.feat_id}, level_gained={self.level_gained})>" 