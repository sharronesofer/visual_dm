from app.models import db

class CharacterSubclass(db.Model):
    """Model for character subclass information."""
    __tablename__ = 'character_subclasses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    class_id = db.Column(db.Integer, db.ForeignKey('character_classes.id'), nullable=False)
    features = db.Column(db.JSON)  # List of subclass features by level
    spell_list = db.Column(db.JSON)  # List of available spells
    prerequisites = db.Column(db.JSON)  # Requirements for taking this subclass
    
    # Relationships
    characters = db.relationship('Character', backref='character_subclass', lazy='dynamic')
    character_class = db.relationship('CharacterClass', backref='subclasses', lazy=True)
    
    def __repr__(self):
        return f'<CharacterSubclass {self.name}>' 