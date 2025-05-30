from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.models.base import BaseModel

# Association tables
user_roles = Table(
    'user_roles', BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions', BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        Index('ix_user_email', 'email'),
    )

    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    password_reset_token = Column(String(128), nullable=True)
    password_reset_sent_at = Column(DateTime(timezone=True), nullable=True)

    roles = relationship('Role', secondary=user_roles, back_populates='users')

class Role(BaseModel):
    __tablename__ = 'roles'
    __table_args__ = (
        UniqueConstraint('name', name='uq_role_name'),
    )

    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

class Permission(BaseModel):
    __tablename__ = 'permissions'
    __table_args__ = (
        UniqueConstraint('name', name='uq_permission_name'),
    )

    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(255))
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions') 