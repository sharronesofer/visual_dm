from typing import Any, Dict, List, Union
from enum import Enum



/**
 * Party Management System Types
 * 
 * This file defines the core types used throughout the party management system.
 */
/**
 * Party member role enum
 */
class PartyRole(Enum):
    LEADER = 'leader'
    MEMBER = 'member'
    ADVISER = 'adviser'
    GUEST = 'guest'
    FOLLOWER = 'follower'
/**
 * Party invitation status enum
 */
class InvitationStatus(Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
/**
 * Party status enum
 */
class PartyStatus(Enum):
    FORMING = 'forming'
    ACTIVE = 'active'
    DISBANDED = 'disbanded'
    INACTIVE = 'inactive'
    ON_MISSION = 'on_mission'
/**
 * Resource sharing policy enum
 */
class ResourceSharingPolicy(Enum):
    EQUAL = 'equal'
    PROPORTIONAL = 'proportional'
    LEADER_DECIDES = 'leader_decides'
    NONE = 'none'
/**
 * Party invitation interface
 */
class PartyInvitation:
    id: UUID
    partyId: UUID
    fromEntityId: UUID
    toEntityId: UUID
    status: \'InvitationStatus\'
    message?: str
    createdAt: float
    expiresAt?: float
    responseAt?: float
/**
 * Party member interface
 */
class PartyMember:
    entityId: UUID
    role: \'PartyRole\'
    joinedAt: float
    contributionScore: float
    isActive: bool
    abilities: List[str]
    permissions: List[str]
    settings?: Dict[str, Any>
/**
 * Party interface
 */
class Party:
    id: UUID
    name: str
    description?: str
    status: \'PartyStatus\'
    leaderId: UUID
    members: List[PartyMember]
    createdAt: float
    updatedAt: float
    activeQuestIds: List[UUID]
    completedQuestIds: List[UUID]
    tags: List[str]
    resourceSharingPolicy: \'ResourceSharingPolicy\'
    partyBonuses: List[PartyBonus]
    maxSize: float
    isPublic: bool
    settings?: Dict[str, Any>
/**
 * Party bonus interface - represents benefits from having certain party compositions
 */
class PartyBonus:
    id: UUID
    name: str
    description: str
    statModifiers: List[StatModifier]
    conditions: List[PartyBonusCondition]
    isActive: bool
/**
 * Stat modifier interface - used for party bonuses
 */
class StatModifier:
    stat: str
    value: float
    type: Union['flat', 'percentage']
/**
 * Party bonus condition interface - determines when a bonus is active
 */
class PartyBonusCondition:
    type: Union['role_count', 'ability_present', 'member_count', 'custom']
    value: Any
    operator: Union['==', '>=', '<=', '>', '<']
/**
 * Party action interface - represents a coordinated action the party can take
 */
class PartyAction:
    id: UUID
    name: str
    description: str
    requiredRoles: List[PartyRole]
    requiredAbilities: List[str]
    minMembers: float
    cooldown: float
    lastUsed?: float
    effects: List[str] 