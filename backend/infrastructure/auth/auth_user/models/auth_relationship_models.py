"""
Auth Relationship Models
-----------------------
Models for managing authentication relationships between users and characters.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Dict, Any

from backend.infrastructure.auth.auth_user.models.base import AuthBaseModel, Base

class AuthRelationship(AuthBaseModel):
    """
    Model representing the relationship between a user and a character.
    Defines permissions and ownership for character access control.
    """
    __tablename__ = 'auth_relationships'
    __table_args__ = (
        UniqueConstraint('user_id', 'character_id', name='uq_auth_relationship_user_character'),
        Index('ix_auth_relationship_user_id', 'user_id'),
        Index('ix_auth_relationship_character_id', 'character_id'),
        {'extend_existing': True}
    )

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id'), nullable=False)
    character_id = Column(UUID(as_uuid=True), nullable=False)  # References character system
    
    # Relationship properties
    is_owner = Column(Boolean, default=False, nullable=False)
    permissions = Column(JSON, default=list, nullable=False)  # List of permission strings
    
    # Optional metadata
    relationship_type = Column(String(50), default='viewer', nullable=False)  # owner, editor, viewer
    notes = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='character_relationships')

    def __repr__(self):
        return f"<AuthRelationship(user_id={self.user_id}, character_id={self.character_id}, is_owner={self.is_owner})>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if this relationship grants a specific permission."""
        if self.is_owner:
            return True
        return permission in (self.permissions or [])
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to this relationship."""
        if not self.permissions:
            self.permissions = []
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """Remove a permission from this relationship."""
        if self.permissions and permission in self.permissions:
            self.permissions.remove(permission)
    
    def get_all_permissions(self) -> List[str]:
        """Get all permissions for this relationship."""
        if self.is_owner:
            return [
                'read', 'write', 'delete', 'share', 'manage_permissions',
                'transfer_ownership', 'view_stats', 'edit_stats', 'manage_inventory',
                'manage_equipment', 'manage_spells', 'manage_notes'
            ]
        return self.permissions or []

# Update User model to include relationship back-reference
# This should be added to user_models.py but we'll handle it via imports 