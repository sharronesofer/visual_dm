"""
User model for authentication and authorization.
"""

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.database import db
from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.models.save import SaveGame

class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    save_games = relationship('SaveGame', back_populates='user')
    
    @hybrid_property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def set_password(self, password: str) -> None:
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the given password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if the user has a specific permission via their role."""
        if self.role and hasattr(self.role, 'permissions'):
            return self.role.has_permission(permission_name)
        return False
    
    def set_role(self, role):
        """Set the user's role."""
        self.role = role
        db.session.commit()
    
    def verify_email(self, token: str) -> bool:
        """Verify the user's email with the given token."""
        if self.verification_token == token:
            self.is_verified = True
            self.verification_token = None
            db.session.commit()
            return True
        return False
    
    def set_reset_token(self, token: str, expires_in: int = 3600) -> None:
        """Set a password reset token that expires in the given number of seconds."""
        self.reset_token = token
        self.reset_token_expires = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
    
    def check_reset_token(self, token: str) -> bool:
        """Check if the given reset token is valid and not expired."""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return self.reset_token == token
    
    def to_dict(self) -> dict:
        """Convert the user object to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.name if self.role else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 