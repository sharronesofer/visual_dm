from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID # For ForeignKey references if IDs are UUID

from backend.infrastructure.auth.auth_user.models.base import AuthBaseModel, Base # Use local base model

# Association table: user_roles
# Assuming User.id and Role.id will be UUIDs from AuthBaseModel
user_roles_table = Table(
    'auth_user_roles', Base.metadata, # Changed table name prefix for clarity
    Column('user_id', UUID(as_uuid=True), ForeignKey('auth_users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('auth_roles.id'), primary_key=True)
)

# Association table: role_permissions
# Assuming Role.id and Permission.id will be UUIDs from AuthBaseModel
role_permissions_table = Table(
    'auth_role_permissions', Base.metadata, # Changed table name prefix
    Column('role_id', UUID(as_uuid=True), ForeignKey('auth_roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('auth_permissions.id'), primary_key=True)
)

class User(AuthBaseModel):
    __tablename__ = 'auth_users' # Changed table name prefix
    __table_args__ = (
        UniqueConstraint('email', name='uq_auth_user_email'),
        Index('ix_auth_user_email', 'email'),
        {'extend_existing': True} # In case User table was defined elsewhere by Flask-SQLAlchemy
    )

    # id, created_at, updated_at are inherited from AuthBaseModel (UUID, Timestamps)

    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Fields from old model that are not standard in AuthBaseModel
    password_reset_token = Column(String(128), nullable=True)
    password_reset_sent_at = Column(DateTime(timezone=True), nullable=True)
    # email_verified_at = Column(DateTime(timezone=True), nullable=True) # Example: if you add email verification
    # last_login_at = Column(DateTime(timezone=True), nullable=True) # Example

    # Relationships
    roles = relationship('Role', secondary=user_roles_table, back_populates='users')
    character_relationships = relationship('AuthRelationship', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class Role(AuthBaseModel):
    __tablename__ = 'auth_roles' # Changed table name prefix
    __table_args__ = (
        UniqueConstraint('name', name='uq_auth_role_name'),
        {'extend_existing': True}
    )

    # id, created_at, updated_at are inherited from AuthBaseModel

    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    users = relationship('User', secondary=user_roles_table, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions_table, back_populates='roles')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class Permission(AuthBaseModel):
    __tablename__ = 'auth_permissions' # Changed table name prefix
    __table_args__ = (
        UniqueConstraint('name', name='uq_auth_permission_name'),
        {'extend_existing': True}
    )

    # id, created_at, updated_at are inherited from AuthBaseModel
    
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    roles = relationship('Role', secondary=role_permissions_table, back_populates='permissions')

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>" 