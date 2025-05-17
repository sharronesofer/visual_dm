"""
Role model for user roles and permissions.
"""

from app.core.database import db
from sqlalchemy.orm import relationship
from app.core.models.permission import Permission, role_permissions
from datetime import datetime

class Role(db.Model):
    """Role model for user authorization."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.relationship(
        'Permission',
        secondary=role_permissions,
        backref=db.backref('roles', lazy='dynamic'),
        lazy='dynamic'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship('User', back_populates='role')
    
    def __init__(self, name: str, description: str = None, permissions: list = None):
        """
        Initialize a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permission strings or Permission objects
        """
        self.name = name
        self.description = description
        if permissions:
            # Convert permission names to Permission objects if needed
            perms = []
            for perm in permissions:
                if isinstance(perm, str):
                    perm_obj = Permission.query.filter_by(name=perm).first()
                    if perm_obj:
                        perms.append(perm_obj)
                else:
                    perms.append(perm)
            self.permissions = perms
        else:
            self.permissions = []
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if role has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            bool: True if role has permission
        """
        return self.permissions.filter_by(name=permission).count() > 0
    
    def add_permission(self, permission: str) -> None:
        """
        Add a permission to the role.
        
        Args:
            permission: Permission to add
        """
        perm = Permission.query.filter_by(name=permission).first()
        if perm and not self.permissions.filter_by(name=permission).first():
            self.permissions.append(perm)
    
    def remove_permission(self, permission: str) -> None:
        """
        Remove a permission from the role.
        
        Args:
            permission: Permission to remove
        """
        perm = Permission.query.filter_by(name=permission).first()
        if perm and self.permissions.filter_by(name=permission).first():
            self.permissions.remove(perm)
    
    @classmethod
    def create_default_roles(cls) -> None:
        """Create default roles if they don't exist."""
        default_roles = [
            {
                'name': 'admin',
                'description': 'Administrator with full access',
                'permissions': ['*']  # Wildcard for all permissions
            },
            {
                'name': 'user',
                'description': 'Regular user with basic access',
                'permissions': ['read:own', 'write:own']
            },
            {
                'name': 'guest',
                'description': 'Guest user with limited access',
                'permissions': ['read:public']
            }
        ]
        
        for role_data in default_roles:
            if not cls.query.filter_by(name=role_data['name']).first():
                role = cls(**role_data)
                db.session.add(role)
        
        db.session.commit()
    
    def __repr__(self) -> str:
        """String representation of the role."""
        return f'<Role {self.name}>' 