from app import db
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

class GlobalSettings(db.Model):
    __tablename__ = 'global_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(JSON)
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        
    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value
        } 