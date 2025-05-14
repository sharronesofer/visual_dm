from app.models import db

class CharacterBackground(db.Model):
    """Model for character background information."""
    __tablename__ = 'character_backgrounds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    skill_proficiencies = db.Column(db.JSON)  # List of skill proficiencies
    tool_proficiencies = db.Column(db.JSON)  # List of tool proficiencies
    languages = db.Column(db.JSON)  # List of languages
    equipment = db.Column(db.JSON)  # List of starting equipment
    features = db.Column(db.JSON)  # List of background features
    personality_traits = db.Column(db.JSON)  # List of personality traits
    ideals = db.Column(db.JSON)  # List of ideals
    bonds = db.Column(db.JSON)  # List of bonds
    flaws = db.Column(db.JSON)  # List of flaws
    
    # Relationships
    characters = db.relationship('Character', backref='character_background', lazy='dynamic')
    
    def __repr__(self):
        return f'<CharacterBackground {self.name}>' 