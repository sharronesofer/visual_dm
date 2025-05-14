/**
 * Party Manager
 * 
 * Manages party lifecycle, state transitions, and member interactions.
 * Provides methods for creating, updating, and managing parties.
 */

import { EventEmitter } from 'events';
import {
  Party,
  PartyMember,
  PartyRole,
  PartyStatus,
  PartyInvitation,
  InvitationStatus,
  ResourceSharingPolicy,
  PartyBonus,
  PartyAction
} from './types';
import { UUID } from '../../core/types';

// Party-related events
export enum PartyEvents {
  PARTY_CREATED = 'party:created',
  PARTY_UPDATED = 'party:updated',
  PARTY_DISBANDED = 'party:disbanded',
  MEMBER_JOINED = 'party:member_joined',
  MEMBER_LEFT = 'party:member_left',
  ROLE_CHANGED = 'party:role_changed',
  LEADERSHIP_TRANSFERRED = 'party:leadership_transferred',
  INVITATION_SENT = 'party:invitation_sent',
  INVITATION_ACCEPTED = 'party:invitation_accepted',
  INVITATION_DECLINED = 'party:invitation_declined',
  MEMBER_KICKED = 'party:member_kicked',
  QUEST_ADDED = 'party:quest_added',
  QUEST_COMPLETED = 'party:quest_completed',
  RESOURCE_SHARED = 'party:resource_shared',
  PARTY_ACTION_USED = 'party:action_used'
}

/**
 * Party Manager class
 */
export class PartyManager {
  private static instance: PartyManager;
  private parties: Map<UUID, Party> = new Map();
  private invitations: Map<UUID, PartyInvitation> = new Map();
  private entityParties: Map<UUID, Set<UUID>> = new Map(); // Map of entity ID to party IDs they belong to
  private activePartyActions: Map<UUID, Map<UUID, PartyAction>> = new Map(); // Map of party ID to actions
  private eventEmitter: EventEmitter = new EventEmitter();
  
  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    // Initialize event listeners
    this.setupEventListeners();
  }
  
  /**
   * Get the singleton instance
   */
  public static getInstance(): PartyManager {
    if (!PartyManager.instance) {
      PartyManager.instance = new PartyManager();
    }
    return PartyManager.instance;
  }
  
  /**
   * Set up event listeners
   */
  private setupEventListeners(): void {
    // Add any internal event listeners here
    this.eventEmitter.on(PartyEvents.INVITATION_ACCEPTED, (invitation: PartyInvitation) => {
      this.addMemberFromInvitation(invitation);
    });
  }
  
  /**
   * Create a new party
   */
  public createParty(
    name: string,
    leaderId: UUID,
    description?: string,
    isPublic: boolean = false,
    maxSize: number = 4
  ): Party {
    const id = crypto.randomUUID() as UUID;
    const now = Date.now();
    
    // Create initial party leader as first member
    const leader: PartyMember = {
      entityId: leaderId,
      role: PartyRole.LEADER,
      joinedAt: now,
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['invite', 'kick', 'promote', 'disband', 'assign_quest']
    };
    
    const newParty: Party = {
      id,
      name,
      description,
      status: PartyStatus.FORMING,
      leaderId,
      members: [leader],
      createdAt: now,
      updatedAt: now,
      activeQuestIds: [],
      completedQuestIds: [],
      tags: [],
      resourceSharingPolicy: ResourceSharingPolicy.EQUAL,
      partyBonuses: [],
      maxSize,
      isPublic,
      settings: {}
    };
    
    this.parties.set(id, newParty);
    
    // Add to entity-party mapping
    if (!this.entityParties.has(leaderId)) {
      this.entityParties.set(leaderId, new Set());
    }
    this.entityParties.get(leaderId)!.add(id);
    
    this.eventEmitter.emit(PartyEvents.PARTY_CREATED, newParty);
    return newParty;
  }
  
  /**
   * Get a party by ID
   */
  public getParty(partyId: UUID): Party | undefined {
    return this.parties.get(partyId);
  }
  
  /**
   * Get all parties
   */
  public getAllParties(): Party[] {
    return Array.from(this.parties.values());
  }
  
  /**
   * Get parties by status
   */
  public getPartiesByStatus(status: PartyStatus): Party[] {
    return Array.from(this.parties.values()).filter(party => party.status === status);
  }
  
  /**
   * Get parties by member
   */
  public getPartiesByMember(entityId: UUID): Party[] {
    const partyIds = this.entityParties.get(entityId) || new Set();
    return Array.from(partyIds).map(id => this.parties.get(id)!).filter(Boolean);
  }
  
  /**
   * Get active parties for a member
   */
  public getActivePartiesForMember(entityId: UUID): Party[] {
    return this.getPartiesByMember(entityId)
      .filter(party => party.status === PartyStatus.ACTIVE || party.status === PartyStatus.ON_MISSION);
  }
  
  /**
   * Send a party invitation
   */
  public sendInvitation(
    partyId: UUID,
    fromEntityId: UUID,
    toEntityId: UUID,
    message?: string,
    expiresInMs: number = 86400000 // 24 hours by default
  ): PartyInvitation | null {
    // Verify party exists
    const party = this.parties.get(partyId);
    if (!party) return null;
    
    // Verify sender is in party with invite permissions
    const sender = party.members.find(member => member.entityId === fromEntityId);
    if (!sender || !sender.permissions.includes('invite')) return null;
    
    // Verify target is not already in party
    if (party.members.some(member => member.entityId === toEntityId)) return null;
    
    // Check if an active invitation already exists
    const existingInvitation = Array.from(this.invitations.values()).find(inv => 
      inv.partyId === partyId && 
      inv.toEntityId === toEntityId && 
      inv.status === InvitationStatus.PENDING
    );
    
    if (existingInvitation) return existingInvitation;
    
    // Create new invitation
    const id = crypto.randomUUID() as UUID;
    const now = Date.now();
    
    const invitation: PartyInvitation = {
      id,
      partyId,
      fromEntityId,
      toEntityId,
      status: InvitationStatus.PENDING,
      message,
      createdAt: now,
      expiresAt: now + expiresInMs
    };
    
    this.invitations.set(id, invitation);
    this.eventEmitter.emit(PartyEvents.INVITATION_SENT, invitation);
    
    return invitation;
  }
  
  /**
   * Respond to a party invitation
   */
  public respondToInvitation(
    invitationId: UUID,
    isAccepted: boolean
  ): boolean {
    const invitation = this.invitations.get(invitationId);
    if (!invitation || invitation.status !== InvitationStatus.PENDING) return false;
    
    const now = Date.now();
    
    // Check if invitation has expired
    if (invitation.expiresAt && invitation.expiresAt < now) {
      invitation.status = InvitationStatus.EXPIRED;
      this.invitations.set(invitationId, invitation);
      return false;
    }
    
    // Update invitation status
    invitation.status = isAccepted ? InvitationStatus.ACCEPTED : InvitationStatus.DECLINED;
    invitation.responseAt = now;
    this.invitations.set(invitationId, invitation);
    
    if (isAccepted) {
      this.eventEmitter.emit(PartyEvents.INVITATION_ACCEPTED, invitation);
    } else {
      this.eventEmitter.emit(PartyEvents.INVITATION_DECLINED, invitation);
    }
    
    return true;
  }
  
  /**
   * Add a member to a party based on an accepted invitation
   */
  private addMemberFromInvitation(invitation: PartyInvitation): boolean {
    if (invitation.status !== InvitationStatus.ACCEPTED) return false;
    
    const party = this.parties.get(invitation.partyId);
    if (!party) return false;
    
    // Check if already a member
    if (party.members.some(member => member.entityId === invitation.toEntityId)) return false;
    
    // Check if party is full
    if (party.members.length >= party.maxSize) return false;
    
    // Create new member
    const newMember: PartyMember = {
      entityId: invitation.toEntityId,
      role: PartyRole.MEMBER,
      joinedAt: Date.now(),
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['leave']
    };
    
    // Add member to party
    party.members.push(newMember);
    party.updatedAt = Date.now();
    
    // Update party status if needed
    if (party.status === PartyStatus.FORMING && party.members.length > 1) {
      party.status = PartyStatus.ACTIVE;
    }
    
    this.parties.set(party.id, party);
    
    // Add to entity-party mapping
    if (!this.entityParties.has(invitation.toEntityId)) {
      this.entityParties.set(invitation.toEntityId, new Set());
    }
    this.entityParties.get(invitation.toEntityId)!.add(party.id);
    
    this.eventEmitter.emit(PartyEvents.MEMBER_JOINED, party, newMember);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Add member directly to a party (bypassing invitation)
   */
  public addMember(
    partyId: UUID,
    entityId: UUID,
    role: PartyRole = PartyRole.MEMBER
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Check if already a member
    if (party.members.some(member => member.entityId === entityId)) return false;
    
    // Check if party is full
    if (party.members.length >= party.maxSize) return false;
    
    // Create new member
    const newMember: PartyMember = {
      entityId,
      role: role === PartyRole.LEADER ? PartyRole.MEMBER : role, // Can't add directly as leader
      joinedAt: Date.now(),
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['leave']
    };
    
    // Add member to party
    party.members.push(newMember);
    party.updatedAt = Date.now();
    
    // Update party status if needed
    if (party.status === PartyStatus.FORMING && party.members.length > 1) {
      party.status = PartyStatus.ACTIVE;
    }
    
    this.parties.set(party.id, party);
    
    // Add to entity-party mapping
    if (!this.entityParties.has(entityId)) {
      this.entityParties.set(entityId, new Set());
    }
    this.entityParties.get(entityId)!.add(party.id);
    
    this.eventEmitter.emit(PartyEvents.MEMBER_JOINED, party, newMember);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Remove a member from a party
   */
  public removeMember(
    partyId: UUID,
    entityId: UUID,
    isKicked: boolean = false
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Check if member exists
    const memberIndex = party.members.findIndex(member => member.entityId === entityId);
    if (memberIndex === -1) return false;
    
    // Check if member is the leader
    if (party.leaderId === entityId) {
      // Can't remove the leader without transferring leadership first
      return false;
    }
    
    // Remove the member
    const removedMember = party.members[memberIndex];
    party.members.splice(memberIndex, 1);
    party.updatedAt = Date.now();
    
    // Update party status if needed
    if (party.members.length === 1) {
      party.status = PartyStatus.FORMING;
    } else if (party.members.length === 0) {
      party.status = PartyStatus.DISBANDED;
    }
    
    this.parties.set(party.id, party);
    
    // Remove from entity-party mapping
    const entityParties = this.entityParties.get(entityId);
    if (entityParties) {
      entityParties.delete(party.id);
      if (entityParties.size === 0) {
        this.entityParties.delete(entityId);
      }
    }
    
    if (isKicked) {
      this.eventEmitter.emit(PartyEvents.MEMBER_KICKED, party, removedMember);
    } else {
      this.eventEmitter.emit(PartyEvents.MEMBER_LEFT, party, removedMember);
    }
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Transfer party leadership
   */
  public transferLeadership(
    partyId: UUID,
    currentLeaderId: UUID,
    newLeaderId: UUID
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Verify current leader
    if (party.leaderId !== currentLeaderId) return false;
    
    // Verify new leader is a member
    const newLeader = party.members.find(member => member.entityId === newLeaderId);
    if (!newLeader) return false;
    
    // Update the leaders
    const currentLeader = party.members.find(member => member.entityId === currentLeaderId)!;
    
    // Swap roles and permissions
    currentLeader.role = PartyRole.MEMBER;
    currentLeader.permissions = ['leave', 'invite'];
    
    newLeader.role = PartyRole.LEADER;
    newLeader.permissions = ['invite', 'kick', 'promote', 'disband', 'assign_quest'];
    
    // Update party
    party.leaderId = newLeaderId;
    party.updatedAt = Date.now();
    
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.LEADERSHIP_TRANSFERRED, party, currentLeaderId, newLeaderId);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Change member role
   */
  public changeMemberRole(
    partyId: UUID,
    changerId: UUID,
    targetId: UUID,
    newRole: PartyRole
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Only the leader can change roles
    if (party.leaderId !== changerId) return false;
    
    // Can't change leader's role
    if (targetId === party.leaderId) return false;
    
    // Can't change to leader
    if (newRole === PartyRole.LEADER) return false;
    
    // Find target member
    const member = party.members.find(member => member.entityId === targetId);
    if (!member) return false;
    
    // Update member role
    const oldRole = member.role;
    member.role = newRole;
    
    // Update permissions based on role
    switch (newRole) {
      case PartyRole.ADVISER:
        member.permissions = ['leave', 'invite', 'suggest_quest'];
        break;
      case PartyRole.GUEST:
        member.permissions = ['leave'];
        break;
      case PartyRole.FOLLOWER:
        member.permissions = ['leave', 'suggest_quest'];
        break;
      case PartyRole.MEMBER:
      default:
        member.permissions = ['leave', 'invite'];
        break;
    }
    
    party.updatedAt = Date.now();
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.ROLE_CHANGED, party, targetId, oldRole, newRole);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Add a quest to a party
   */
  public addQuestToParty(
    partyId: UUID,
    questId: UUID,
    assignerId: UUID
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Verify assigner has permission to assign quests
    const assigner = party.members.find(member => member.entityId === assignerId);
    if (!assigner || !assigner.permissions.includes('assign_quest')) return false;
    
    // Check if quest is already active
    if (party.activeQuestIds.includes(questId)) return false;
    
    // Add quest to active quests
    party.activeQuestIds.push(questId);
    party.updatedAt = Date.now();
    
    // Update party status if needed
    if (party.status === PartyStatus.ACTIVE) {
      party.status = PartyStatus.ON_MISSION;
    }
    
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.QUEST_ADDED, party, questId);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Complete a quest for a party
   */
  public completeQuestForParty(
    partyId: UUID,
    questId: UUID
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Check if quest is active
    const questIndex = party.activeQuestIds.indexOf(questId);
    if (questIndex === -1) return false;
    
    // Remove from active quests and add to completed quests
    party.activeQuestIds.splice(questIndex, 1);
    party.completedQuestIds.push(questId);
    party.updatedAt = Date.now();
    
    // Update party status if needed
    if (party.status === PartyStatus.ON_MISSION && party.activeQuestIds.length === 0) {
      party.status = PartyStatus.ACTIVE;
    }
    
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.QUEST_COMPLETED, party, questId);
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Disband a party
   */
  public disbandParty(
    partyId: UUID,
    leaderId: UUID
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Only the leader can disband the party
    if (party.leaderId !== leaderId) return false;
    
    // Update party status
    party.status = PartyStatus.DISBANDED;
    party.updatedAt = Date.now();
    
    this.parties.set(party.id, party);
    
    // Remove from all entity-party mappings
    party.members.forEach(member => {
      const entityParties = this.entityParties.get(member.entityId);
      if (entityParties) {
        entityParties.delete(party.id);
        if (entityParties.size === 0) {
          this.entityParties.delete(member.entityId);
        }
      }
    });
    
    this.eventEmitter.emit(PartyEvents.PARTY_DISBANDED, party);
    
    return true;
  }
  
  /**
   * Register a party action
   */
  public registerPartyAction(
    partyId: UUID,
    action: Omit<PartyAction, 'id'>
  ): PartyAction | null {
    const party = this.parties.get(partyId);
    if (!party) return null;
    
    const id = crypto.randomUUID() as UUID;
    
    const newAction: PartyAction = {
      ...action,
      id
    };
    
    // Initialize party actions map if needed
    if (!this.activePartyActions.has(partyId)) {
      this.activePartyActions.set(partyId, new Map());
    }
    
    this.activePartyActions.get(partyId)!.set(id, newAction);
    
    return newAction;
  }
  
  /**
   * Get available party actions
   */
  public getAvailablePartyActions(partyId: UUID): PartyAction[] {
    const party = this.parties.get(partyId);
    if (!party) return [];
    
    const partyActions = this.activePartyActions.get(partyId);
    if (!partyActions) return [];
    
    const now = Date.now();
    
    // Filter to actions that are available (not on cooldown and requirements met)
    return Array.from(partyActions.values()).filter(action => {
      // Check cooldown
      if (action.lastUsed && now < action.lastUsed + action.cooldown) {
        return false;
      }
      
      // Check member count
      if (party.members.length < action.minMembers) {
        return false;
      }
      
      // Check required roles
      if (action.requiredRoles.length > 0) {
        const roles = party.members.map(member => member.role);
        const hasAllRoles = action.requiredRoles.every(role => roles.includes(role));
        if (!hasAllRoles) return false;
      }
      
      // Check required abilities
      if (action.requiredAbilities.length > 0) {
        const abilities = party.members.flatMap(member => member.abilities);
        const hasAllAbilities = action.requiredAbilities.every(ability => 
          abilities.includes(ability)
        );
        if (!hasAllAbilities) return false;
      }
      
      return true;
    });
  }
  
  /**
   * Use a party action
   */
  public usePartyAction(
    partyId: UUID,
    actionId: UUID,
    initiatorId: UUID
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Check if initiator is a member
    const initiator = party.members.find(member => member.entityId === initiatorId);
    if (!initiator) return false;
    
    // Get the action
    const partyActions = this.activePartyActions.get(partyId);
    if (!partyActions) return false;
    
    const action = partyActions.get(actionId);
    if (!action) return false;
    
    // Check if action is available
    const availableActions = this.getAvailablePartyActions(partyId);
    if (!availableActions.some(a => a.id === actionId)) return false;
    
    // Update last used timestamp
    action.lastUsed = Date.now();
    partyActions.set(actionId, action);
    
    this.eventEmitter.emit(PartyEvents.PARTY_ACTION_USED, party, action, initiatorId);
    
    return true;
  }
  
  /**
   * Calculate and apply party bonuses
   */
  public recalculatePartyBonuses(partyId: UUID): PartyBonus[] {
    const party = this.parties.get(partyId);
    if (!party) return [];
    
    // Reset active status for all bonuses
    party.partyBonuses.forEach(bonus => bonus.isActive = false);
    
    // Check each bonus condition
    party.partyBonuses.forEach(bonus => {
      // All conditions must be met for the bonus to be active
      bonus.isActive = bonus.conditions.every(condition => {
        switch (condition.type) {
          case 'role_count': {
            const [role, count] = condition.value as [PartyRole, number];
            const roleCount = party.members.filter(member => member.role === role).length;
            return this.evaluateCondition(roleCount, count, condition.operator);
          }
          case 'ability_present': {
            const ability = condition.value as string;
            const hasAbility = party.members.some(member => 
              member.abilities.includes(ability)
            );
            return hasAbility;
          }
          case 'member_count': {
            return this.evaluateCondition(
              party.members.length,
              condition.value as number,
              condition.operator
            );
          }
          default:
            return false;
        }
      });
    });
    
    // Return the active bonuses
    const activeBonuses = party.partyBonuses.filter(bonus => bonus.isActive);
    
    this.parties.set(party.id, party);
    
    return activeBonuses;
  }
  
  /**
   * Evaluate a condition
   */
  private evaluateCondition(
    left: number,
    right: number,
    operator: string
  ): boolean {
    switch (operator) {
      case '==': return left === right;
      case '>=': return left >= right;
      case '<=': return left <= right;
      case '>': return left > right;
      case '<': return left < right;
      default: return false;
    }
  }
  
  /**
   * Add a bonus to a party
   */
  public addPartyBonus(
    partyId: UUID,
    bonus: Omit<PartyBonus, 'id' | 'isActive'>
  ): PartyBonus | null {
    const party = this.parties.get(partyId);
    if (!party) return null;
    
    const id = crypto.randomUUID() as UUID;
    
    const newBonus: PartyBonus = {
      ...bonus,
      id,
      isActive: false
    };
    
    party.partyBonuses.push(newBonus);
    party.updatedAt = Date.now();
    
    this.parties.set(party.id, party);
    
    // Recalculate bonuses to see if this one should be active
    this.recalculatePartyBonuses(partyId);
    
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return newBonus;
  }
  
  /**
   * Update party settings
   */
  public updatePartySettings(
    partyId: UUID,
    updaterId: UUID,
    settings: Record<string, any>
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Only the leader can update party settings
    if (party.leaderId !== updaterId) return false;
    
    party.settings = {
      ...party.settings,
      ...settings
    };
    party.updatedAt = Date.now();
    
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Set resource sharing policy
   */
  public setResourceSharingPolicy(
    partyId: UUID,
    updaterId: UUID,
    policy: ResourceSharingPolicy
  ): boolean {
    const party = this.parties.get(partyId);
    if (!party) return false;
    
    // Only the leader can update resource sharing policy
    if (party.leaderId !== updaterId) return false;
    
    party.resourceSharingPolicy = policy;
    party.updatedAt = Date.now();
    
    this.parties.set(party.id, party);
    
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party);
    
    return true;
  }
  
  /**
   * Subscribe to party events
   */
  public on(event: PartyEvents, listener: (...args: any[]) => void): void {
    this.eventEmitter.on(event, listener);
  }
  
  /**
   * Unsubscribe from party events
   */
  public off(event: PartyEvents, listener: (...args: any[]) => void): void {
    this.eventEmitter.off(event, listener);
  }
} 