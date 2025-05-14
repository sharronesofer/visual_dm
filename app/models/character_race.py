from app.models import db

class CharacterRace(db.Model):
    """Model for character race information."""
    __tablename__ = 'character_races'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    size = db.Column(db.String(20), nullable=False)  # e.g., "Medium", "Small"
    speed = db.Column(db.Integer, nullable=False)  # Base movement speed in feet
    ability_score_increases = db.Column(db.JSON)  # Ability score bonuses
    racial_traits = db.Column(db.JSON)  # List of racial traits
    languages = db.Column(db.JSON)  # List of known languages
    subraces = db.Column(db.JSON)  # Available subraces and their features
    age_range = db.Column(db.JSON)  # Min and max age range
    alignment_tendencies = db.Column(db.JSON)  # Common alignment tendencies
    height_range = db.Column(db.JSON)  # Min and max height range
    weight_range = db.Column(db.JSON)  # Min and max weight range
    
    # Relationships
    characters = db.relationship('Character', foreign_keys='Character.race_id', lazy='dynamic')
    
    def __repr__(self):
        return f'<CharacterRace {self.name}>' 