from typing import Any


/**
 * Party Manager Tests
 */
describe('PartyManager', () => {
  let partyManager: PartyManager
  beforeEach(() => {
    (PartyManager as any).instance = undefined
    partyManager = PartyManager.getInstance()
  })
  describe('Party Creation', () => {
    test('should create a party with required fields', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      expect(party).toBeDefined()
      expect(party.id).toBeDefined()
      expect(party.name).toBe('Test Party')
      expect(party.leaderId).toBe(leaderId)
      expect(party.status).toBe(PartyStatus.FORMING)
      expect(party.members.length).toBe(1)
      expect(party.members[0].entityId).toBe(leaderId)
      expect(party.members[0].role).toBe(PartyRole.LEADER)
    })
    test('should retrieve a party by ID', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const retrievedParty = partyManager.getParty(party.id)
      expect(retrievedParty).toBeDefined()
      expect(retrievedParty!.id).toBe(party.id)
    })
  })
  describe('Party Membership', () => {
    test('should add a member to a party', () => {
      const leaderId = crypto.randomUUID() as UUID
      const memberId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const result = partyManager.addMember(party.id, memberId)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.members.length).toBe(2)
      expect(updatedParty!.members[1].entityId).toBe(memberId)
      expect(updatedParty!.members[1].role).toBe(PartyRole.MEMBER)
      expect(updatedParty!.status).toBe(PartyStatus.ACTIVE) 
    })
    test('should not add a member to a non-existent party', () => {
      const memberId = crypto.randomUUID() as UUID
      const fakePartyId = crypto.randomUUID() as UUID
      const result = partyManager.addMember(fakePartyId, memberId)
      expect(result).toBe(false)
    })
    test('should not add a member if party is full', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Small Party', leaderId, undefined, false, 2)
      const memberId1 = crypto.randomUUID() as UUID
      const result1 = partyManager.addMember(party.id, memberId1)
      expect(result1).toBe(true)
      const memberId2 = crypto.randomUUID() as UUID
      const result2 = partyManager.addMember(party.id, memberId2)
      expect(result2).toBe(false)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.members.length).toBe(2) 
    })
    test('should remove a member from a party', () => {
      const leaderId = crypto.randomUUID() as UUID
      const memberId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      partyManager.addMember(party.id, memberId)
      const result = partyManager.removeMember(party.id, memberId)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.members.length).toBe(1)
      expect(updatedParty!.status).toBe(PartyStatus.FORMING) 
    })
    test('should not allow removing the leader', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const result = partyManager.removeMember(party.id, leaderId)
      expect(result).toBe(false)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.members.length).toBe(1) 
    })
  })
  describe('Leadership', () => {
    test('should transfer leadership', () => {
      const leaderId = crypto.randomUUID() as UUID
      const memberId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      partyManager.addMember(party.id, memberId)
      const result = partyManager.transferLeadership(party.id, leaderId, memberId)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.leaderId).toBe(memberId)
      const oldLeader = updatedParty!.members.find(m => m.entityId === leaderId)
      const newLeader = updatedParty!.members.find(m => m.entityId === memberId)
      expect(oldLeader!.role).toBe(PartyRole.MEMBER)
      expect(newLeader!.role).toBe(PartyRole.LEADER)
    })
    test('should not transfer leadership if current leader is incorrect', () => {
      const leaderId = crypto.randomUUID() as UUID
      const memberId = crypto.randomUUID() as UUID
      const fakeLeaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      partyManager.addMember(party.id, memberId)
      const result = partyManager.transferLeadership(party.id, fakeLeaderId, memberId)
      expect(result).toBe(false)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.leaderId).toBe(leaderId) 
    })
  })
  describe('Party Actions and Quests', () => {
    test('should add a quest to a party', () => {
      const leaderId = crypto.randomUUID() as UUID
      const questId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const result = partyManager.addQuestToParty(party.id, questId, leaderId)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.activeQuestIds).toContain(questId)
      expect(updatedParty!.status).toBe(PartyStatus.ON_MISSION)
    })
    test('should complete a quest for a party', () => {
      const leaderId = crypto.randomUUID() as UUID
      const questId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      partyManager.addQuestToParty(party.id, questId, leaderId)
      const result = partyManager.completeQuestForParty(party.id, questId)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.activeQuestIds).not.toContain(questId)
      expect(updatedParty!.completedQuestIds).toContain(questId)
      expect(updatedParty!.status).toBe(PartyStatus.ACTIVE) 
    })
  })
  describe('Party Settings', () => {
    test('should update party settings', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const newSettings = {
        partyColor: '#FF0000',
        isOpen: true,
        description: 'Updated description'
      }
      const result = partyManager.updatePartySettings(party.id, leaderId, newSettings)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.settings).toMatchObject(newSettings)
    })
    test('should set resource sharing policy', () => {
      const leaderId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const result = partyManager.setResourceSharingPolicy(
        party.id, 
        leaderId, 
        ResourceSharingPolicy.PROPORTIONAL
      )
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.resourceSharingPolicy).toBe(ResourceSharingPolicy.PROPORTIONAL)
    })
  })
  describe('Party Queries', () => {
    test('should get parties by status', () => {
      const leaderId1 = crypto.randomUUID() as UUID
      const leaderId2 = crypto.randomUUID() as UUID
      const party1 = partyManager.createParty('Active Party', leaderId1)
      const party2 = partyManager.createParty('Forming Party', leaderId2)
      const memberId = crypto.randomUUID() as UUID
      partyManager.addMember(party1.id, memberId)
      const activeParties = partyManager.getPartiesByStatus(PartyStatus.ACTIVE)
      const formingParties = partyManager.getPartiesByStatus(PartyStatus.FORMING)
      expect(activeParties.length).toBe(1)
      expect(formingParties.length).toBe(1)
      expect(activeParties[0].id).toBe(party1.id)
      expect(formingParties[0].id).toBe(party2.id)
    })
    test('should get parties by member', () => {
      const leaderId = crypto.randomUUID() as UUID
      const memberId = crypto.randomUUID() as UUID
      const party1 = partyManager.createParty('Party 1', leaderId)
      const party2 = partyManager.createParty('Party 2', memberId)
      partyManager.addMember(party2.id, leaderId)
      const leaderParties = partyManager.getPartiesByMember(leaderId)
      expect(leaderParties.length).toBe(2)
      expect(leaderParties.some(p => p.id === party1.id)).toBe(true)
      expect(leaderParties.some(p => p.id === party2.id)).toBe(true)
    })
  })
  describe('Party Invitations', () => {
    test('should send and accept invitations', () => {
      const leaderId = crypto.randomUUID() as UUID
      const inviteeId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const invitation = partyManager.sendInvitation(party.id, leaderId, inviteeId)
      expect(invitation).toBeDefined()
      expect(invitation!.fromEntityId).toBe(leaderId)
      expect(invitation!.toEntityId).toBe(inviteeId)
      const result = partyManager.respondToInvitation(invitation!.id, true)
      expect(result).toBe(true)
      const updatedParty = partyManager.getParty(party.id)
      expect(updatedParty!.members.some(m => m.entityId === inviteeId)).toBe(true)
    })
    test('should not allow non-members to send invitations', () => {
      const leaderId = crypto.randomUUID() as UUID
      const nonMemberId = crypto.randomUUID() as UUID
      const inviteeId = crypto.randomUUID() as UUID
      const party = partyManager.createParty('Test Party', leaderId)
      const invitation = partyManager.sendInvitation(party.id, nonMemberId, inviteeId)
      expect(invitation).toBeNull()
    })
  })
}) 