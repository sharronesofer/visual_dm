/**
 * Party Management System Types
 * 
 * This file defines the core types used throughout the party management system.
 */

import { UUID } from '../../core/types';

/**
 * Party member role enum
 */
export enum PartyRole {
  LEADER = 'leader',
  MEMBER = 'member',
  ADVISER = 'adviser',
  GUEST = 'guest',
  FOLLOWER = 'follower'
}

/**
 * Party invitation status enum
 */
export enum InvitationStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  DECLINED = 'declined',
  EXPIRED = 'expired',
  REVOKED = 'revoked'
}

/**
 * Party status enum
 */
export enum PartyStatus {
  FORMING = 'forming',
  ACTIVE = 'active',
  DISBANDED = 'disbanded',
  INACTIVE = 'inactive',
  ON_MISSION = 'on_mission'
}

/**
 * Resource sharing policy enum
 */
export enum ResourceSharingPolicy {
  EQUAL = 'equal',           // Equal distribution among all members
  PROPORTIONAL = 'proportional', // Based on contribution
  LEADER_DECIDES = 'leader_decides', // Leader allocates
  NONE = 'none'             // No automatic sharing
}

/**
 * Party invitation interface
 */
export interface PartyInvitation {
  id: UUID;
  partyId: UUID;
  fromEntityId: UUID; // Entity sending invitation
  toEntityId: UUID;   // Entity receiving invitation
  status: InvitationStatus;
  message?: string;
  createdAt: number;
  expiresAt?: number;
  responseAt?: number;
}

/**
 * Party member interface
 */
export interface PartyMember {
  entityId: UUID;
  role: PartyRole;
  joinedAt: number;
  contributionScore: number; // For proportional resource distribution
  isActive: boolean;
  abilities: string[]; // Special abilities this member brings to party
  permissions: string[]; // What this member is allowed to do
  settings?: Record<string, any>; // Member-specific settings
}

/**
 * Party interface
 */
export interface Party {
  id: UUID;
  name: string;
  description?: string;
  status: PartyStatus;
  leaderId: UUID;
  members: PartyMember[];
  createdAt: number;
  updatedAt: number;
  activeQuestIds: UUID[];
  completedQuestIds: UUID[];
  tags: string[];
  resourceSharingPolicy: ResourceSharingPolicy;
  partyBonuses: PartyBonus[];
  maxSize: number;
  isPublic: boolean;
  settings?: Record<string, any>; // Party-specific settings
}

/**
 * Party bonus interface - represents benefits from having certain party compositions
 */
export interface PartyBonus {
  id: UUID;
  name: string;
  description: string;
  statModifiers: StatModifier[];
  conditions: PartyBonusCondition[];
  isActive: boolean;
}

/**
 * Stat modifier interface - used for party bonuses
 */
export interface StatModifier {
  stat: string;
  value: number;
  type: 'flat' | 'percentage';
}

/**
 * Party bonus condition interface - determines when a bonus is active
 */
export interface PartyBonusCondition {
  type: 'role_count' | 'ability_present' | 'member_count' | 'custom';
  value: any;
  operator: '==' | '>=' | '<=' | '>' | '<';
}

/**
 * Party action interface - represents a coordinated action the party can take
 */
export interface PartyAction {
  id: UUID;
  name: string;
  description: string;
  requiredRoles: PartyRole[];
  requiredAbilities: string[];
  minMembers: number;
  cooldown: number;
  lastUsed?: number;
  effects: string[];
} 