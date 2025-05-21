from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
# Assuming Base is available from backend.core.database or a similar central place
# For example: from backend.core.database import Base
# If Base is defined in backend_backup/app/models/base.py, that needs to be handled.
# For now, I'll assume a placeholder Base or it needs to be imported correctly.

# Placeholder for Base if its actual import path is unknown
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

character_skills = Table(
    'character_skills',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSON, nullable=False)  # Stores ability scores, HP, etc.
    background = Column(String(100))
    alignment = Column(String(50))
    # equipment = Column(JSON, default=list)  # REMOVED: Inventory is now managed by Inventory/InventoryItem
    skills = relationship('Skill', secondary=character_skills, backref='characters')
    notes = Column(JSON, default=list)  # Character-specific notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Fields from CharacterBuilder that might be missing and could be added:
    # attributes_json = Column(JSON) # Or expand stats to include all attributes
    # xp = Column(Integer, default=0)
    # hp = Column(Integer) # This might be part of 'stats' JSON
    # mp = Column(Integer) # This might be part of 'stats' JSON
    # gold = Column(Integer, default=0)
    # faction_affiliations: Managed by Relationship model
    # reputation: Managed by Relationship model or a direct field
    # ... other fields from CharacterBuilder.finalize() output

    def __repr__(self):
        return f"<Character {self.name}>"

    def to_builder(self):
        from backend.systems.character.core.character_builder_class import CharacterBuilder, RACES_DATA, FEATS_LIST # Assuming FEATS_LIST is what builder uses
        # Assuming SKILL_LIST is defined in character_builder_class or accessible
        # For now, let's fetch all skill names from the DB as a list for the builder.
        # This might need refinement based on where CharacterBuilder expects its skill_list from.
        from backend.core.database import get_db_session # Temporary for fetching skills
        db_session = next(get_db_session())
        all_skills_from_db = [s.name for s in db_session.query(Skill.name).all()]
        db_session.close()

        # Initialize builder with necessary static data
        # Ensure RACES_DATA and FEATS_LIST are correctly loaded in CharacterBuilder or passed appropriately
        builder = CharacterBuilder(race_data=RACES_DATA, feat_data=FEATS_LIST, skill_list=all_skills_from_db)

        builder.character_name = self.name
        if self.race in builder.race_data:
            builder.selected_race = self.race
        else:
            print(f"Warning: Character race '{self.race}' not found in builder's race_data.")

        # Populate attributes
        if isinstance(self.stats, dict):
            for attr, value in self.stats.items():
                if attr.upper() in builder.attributes: # Builder uses uppercase keys like STR, DEX
                    builder.attributes[attr.upper()] = value
                # Also handle direct stat fields if they were on builder (hp, mp, ac, xp, level)
                elif hasattr(builder, attr):
                    setattr(builder, attr, value)
        
        builder.level = self.level
        # if hasattr(self, 'xp'): builder.xp = self.xp # If Character ORM has xp
        # if hasattr(self, 'gold'): builder.gold = self.gold # If Character ORM has gold
        # Note: HP, MP, AC are usually derived in builder.finalize(), 
        # so not setting them directly unless the builder expects it.

        # Populate skills (names)
        builder.selected_skills = [skill.name for skill in self.skills]

        # Populate feats (names)
        # This assumes feats are stored in a way that can be retrieved and matched to builder.feat_data keys
        # If Character.feats is a relationship to a Feat model similar to Skill:
        # builder.selected_feats = [feat.name for feat in self.feats_relationship] # Assuming feats_relationship
        # For now, if feats are stored as a list of names in self.stats or another field:
        # if isinstance(self.stats.get('feats'), list):
        #    builder.selected_feats = [f for f in self.stats['feats'] if f in builder.feat_data]

        # Starter kit is usually applied during initial creation, not typically reverse-populated this way.
        # If needed, specific equipment/gold from inventory could be mapped back if the builder needs it.

        # Alignment, background, notes if they exist on Character ORM and builder has fields for them
        if hasattr(self, 'alignment') and hasattr(builder, 'alignment'): # builder doesn't have alignment field
             pass # builder.alignment = self.alignment
        if hasattr(self, 'background') and hasattr(builder, 'background'): # builder doesn't have background
             pass # builder.background = self.background
        # Notes: builder doesn't have a direct notes field. Could be part of some other dict.

        return builder

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    ability = Column(String(50))  # Associated ability score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Skill {self.name}>"

__all__ = ["Character", "Skill"] 