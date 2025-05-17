"""
Session model for managing user sessions.
"""

from datetime import datetime
from app.core.database import db
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class Session(db.Model):
    """Session model for tracking user sessions."""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    device_info = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_valid(self) -> bool:
        """Check if the session is valid and not expired."""
        return (
            self.is_active and
            datetime.utcnow() <= self.expires_at
        )
    
    def invalidate(self) -> None:
        """Invalidate the session."""
        self.is_active = False
        db.session.commit()
    
    def update_last_accessed(self) -> None:
        """Update the last accessed timestamp."""
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convert the session object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_info': self.device_info,
            'ip_address': self.ip_address,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
    
    def __repr__(self):
        return f'<Session {self.id} for User {self.user_id}>' 