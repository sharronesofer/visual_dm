"""
Role model for user roles and permissions.
"""

from app.core.database import db
from sqlalchemy.orm import relationship

class Role(db.Model):
    """Role model for user authorization."""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default=list)
    
    # Relationships
    users = relationship('User', back_populates='role')
    
    def __init__(self, name: str, description: str = None, permissions: list = None):
        """
        Initialize a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permission strings
        """
        self.name = name
        self.description = description
        self.permissions = permissions or []
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if role has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            bool: True if role has permission
        """
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> None:
        """
        Add a permission to the role.
        
        Args:
            permission: Permission to add
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """
        Remove a permission from the role.
        
        Args:
            permission: Permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
    
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