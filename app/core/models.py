"""
Database models.
"""

from datetime import datetime
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.database import db

class Role(db.Model):
    """Role model."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

# class User(db.Model):
#     """User model."""
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(255), nullable=False)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     last_login = db.Column(db.DateTime)
#     def set_password(self, password: str) -> None:
#         self.password_hash = generate_password_hash(password)
#     def check_password(self, password: str) -> bool:
#         return check_password_hash(self.password_hash, password)
#     def __repr__(self):
#         return f'<User {self.username}>'

class Character(db.Model):
    """Character model."""
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='characters', lazy=True)
    
    def __repr__(self):
        return f'<Character {self.name}>'

class Quest(db.Model):
    """Quest model."""
    __tablename__ = 'quests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='not_started')
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    character = db.relationship('Character', backref='quests', lazy=True)
    
    def __repr__(self):
        return f'<Quest {self.title}>'

class Event(db.Model):
    """Event model."""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    quest = db.relationship('Quest', backref='events', lazy=True)
    character = db.relationship('Character', backref='events', lazy=True)
    
    def __repr__(self):
        return f'<Event {self.title}>' 