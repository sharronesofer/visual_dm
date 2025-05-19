# Party Management System Usage Examples

This document provides examples and usage patterns for the Party Management System.

## Basic Setup

The Party Management System provides a singleton pattern for easy access:

```typescript
import { partyManager, PartyRole, PartyStatus } from '../'

// The system uses a singleton instance that's already initialized
// No additional setup required
```

## Creating and Managing Parties

### Creating a Party

```typescript
import { partyManager, PartyRole } from '../'
import { UUID } from '../../../core/types'

// Create a new party
const leaderId = 'player-123' as UUID
const party = partyManager.createParty(
  'The Adventurers', // name
  leaderId,          // leaderId
  'A brave group of heroes', // description (optional)
  false,             // isPublic (optional, default: false)
  5                  // maxSize (optional, default: 4)
)

console.log(`Created party: ${party.name} with ID: ${party.id}`)
```

### Managing Party Members

```typescript
// Send invitations to join a party
const invitation = partyManager.sendInvitation(
  party.id,           // partyId
  leaderId,           // fromEntityId (must have invite permission)
  'player-456',       // toEntityId
  'Join our adventure!', // message (optional)
  3600000             // expiresInMs (optional, default: 24 hours)
)

// Accept an invitation
partyManager.respondToInvitation(invitation.id, true)

// Reject an invitation
partyManager.respondToInvitation(invitation.id, false)

// Add a member directly (bypassing the invitation system)
partyManager.addMember(
  party.id,           // partyId
  'npc-123',          // entityId
  PartyRole.FOLLOWER  // role (optional, default: MEMBER)
)

// Remove a member
partyManager.removeMember(
  party.id,           // partyId
  'player-456',       // entityId
  true                // isKicked (optional, default: false)
)

// Transfer leadership
partyManager.transferLeadership(
  party.id,           // partyId
  leaderId,           // currentLeaderId
  'player-456'        // newLeaderId
)

// Change a member's role
partyManager.changeMemberRole(
  party.id,           // partyId
  leaderId,           // changerId (must be the leader)
  'npc-123',          // targetId
  PartyRole.ADVISER   // newRole
)
```

### Party Quests and Actions

```typescript
// Assign a quest to a party
partyManager.addQuestToParty(
  party.id,           // partyId
  'quest-789',        // questId
  leaderId            // assignerId (must have permission)
)

// Complete a quest
partyManager.completeQuestForParty(
  party.id,           // partyId
  'quest-789'         // questId
)

// Register a party action
const action = partyManager.registerPartyAction(
  party.id,           // partyId
  {
    name: 'Group Charge',
    description: 'The party charges forward as one',
    requiredRoles: [PartyRole.LEADER],
    requiredAbilities: ['combat'],
    minMembers: 3,
    cooldown: 60000,  // 1 minute cooldown
    effects: ['group_speed_boost', 'intimidate_enemies']
  }
)

// Get available party actions
const availableActions = partyManager.getAvailablePartyActions(party.id)

// Use a party action
partyManager.usePartyAction(
  party.id,           // partyId
  action.id,          // actionId
  leaderId            // initiatorId
)
```

### Party Settings and Bonuses

```typescript
import { ResourceSharingPolicy } from '../'

// Update party settings
partyManager.updatePartySettings(
  party.id,           // partyId
  leaderId,           // updaterId (must be the leader)
  {
    partyColor: '#FF0000',
    partySymbol: 'dragon',
    allowMemberInvites: true
  }
)

// Set resource sharing policy
partyManager.setResourceSharingPolicy(
  party.id,           // partyId
  leaderId,           // updaterId (must be the leader)
  ResourceSharingPolicy.PROPORTIONAL // new policy
)

// Add a party bonus
partyManager.addPartyBonus(
  party.id,           // partyId
  {
    name: 'Diverse Group',
    description: 'Bonus for having diverse roles',
    statModifiers: [
      { stat: 'wisdom', value: 2, type: 'flat' },
      { stat: 'perception', value: 10, type: 'percentage' }
    ],
    conditions: [
      { 
        type: 'role_count', 
        value: [PartyRole.ADVISER, 1], 
        operator: '>=' 
      },
      { 
        type: 'member_count', 
        value: 3, 
        operator: '>=' 
      }
    ]
  }
)

// Recalculate party bonuses (when party composition changes)
const activeBonus = partyManager.recalculatePartyBonuses(party.id)
```

### Party Queries

```typescript
// Get a specific party
const retrievedParty = partyManager.getParty(party.id)

// Get all parties
const allParties = partyManager.getAllParties()

// Get parties by status
const activeParties = partyManager.getPartiesByStatus(PartyStatus.ACTIVE)
const missionParties = partyManager.getPartiesByStatus(PartyStatus.ON_MISSION)

// Get parties by member
const memberParties = partyManager.getPartiesByMember('player-456')

// Get only active parties for a member
const activeMemberParties = partyManager.getActivePartiesForMember('player-456')
```

## AI Party Members

AI-controlled party members can be managed with the PartyMemberAI class:

```typescript
import { PartyMemberAI, BehaviorType, CombatRole, FollowBehavior, AIState } from '../'

// Create an AI controller for a party member
const npcId = 'npc-123'
const ai = new PartyMemberAI(
  npcId,             // entityId
  party.id,          // partyId
  {
    // Custom settings (all fields optional)
    behavior: BehaviorType.SUPPORTIVE,
    combatRole: CombatRole.SUPPORT,
    followBehavior: FollowBehavior.CLOSE,
    useItems: true,
    reactToThreats: true,
    assistAllies: true,
    fleeThreshold: 25, // Flee at 25% health
    skillPreferences: ['heal', 'buff', 'debuff'],
    targetPreferences: ['wounded_ally', 'enemy_mage']
  }
)

// Update the AI in your game loop
function gameLoop() {
  const currentTime = Date.now()
  const worldState = { 
    // Your world state here (positions, health, targets, etc.)
  }
  
  // This will make decisions based on state, behavior, and world
  ai.update(currentTime, worldState)
  
  // The AI's state tells you what it wants to do
  const aiState = ai.getState() // IDLE, FOLLOWING, COMBAT, etc.
  
  // Handle the AI's actions based on state...
}

// Change behavior during gameplay
ai.setBehavior(BehaviorType.AGGRESSIVE)

// Update settings during gameplay
ai.updateSettings({
  combatRole: CombatRole.DAMAGE,
  fleeThreshold: 10 // More reckless, flees at 10% health
})

// Listen for AI events
ai.on(AIEvents.STATE_CHANGED, (oldState, newState) => {
  console.log(`AI state changed from ${oldState} to ${newState}`)
})

ai.on(AIEvents.TARGET_SELECTED, (oldTarget, newTarget) => {
  console.log(`AI changed target from ${oldTarget} to ${newTarget}`)
})
```

## Event System

The Party Management System provides an event system for reacting to changes:

```typescript
import { PartyEvents } from '../'

// Subscribe to party events
partyManager.on(PartyEvents.PARTY_CREATED, (party) => {
  console.log(`New party created: ${party.name}`)
})

partyManager.on(PartyEvents.MEMBER_JOINED, (party, member) => {
  console.log(`${member.entityId} joined party ${party.name}`)
})

partyManager.on(PartyEvents.LEADERSHIP_TRANSFERRED, (party, oldLeaderId, newLeaderId) => {
  console.log(`Leadership of ${party.name} transferred from ${oldLeaderId} to ${newLeaderId}`)
})

// Unsubscribe when needed
const handler = (party) => console.log(`Quest added to ${party.name}`)
partyManager.on(PartyEvents.QUEST_ADDED, handler)

// Later...
partyManager.off(PartyEvents.QUEST_ADDED, handler)
``` 