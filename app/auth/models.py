"""
Authentication models.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.database import db

# class User(UserMixin, db.Model):
#     """User model for authentication."""
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(128), nullable=False)
#     role = db.Column(db.String(20), nullable=False, default='user', index=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     last_login = db.Column(db.DateTime)
#     is_active = db.Column(db.Boolean, default=True)
#     is_admin = db.Column(db.Boolean, default=False)
#     campaigns = db.relationship('Campaign', backref='owner', lazy='dynamic')
#     characters = db.relationship('Character', backref='creator', lazy='dynamic')
#     npcs = db.relationship('NPC', backref='creator', lazy='dynamic')
#     locations = db.relationship('Location', backref='creator', lazy='dynamic')
#     items = db.relationship('Item', backref='creator', lazy='dynamic')
#     quests = db.relationship('Quest', backref='creator', lazy='dynamic')
#     encounters = db.relationship('Encounter', backref='creator', lazy='dynamic')
#     def __init__(self, username, email, password=None, role='user'):
#         self.username = username
#         self.email = email
#         self.role = role
#         if password:
#             self.set_password(password)
#     def set_password(self, password):
#         if not self.validate_password_strength(password):
#             raise ValueError("Password does not meet strength requirements.")
#         self.password_hash = generate_password_hash(password)
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#     @staticmethod
#     def validate_password_strength(password):
#         import re
#         if len(password) < 8:
#             return False
#         if not re.search(r"[A-Za-z]", password):
#             return False
#         if not re.search(r"\d", password):
#             return False
#         return True
#     def update_last_login(self):
#         self.last_login = datetime.utcnow()
#         db.session.commit()
#     def __repr__(self):
#         return f'<User {self.username}>'
#     @property
#     def is_authenticated(self):
#         return True
#     @property
#     def is_anonymous(self):
#         return False
#     def get_id(self):
#         return str(self.id) 