"""
Unified Access Control Service

This module provides a centralized interface for all permission checks, role/permission management, and audit logging.

Features:
- Centralized RBAC/ABAC permission checks
- Role and permission management APIs
- Audit logging integration for all access attempts
- Caching support for performance
- Pluggable authentication adapter stubs for future identity provider integration

Usage Example:

    from app.core.services.access_control_service import access_control_service
    
    # Check permission
    if access_control_service.has_permission(user, 'edit_article'):
        ...
    
    # Assign role
    access_control_service.assign_role(user, role)
    
    # Add permission to role
    access_control_service.add_permission_to_role(role, permission)

Integration Notes:
- All permission checks should use this service for consistency and auditability.
- Extend the ABAC stub for attribute-based access control as needed.
- Use the provided methods for role/permission management to ensure proper logging and cache invalidation.
"""

from typing import List, Optional, Dict, Any
from app.core.models.user import User
from app.core.models.role import Role
from app.core.models.permission import Permission
from app.core.logging.security import log_audit_event
from app.core.utils.cache import Cache
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class AccessControlService:
    def __init__(self, cache: Optional[Cache] = None):
        self.cache = cache or Cache()

    def has_permission(self, user: User, permission: str, resource: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if the user has the specified permission (RBAC/ABAC).
        Logs the access attempt for auditing.
        """
        # RBAC check
        if user.role and permission in [p.name for p in user.role.permissions]:
            self._log_access(user, permission, resource, True)
            return True
        # ABAC stub (extend as needed)
        # if attributes and self._abac_check(user, permission, resource, attributes):
        #     self._log_access(user, permission, resource, True)
        #     return True
        self._log_access(user, permission, resource, False)
        return False

    def _log_access(self, user: User, permission: str, resource: Optional[str], success: bool):
        log_audit_event(
            event_type='access',
            user_id=str(user.id),
            action=permission,
            resource=resource or 'unknown',
            details={'username': user.username},
            success=success
        )

    def get_user_permissions(self, user: User) -> List[str]:
        if user.role:
            return [p.name for p in user.role.permissions]
        return []

    def assign_role(self, user: User, role: Role):
        user.set_role(role)
        db.session.commit()
        logger.info(f"Assigned role {role.name} to user {user.username}")

    def add_permission_to_role(self, role: Role, permission: Permission):
        if permission not in role.permissions:
            role.add_permission(permission.name)
            db.session.commit()
            logger.info(f"Added permission {permission.name} to role {role.name}")

    def remove_permission_from_role(self, role: Role, permission: Permission):
        if permission in role.permissions:
            role.remove_permission(permission.name)
            db.session.commit()
            logger.info(f"Removed permission {permission.name} from role {role.name}")

    # Caching stubs
    def invalidate_cache(self, user: User):
        self.cache.invalidate(f"user_permissions:{user.id}")

    # Pluggable authentication adapter stub
    def set_auth_adapter(self, adapter):
        self.auth_adapter = adapter

    # ABAC stub for future extension
    # def _abac_check(self, user: User, permission: str, resource: Optional[str], attributes: Dict[str, Any]) -> bool:
    #     # Implement attribute-based access control logic here
    #     return False

    def create_permission(self, name: str, description: str = None) -> Permission:
        perm = Permission.get_or_create(name, description)
        logger.info(f"Created or fetched permission: {name}")
        return perm

    def create_role(self, name: str, description: str = None) -> Role:
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
            logger.info(f"Created role: {name}")
        return role

    def assign_permission_to_user(self, user: User, permission: Permission):
        # For future ABAC or direct assignment support
        if not hasattr(user, 'permissions'):
            user.permissions = []
        if permission not in user.permissions:
            user.permissions.append(permission)
            db.session.commit()
            logger.info(f"Assigned permission {permission.name} directly to user {user.username}")

access_control_service = AccessControlService() 