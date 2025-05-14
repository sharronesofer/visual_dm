from app.core.database import db

class Equipment(db.Model):
    """Equipment model for managing items that can be equipped by characters."""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    equipment_type = db.Column(db.String(50), nullable=False)  # weapon, armor, accessory
    slot = db.Column(db.String(50), nullable=False)  # head, chest, main_hand, etc.
    level_requirement = db.Column(db.Integer, default=1)
    rarity = db.Column(db.String(20), default='common')
    
    # Stats
    armor_class = db.Column(db.Integer, default=0)
    damage_bonus = db.Column(db.Integer, default=0)
    hit_bonus = db.Column(db.Integer, default=0)
    
    # Special attributes
    attributes = db.Column(db.JSON)  # Store special effects, requirements, etc.
    
    # Shop and inventory management
    base_price = db.Column(db.Integer, default=0)
    is_unique = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    @property
    def full_stats(self):
        """Get complete stats including base and special attributes."""
        stats = {
            'armor_class': self.armor_class,
            'damage_bonus': self.damage_bonus,
            'hit_bonus': self.hit_bonus
        }
        if self.attributes:
            stats.update(self.attributes)
        return stats

class EquipmentInstance(db.Model):
    """Instance of equipment owned by a character or shop."""
    __tablename__ = 'equipment_instances'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    owner_type = db.Column(db.String(50))  # character, shop, etc.
    owner_id = db.Column(db.Integer)
    condition = db.Column(db.Integer, default=100)  # 0-100
    custom_name = db.Column(db.String(100))
    
    equipment = db.relationship('Equipment', backref='instances')
    
    def __repr__(self):
        return f'<EquipmentInstance {self.equipment.name} owned by {self.owner_type}:{self.owner_id}>' 