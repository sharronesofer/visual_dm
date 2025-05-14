from typing import Any, List
from enum import Enum


/**
 * Party Manager
 * 
 * Manages party lifecycle, state transitions, and member interactions.
 * Provides methods for creating, updating, and managing parties.
 */
  Party,
  PartyMember,
  PartyRole,
  PartyStatus,
  PartyInvitation,
  InvitationStatus,
  ResourceSharingPolicy,
  PartyBonus,
  PartyAction
} from './types'
class PartyEvents(Enum):
    PARTY_CREATED = 'party:created'
    PARTY_UPDATED = 'party:updated'
    PARTY_DISBANDED = 'party:disbanded'
    MEMBER_JOINED = 'party:member_joined'
    MEMBER_LEFT = 'party:member_left'
    ROLE_CHANGED = 'party:role_changed'
    LEADERSHIP_TRANSFERRED = 'party:leadership_transferred'
    INVITATION_SENT = 'party:invitation_sent'
    INVITATION_ACCEPTED = 'party:invitation_accepted'
    INVITATION_DECLINED = 'party:invitation_declined'
    MEMBER_KICKED = 'party:member_kicked'
    QUEST_ADDED = 'party:quest_added'
    QUEST_COMPLETED = 'party:quest_completed'
    RESOURCE_SHARED = 'party:resource_shared'
    PARTY_ACTION_USED = 'party:action_used'
/**
 * Party Manager class
 */
class PartyManager {
  private static instance: \'PartyManager\'
  private parties: Map<UUID, Party> = new Map()
  private invitations: Map<UUID, PartyInvitation> = new Map()
  private entityParties: Map<UUID, Set<UUID>> = new Map() 
  private activePartyActions: Map<UUID, Map<UUID, PartyAction>> = new Map() 
  private eventEmitter: EventEmitter = new EventEmitter()
  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.setupEventListeners()
  }
  /**
   * Get the singleton instance
   */
  public static getInstance(): \'PartyManager\' {
    if (!PartyManager.instance) {
      PartyManager.instance = new PartyManager()
    }
    return PartyManager.instance
  }
  /**
   * Set up event listeners
   */
  private setupEventListeners(): void {
    this.eventEmitter.on(PartyEvents.INVITATION_ACCEPTED, (invitation: PartyInvitation) => {
      this.addMemberFromInvitation(invitation)
    })
  }
  /**
   * Create a new party
   */
  public createParty(
    name: str,
    leaderId: UUID,
    description?: str,
    isPublic: bool = false,
    maxSize: float = 4
  ): Party {
    const id = crypto.randomUUID() as UUID
    const now = Date.now()
    const leader: PartyMember = {
      entityId: leaderId,
      role: PartyRole.LEADER,
      joinedAt: now,
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['invite', 'kick', 'promote', 'disband', 'assign_quest']
    }
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
    }
    this.parties.set(id, newParty)
    if (!this.entityParties.has(leaderId)) {
      this.entityParties.set(leaderId, new Set())
    }
    this.entityParties.get(leaderId)!.add(id)
    this.eventEmitter.emit(PartyEvents.PARTY_CREATED, newParty)
    return newParty
  }
  /**
   * Get a party by ID
   */
  public getParty(partyId: UUID): Party | undefined {
    return this.parties.get(partyId)
  }
  /**
   * Get all parties
   */
  public getAllParties(): Party[] {
    return Array.from(this.parties.values())
  }
  /**
   * Get parties by status
   */
  public getPartiesByStatus(status: PartyStatus): Party[] {
    return Array.from(this.parties.values()).filter(party => party.status === status)
  }
  /**
   * Get parties by member
   */
  public getPartiesByMember(entityId: UUID): Party[] {
    const partyIds = this.entityParties.get(entityId) || new Set()
    return Array.from(partyIds).map(id => this.parties.get(id)!).filter(Boolean)
  }
  /**
   * Get active parties for a member
   */
  public getActivePartiesForMember(entityId: UUID): Party[] {
    return this.getPartiesByMember(entityId)
      .filter(party => party.status === PartyStatus.ACTIVE || party.status === PartyStatus.ON_MISSION)
  }
  /**
   * Send a party invitation
   */
  public sendInvitation(
    partyId: UUID,
    fromEntityId: UUID,
    toEntityId: UUID,
    message?: str,
    expiresInMs: float = 86400000 
  ): PartyInvitation | null {
    const party = this.parties.get(partyId)
    if (!party) return null
    const sender = party.members.find(member => member.entityId === fromEntityId)
    if (!sender || !sender.permissions.includes('invite')) return null
    if (party.members.some(member => member.entityId === toEntityId)) return null
    const existingInvitation = Array.from(this.invitations.values()).find(inv => 
      inv.partyId === partyId && 
      inv.toEntityId === toEntityId && 
      inv.status === InvitationStatus.PENDING
    )
    if (existingInvitation) return existingInvitation
    const id = crypto.randomUUID() as UUID
    const now = Date.now()
    const invitation: PartyInvitation = {
      id,
      partyId,
      fromEntityId,
      toEntityId,
      status: InvitationStatus.PENDING,
      message,
      createdAt: now,
      expiresAt: now + expiresInMs
    }
    this.invitations.set(id, invitation)
    this.eventEmitter.emit(PartyEvents.INVITATION_SENT, invitation)
    return invitation
  }
  /**
   * Respond to a party invitation
   */
  public respondToInvitation(
    invitationId: UUID,
    isAccepted: bool
  ): bool {
    const invitation = this.invitations.get(invitationId)
    if (!invitation || invitation.status !== InvitationStatus.PENDING) return false
    const now = Date.now()
    if (invitation.expiresAt && invitation.expiresAt < now) {
      invitation.status = InvitationStatus.EXPIRED
      this.invitations.set(invitationId, invitation)
      return false
    }
    invitation.status = isAccepted ? InvitationStatus.ACCEPTED : InvitationStatus.DECLINED
    invitation.responseAt = now
    this.invitations.set(invitationId, invitation)
    if (isAccepted) {
      this.eventEmitter.emit(PartyEvents.INVITATION_ACCEPTED, invitation)
    } else {
      this.eventEmitter.emit(PartyEvents.INVITATION_DECLINED, invitation)
    }
    return true
  }
  /**
   * Add a member to a party based on an accepted invitation
   */
  private addMemberFromInvitation(invitation: PartyInvitation): bool {
    if (invitation.status !== InvitationStatus.ACCEPTED) return false
    const party = this.parties.get(invitation.partyId)
    if (!party) return false
    if (party.members.some(member => member.entityId === invitation.toEntityId)) return false
    if (party.members.length >= party.maxSize) return false
    const newMember: PartyMember = {
      entityId: invitation.toEntityId,
      role: PartyRole.MEMBER,
      joinedAt: Date.now(),
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['leave']
    }
    party.members.push(newMember)
    party.updatedAt = Date.now()
    if (party.status === PartyStatus.FORMING && party.members.length > 1) {
      party.status = PartyStatus.ACTIVE
    }
    this.parties.set(party.id, party)
    if (!this.entityParties.has(invitation.toEntityId)) {
      this.entityParties.set(invitation.toEntityId, new Set())
    }
    this.entityParties.get(invitation.toEntityId)!.add(party.id)
    this.eventEmitter.emit(PartyEvents.MEMBER_JOINED, party, newMember)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Add member directly to a party (bypassing invitation)
   */
  public addMember(
    partyId: UUID,
    entityId: UUID,
    role: PartyRole = PartyRole.MEMBER
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.members.some(member => member.entityId === entityId)) return false
    if (party.members.length >= party.maxSize) return false
    const newMember: PartyMember = {
      entityId,
      role: role === PartyRole.LEADER ? PartyRole.MEMBER : role, 
      joinedAt: Date.now(),
      contributionScore: 0,
      isActive: true,
      abilities: [],
      permissions: ['leave']
    }
    party.members.push(newMember)
    party.updatedAt = Date.now()
    if (party.status === PartyStatus.FORMING && party.members.length > 1) {
      party.status = PartyStatus.ACTIVE
    }
    this.parties.set(party.id, party)
    if (!this.entityParties.has(entityId)) {
      this.entityParties.set(entityId, new Set())
    }
    this.entityParties.get(entityId)!.add(party.id)
    this.eventEmitter.emit(PartyEvents.MEMBER_JOINED, party, newMember)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Remove a member from a party
   */
  public removeMember(
    partyId: UUID,
    entityId: UUID,
    isKicked: bool = false
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    const memberIndex = party.members.findIndex(member => member.entityId === entityId)
    if (memberIndex === -1) return false
    if (party.leaderId === entityId) {
      return false
    }
    const removedMember = party.members[memberIndex]
    party.members.splice(memberIndex, 1)
    party.updatedAt = Date.now()
    if (party.members.length === 1) {
      party.status = PartyStatus.FORMING
    } else if (party.members.length === 0) {
      party.status = PartyStatus.DISBANDED
    }
    this.parties.set(party.id, party)
    const entityParties = this.entityParties.get(entityId)
    if (entityParties) {
      entityParties.delete(party.id)
      if (entityParties.size === 0) {
        this.entityParties.delete(entityId)
      }
    }
    if (isKicked) {
      this.eventEmitter.emit(PartyEvents.MEMBER_KICKED, party, removedMember)
    } else {
      this.eventEmitter.emit(PartyEvents.MEMBER_LEFT, party, removedMember)
    }
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Transfer party leadership
   */
  public transferLeadership(
    partyId: UUID,
    currentLeaderId: UUID,
    newLeaderId: UUID
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.leaderId !== currentLeaderId) return false
    const newLeader = party.members.find(member => member.entityId === newLeaderId)
    if (!newLeader) return false
    const currentLeader = party.members.find(member => member.entityId === currentLeaderId)!
    currentLeader.role = PartyRole.MEMBER
    currentLeader.permissions = ['leave', 'invite']
    newLeader.role = PartyRole.LEADER
    newLeader.permissions = ['invite', 'kick', 'promote', 'disband', 'assign_quest']
    party.leaderId = newLeaderId
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.LEADERSHIP_TRANSFERRED, party, currentLeaderId, newLeaderId)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Change member role
   */
  public changeMemberRole(
    partyId: UUID,
    changerId: UUID,
    targetId: UUID,
    newRole: PartyRole
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.leaderId !== changerId) return false
    if (targetId === party.leaderId) return false
    if (newRole === PartyRole.LEADER) return false
    const member = party.members.find(member => member.entityId === targetId)
    if (!member) return false
    const oldRole = member.role
    member.role = newRole
    switch (newRole) {
      case PartyRole.ADVISER:
        member.permissions = ['leave', 'invite', 'suggest_quest']
        break
      case PartyRole.GUEST:
        member.permissions = ['leave']
        break
      case PartyRole.FOLLOWER:
        member.permissions = ['leave', 'suggest_quest']
        break
      case PartyRole.MEMBER:
      default:
        member.permissions = ['leave', 'invite']
        break
    }
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.ROLE_CHANGED, party, targetId, oldRole, newRole)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Add a quest to a party
   */
  public addQuestToParty(
    partyId: UUID,
    questId: UUID,
    assignerId: UUID
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    const assigner = party.members.find(member => member.entityId === assignerId)
    if (!assigner || !assigner.permissions.includes('assign_quest')) return false
    if (party.activeQuestIds.includes(questId)) return false
    party.activeQuestIds.push(questId)
    party.updatedAt = Date.now()
    if (party.status === PartyStatus.ACTIVE) {
      party.status = PartyStatus.ON_MISSION
    }
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.QUEST_ADDED, party, questId)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Complete a quest for a party
   */
  public completeQuestForParty(
    partyId: UUID,
    questId: UUID
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    const questIndex = party.activeQuestIds.indexOf(questId)
    if (questIndex === -1) return false
    party.activeQuestIds.splice(questIndex, 1)
    party.completedQuestIds.push(questId)
    party.updatedAt = Date.now()
    if (party.status === PartyStatus.ON_MISSION && party.activeQuestIds.length === 0) {
      party.status = PartyStatus.ACTIVE
    }
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.QUEST_COMPLETED, party, questId)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Disband a party
   */
  public disbandParty(
    partyId: UUID,
    leaderId: UUID
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.leaderId !== leaderId) return false
    party.status = PartyStatus.DISBANDED
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    party.members.forEach(member => {
      const entityParties = this.entityParties.get(member.entityId)
      if (entityParties) {
        entityParties.delete(party.id)
        if (entityParties.size === 0) {
          this.entityParties.delete(member.entityId)
        }
      }
    })
    this.eventEmitter.emit(PartyEvents.PARTY_DISBANDED, party)
    return true
  }
  /**
   * Register a party action
   */
  public registerPartyAction(
    partyId: UUID,
    action: Omit<PartyAction, 'id'>
  ): PartyAction | null {
    const party = this.parties.get(partyId)
    if (!party) return null
    const id = crypto.randomUUID() as UUID
    const newAction: PartyAction = {
      ...action,
      id
    }
    if (!this.activePartyActions.has(partyId)) {
      this.activePartyActions.set(partyId, new Map())
    }
    this.activePartyActions.get(partyId)!.set(id, newAction)
    return newAction
  }
  /**
   * Get available party actions
   */
  public getAvailablePartyActions(partyId: UUID): PartyAction[] {
    const party = this.parties.get(partyId)
    if (!party) return []
    const partyActions = this.activePartyActions.get(partyId)
    if (!partyActions) return []
    const now = Date.now()
    return Array.from(partyActions.values()).filter(action => {
      if (action.lastUsed && now < action.lastUsed + action.cooldown) {
        return false
      }
      if (party.members.length < action.minMembers) {
        return false
      }
      if (action.requiredRoles.length > 0) {
        const roles = party.members.map(member => member.role)
        const hasAllRoles = action.requiredRoles.every(role => roles.includes(role))
        if (!hasAllRoles) return false
      }
      if (action.requiredAbilities.length > 0) {
        const abilities = party.members.flatMap(member => member.abilities)
        const hasAllAbilities = action.requiredAbilities.every(ability => 
          abilities.includes(ability)
        )
        if (!hasAllAbilities) return false
      }
      return true
    })
  }
  /**
   * Use a party action
   */
  public usePartyAction(
    partyId: UUID,
    actionId: UUID,
    initiatorId: UUID
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    const initiator = party.members.find(member => member.entityId === initiatorId)
    if (!initiator) return false
    const partyActions = this.activePartyActions.get(partyId)
    if (!partyActions) return false
    const action = partyActions.get(actionId)
    if (!action) return false
    const availableActions = this.getAvailablePartyActions(partyId)
    if (!availableActions.some(a => a.id === actionId)) return false
    action.lastUsed = Date.now()
    partyActions.set(actionId, action)
    this.eventEmitter.emit(PartyEvents.PARTY_ACTION_USED, party, action, initiatorId)
    return true
  }
  /**
   * Calculate and apply party bonuses
   */
  public recalculatePartyBonuses(partyId: UUID): PartyBonus[] {
    const party = this.parties.get(partyId)
    if (!party) return []
    party.partyBonuses.forEach(bonus => bonus.isActive = false)
    party.partyBonuses.forEach(bonus => {
      bonus.isActive = bonus.conditions.every(condition => {
        switch (condition.type) {
          case 'role_count': {
            const [role, count] = condition.value as [PartyRole, number]
            const roleCount = party.members.filter(member => member.role === role).length
            return this.evaluateCondition(roleCount, count, condition.operator)
          }
          case 'ability_present': {
            const ability = condition.value as string
            const hasAbility = party.members.some(member => 
              member.abilities.includes(ability)
            )
            return hasAbility
          }
          case 'member_count': {
            return this.evaluateCondition(
              party.members.length,
              condition.value as number,
              condition.operator
            )
          }
          default:
            return false
        }
      })
    })
    const activeBonuses = party.partyBonuses.filter(bonus => bonus.isActive)
    this.parties.set(party.id, party)
    return activeBonuses
  }
  /**
   * Evaluate a condition
   */
  private evaluateCondition(
    left: float,
    right: float,
    operator: str
  ): bool {
    switch (operator) {
      case '==': return left === right
      case '>=': return left >= right
      case '<=': return left <= right
      case '>': return left > right
      case '<': return left < right
      default: return false
    }
  }
  /**
   * Add a bonus to a party
   */
  public addPartyBonus(
    partyId: UUID,
    bonus: Omit<PartyBonus, 'id' | 'isActive'>
  ): PartyBonus | null {
    const party = this.parties.get(partyId)
    if (!party) return null
    const id = crypto.randomUUID() as UUID
    const newBonus: PartyBonus = {
      ...bonus,
      id,
      isActive: false
    }
    party.partyBonuses.push(newBonus)
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    this.recalculatePartyBonuses(partyId)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return newBonus
  }
  /**
   * Update party settings
   */
  public updatePartySettings(
    partyId: UUID,
    updaterId: UUID,
    settings: Record<string, any>
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.leaderId !== updaterId) return false
    party.settings = {
      ...party.settings,
      ...settings
    }
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Set resource sharing policy
   */
  public setResourceSharingPolicy(
    partyId: UUID,
    updaterId: UUID,
    policy: ResourceSharingPolicy
  ): bool {
    const party = this.parties.get(partyId)
    if (!party) return false
    if (party.leaderId !== updaterId) return false
    party.resourceSharingPolicy = policy
    party.updatedAt = Date.now()
    this.parties.set(party.id, party)
    this.eventEmitter.emit(PartyEvents.PARTY_UPDATED, party)
    return true
  }
  /**
   * Subscribe to party events
   */
  public on(event: \'PartyEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.on(event, listener)
  }
  /**
   * Unsubscribe from party events
   */
  public off(event: \'PartyEvents\', listener: (...args: List[any]) => void): void {
    this.eventEmitter.off(event, listener)
  }
} 