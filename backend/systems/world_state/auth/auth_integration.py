"""
Authentication Integration for World State System

Provides role-based access control and permission management for world state operations.
Integrates with your existing auth system while maintaining security.

Permissions:
- world_state.read: View world state data
- world_state.write: Modify world state
- world_state.admin: Full administrative access
- world_state.region.{region_id}: Region-specific access
- world_state.faction.{faction_id}: Faction-specific access

Usage:
    # Wrap your service with auth
    auth_service = AuthenticatedWorldStateService(world_state_service, auth_manager)
    
    # All operations now require authentication
    result = await auth_service.get_state_variable("population", user=current_user)
"""

from typing import Optional, Dict, Any, List, Set, Protocol
from uuid import UUID
from datetime import datetime
import logging
from enum import Enum

from backend.systems.world_state.services.services import WorldStateService
from backend.systems.world_state.world_types import StateCategory

logger = logging.getLogger(__name__)


class Permission(Enum):
    """World state permissions"""
    READ = "world_state.read"
    WRITE = "world_state.write"
    ADMIN = "world_state.admin"
    READ_HISTORICAL = "world_state.read_historical"
    MANAGE_REGIONS = "world_state.manage_regions"
    MANAGE_FACTIONS = "world_state.manage_factions"


class User:
    """User model for authentication"""
    def __init__(self, user_id: UUID, username: str, roles: List[str], permissions: Set[str]):
        self.user_id = user_id
        self.username = username
        self.roles = roles
        self.permissions = permissions
        self.is_authenticated = True


class AuthManagerProtocol(Protocol):
    """Protocol for authentication managers"""
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        ...
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission"""
        ...
    
    async def get_user_regions(self, user: User) -> List[str]:
        """Get regions user has access to"""
        ...
    
    async def get_user_factions(self, user: User) -> List[UUID]:
        """Get factions user has access to"""
        ...


class WorldStateAuthManager:
    """Default authentication manager for world state"""
    
    def __init__(self):
        # Simple role-based permissions mapping
        self.role_permissions = {
            'admin': {
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.ADMIN.value,
                Permission.READ_HISTORICAL.value,
                Permission.MANAGE_REGIONS.value,
                Permission.MANAGE_FACTIONS.value
            },
            'moderator': {
                Permission.READ.value,
                Permission.WRITE.value,
                Permission.READ_HISTORICAL.value,
                Permission.MANAGE_REGIONS.value
            },
            'player': {
                Permission.READ.value
            },
            'faction_leader': {
                Permission.READ.value,
                Permission.WRITE.value  # Limited to their faction's regions
            }
        }
        
        # User database (in production, this would be from your auth service)
        self.users = {}
        self.user_regions = {}  # user_id -> list of region_ids
        self.user_factions = {}  # user_id -> list of faction_ids
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token (mock implementation)"""
        # In production, this would validate JWT token and fetch user from database
        if token == "admin_token":
            return User(
                user_id=UUID("11111111-1111-1111-1111-111111111111"),
                username="admin",
                roles=["admin"],
                permissions=self.role_permissions["admin"]
            )
        elif token == "player_token":
            return User(
                user_id=UUID("22222222-2222-2222-2222-222222222222"),
                username="player1",
                roles=["player"],
                permissions=self.role_permissions["player"]
            )
        return None
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission"""
        return permission in user.permissions
    
    async def get_user_regions(self, user: User) -> List[str]:
        """Get regions user has access to"""
        # Admin can access all regions
        if Permission.ADMIN.value in user.permissions:
            return []  # Empty list means all regions
        
        return self.user_regions.get(str(user.user_id), [])
    
    async def get_user_factions(self, user: User) -> List[UUID]:
        """Get factions user has access to"""
        if Permission.ADMIN.value in user.permissions:
            return []  # Empty list means all factions
        
        return self.user_factions.get(str(user.user_id), [])
    
    async def can_access_region(self, user: User, region_id: str) -> bool:
        """Check if user can access specific region"""
        if Permission.ADMIN.value in user.permissions:
            return True
        
        user_regions = await self.get_user_regions(user)
        return not user_regions or region_id in user_regions
    
    async def can_access_faction(self, user: User, faction_id: UUID) -> bool:
        """Check if user can access specific faction"""
        if Permission.ADMIN.value in user.permissions:
            return True
        
        user_factions = await self.get_user_factions(user)
        return not user_factions or faction_id in user_factions


class AuthenticatedWorldStateService:
    """World state service wrapper with authentication"""
    
    def __init__(self, world_state_service: WorldStateService, auth_manager: AuthManagerProtocol):
        self.world_state_service = world_state_service
        self.auth_manager = auth_manager
    
    async def _check_permission(self, user: Optional[User], permission: Permission) -> bool:
        """Check if user has required permission"""
        if not user:
            return False
        return await self.auth_manager.check_permission(user, permission.value)
    
    async def _check_region_access(self, user: Optional[User], region_id: Optional[str]) -> bool:
        """Check if user can access region"""
        if not user:
            return False
        
        if not region_id:
            return True  # No region restriction
        
        return await self.auth_manager.can_access_region(user, region_id)
    
    async def _audit_log(self, user: Optional[User], action: str, **kwargs):
        """Log user actions for audit purposes"""
        log_data = {
            'user_id': str(user.user_id) if user else None,
            'username': user.username if user else None,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(f"AUDIT: {log_data}")
    
    # ===== AUTHENTICATED READ OPERATIONS =====
    
    async def get_state_variable(
        self,
        key: str,
        region_id: Optional[str] = None,
        default: Any = None,
        user: Optional[User] = None
    ) -> Any:
        """Get state variable with authentication"""
        if not await self._check_permission(user, Permission.READ):
            raise PermissionError("User does not have read permission")
        
        if not await self._check_region_access(user, region_id):
            raise PermissionError(f"User cannot access region {region_id}")
        
        await self._audit_log(user, "get_state_variable", key=key, region_id=region_id)
        
        return await self.world_state_service.get_state_variable(key, region_id, default)
    
    async def query_state(
        self,
        category: Optional[StateCategory] = None,
        region_id: Optional[str] = None,
        key_pattern: Optional[str] = None,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Query state with authentication"""
        if not await self._check_permission(user, Permission.READ):
            raise PermissionError("User does not have read permission")
        
        if not await self._check_region_access(user, region_id):
            raise PermissionError(f"User cannot access region {region_id}")
        
        await self._audit_log(user, "query_state", category=category, region_id=region_id, pattern=key_pattern)
        
        return await self.world_state_service.query_state(category, region_id, key_pattern)
    
    async def get_system_status(self, user: Optional[User] = None) -> Dict[str, Any]:
        """Get system status with authentication"""
        if not await self._check_permission(user, Permission.READ):
            raise PermissionError("User does not have read permission")
        
        await self._audit_log(user, "get_system_status")
        
        status = await self.world_state_service.get_system_status()
        
        # Filter sensitive information for non-admin users
        if not await self._check_permission(user, Permission.ADMIN):
            # Remove sensitive fields for non-admin users
            filtered_status = {k: v for k, v in status.items() 
                             if k not in ['repository_info', 'internal_stats']}
            return filtered_status
        
        return status
    
    # ===== AUTHENTICATED WRITE OPERATIONS =====
    
    async def set_state_variable(
        self,
        key: str,
        value: Any,
        region_id: Optional[str] = None,
        category: StateCategory = StateCategory.GENERAL,
        reason: str = "State update",
        user: Optional[User] = None
    ) -> bool:
        """Set state variable with authentication"""
        if not await self._check_permission(user, Permission.WRITE):
            raise PermissionError("User does not have write permission")
        
        if not await self._check_region_access(user, region_id):
            raise PermissionError(f"User cannot access region {region_id}")
        
        # Add user ID to reason for audit trail
        full_reason = f"{reason} (by {user.username if user else 'system'})"
        
        await self._audit_log(user, "set_state_variable", 
                            key=key, value=value, region_id=region_id, category=category.value)
        
        return await self.world_state_service.set_state_variable(
            key, value, region_id, category, full_reason, str(user.user_id) if user else None
        )
    
    async def record_world_event(
        self,
        event_type: str,
        description: str,
        affected_regions: Optional[List[str]] = None,
        category: StateCategory = StateCategory.GENERAL,
        metadata: Optional[Dict[str, Any]] = None,
        user: Optional[User] = None
    ) -> str:
        """Record world event with authentication"""
        if not await self._check_permission(user, Permission.WRITE):
            raise PermissionError("User does not have write permission")
        
        # Check access to all affected regions
        if affected_regions:
            for region_id in affected_regions:
                if not await self._check_region_access(user, region_id):
                    raise PermissionError(f"User cannot access region {region_id}")
        
        # Add user context to metadata
        enhanced_metadata = metadata or {}
        enhanced_metadata.update({
            'recorded_by_user': str(user.user_id) if user else None,
            'recorded_by_username': user.username if user else None
        })
        
        await self._audit_log(user, "record_world_event", 
                            event_type=event_type, affected_regions=affected_regions)
        
        return await self.world_state_service.record_world_event(
            event_type, description, affected_regions, category, enhanced_metadata
        )
    
    # ===== AUTHENTICATED HISTORICAL OPERATIONS =====
    
    async def get_historical_state(
        self,
        timestamp: datetime,
        region_id: Optional[str] = None,
        user: Optional[User] = None
    ) -> Optional[Dict[str, Any]]:
        """Get historical state with authentication"""
        if not await self._check_permission(user, Permission.READ_HISTORICAL):
            raise PermissionError("User does not have historical read permission")
        
        if not await self._check_region_access(user, region_id):
            raise PermissionError(f"User cannot access region {region_id}")
        
        await self._audit_log(user, "get_historical_state", timestamp=timestamp.isoformat(), region_id=region_id)
        
        return await self.world_state_service.get_historical_state(timestamp, region_id)
    
    # ===== AUTHENTICATED ADMINISTRATIVE OPERATIONS =====
    
    async def create_snapshot(
        self,
        region_id: Optional[str] = None,
        reason: str = "Manual snapshot",
        user: Optional[User] = None
    ) -> Optional[str]:
        """Create snapshot with authentication"""
        if not await self._check_permission(user, Permission.ADMIN):
            raise PermissionError("User does not have admin permission")
        
        if region_id and not await self._check_region_access(user, region_id):
            raise PermissionError(f"User cannot access region {region_id}")
        
        full_reason = f"{reason} (by {user.username if user else 'system'})"
        
        await self._audit_log(user, "create_snapshot", region_id=region_id, reason=reason)
        
        return await self.world_state_service.create_snapshot(region_id, full_reason)
    
    async def trigger_summarization(self, user: Optional[User] = None) -> bool:
        """Trigger summarization with authentication"""
        if not await self._check_permission(user, Permission.ADMIN):
            raise PermissionError("User does not have admin permission")
        
        await self._audit_log(user, "trigger_summarization")
        
        return await self.world_state_service.trigger_summarization()
    
    # ===== REGION-SPECIFIC OPERATIONS =====
    
    async def get_user_accessible_regions(self, user: Optional[User] = None) -> List[str]:
        """Get list of regions user can access"""
        if not user:
            return []
        
        if await self._check_permission(user, Permission.ADMIN):
            # Admin can see all regions - get from world state
            status = await self.world_state_service.get_system_status()
            # Extract region list from status (implementation depends on your data structure)
            return list(status.get('regions', {}).keys()) if 'regions' in status else []
        
        return await self.auth_manager.get_user_regions(user)
    
    async def get_filtered_state_for_user(self, user: Optional[User] = None) -> Dict[str, Any]:
        """Get world state filtered for user's permissions"""
        if not await self._check_permission(user, Permission.READ):
            raise PermissionError("User does not have read permission")
        
        # Get full system status
        full_status = await self.world_state_service.get_system_status()
        
        # Filter based on user's region access
        accessible_regions = await self.get_user_accessible_regions(user)
        
        # If user has access to all regions (admin or empty list), return full status
        if not accessible_regions or await self._check_permission(user, Permission.ADMIN):
            return full_status
        
        # Filter regions
        filtered_status = full_status.copy()
        if 'regions' in filtered_status:
            filtered_status['regions'] = {
                region_id: region_data 
                for region_id, region_data in filtered_status['regions'].items()
                if region_id in accessible_regions
            }
        
        await self._audit_log(user, "get_filtered_state", accessible_regions=accessible_regions)
        
        return filtered_status


# ===== AUTHENTICATION DECORATORS =====

def require_permission(permission: Permission):
    """Decorator to require specific permission for a method"""
    def decorator(func):
        async def wrapper(self, *args, user: Optional[User] = None, **kwargs):
            if not user:
                raise PermissionError("Authentication required")
            
            if not await self.auth_manager.check_permission(user, permission.value):
                raise PermissionError(f"Permission {permission.value} required")
            
            return await func(self, *args, user=user, **kwargs)
        return wrapper
    return decorator


def require_region_access(region_param: str = 'region_id'):
    """Decorator to require access to specific region"""
    def decorator(func):
        async def wrapper(self, *args, user: Optional[User] = None, **kwargs):
            region_id = kwargs.get(region_param)
            
            if region_id and not await self.auth_manager.can_access_region(user, region_id):
                raise PermissionError(f"Access denied to region {region_id}")
            
            return await func(self, *args, user=user, **kwargs)
        return wrapper
    return decorator


# ===== FACTORY FUNCTIONS =====

async def create_authenticated_world_state_service(
    world_state_service: WorldStateService,
    auth_manager: Optional[AuthManagerProtocol] = None
) -> AuthenticatedWorldStateService:
    """Factory to create authenticated world state service"""
    if not auth_manager:
        auth_manager = WorldStateAuthManager()
    
    return AuthenticatedWorldStateService(world_state_service, auth_manager) 