"""
Permission model for RBAC.
"""

from datetime import datetime
from app.core.database import db

# Association table for Role <-> Permission (many-to-many)
role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Permission {self.name}>'

    @classmethod
    def get_or_create(cls, name: str, description: str = None):
        perm = cls.query.filter_by(name=name).first()
        if not perm:
            perm = cls(name=name, description=description)
            db.session.add(perm)
            db.session.commit()
        return perm 