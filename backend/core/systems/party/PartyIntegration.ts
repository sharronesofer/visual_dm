import { eventBus } from '../../../../src/eventBus/EventBus';
import { PartyIntegrationEventType, PartyIntegrationEventPayload } from '../../../../src/interfaces/PartyIntegrationEvents';
import { partyManager, PartyEvents, Party, PartyMember } from './index';
import { reputationSystem } from '../../../../src/systems/npc/ReputationSystem';
import { emotionSystem } from '../../../../src/systems/npc/EmotionSystem';
import { InteractionType, InteractionResult } from '../../../../src/systems/npc/InteractionSystem';
import { NPCData } from '../../../../src/core/interfaces/types/npc/npc';

// Helper to convert PartyMember to minimal NPCData (for demo purposes)
function partyMemberToNPCData(member: PartyMember): NPCData {
    return {
        id: member.entityId,
        name: '',
        faction: undefined as any,
        position: { x: 0, y: 0 },
        traits: [],
        values: [],
        goals: [],
        stats: {} as any,
        personality: {
            traits: new Map(),
            compatibilityProfile: { preferredTraits: [], avoidedTraits: [], adaptability: 0 },
            socialPreferences: {
                groupSize: { min: 1, optimal: 4, max: 8 },
                leadershipStyle: 'collaborative',
                conflictResolution: 'diplomatic',
            },
        },
        skills: new Map(),
        inventory: [],
        relationships: new Map(),
        memories: [],
        location: '',
        groupAffiliations: [],
        socialStatus: { reputation: 0, influence: 0, trustworthiness: 0, lastInteractionTime: 0, recentInteractions: [] },
        learningProgress: new Map(),
        recentInteractions: [],
        interactionHistory: { individual: new Map(), group: new Map() },
        groupFormationPreferences: { triggers: { emergency: 0, resource: 0, goal: 0, social: 0 }, rolePreferences: [], purposeWeights: new Map(), minTrustThreshold: 0 },
    };
}

// Helper to emit party integration events
export function emitPartyEvent(eventType: PartyIntegrationEventType, party: Party, member?: PartyMember) {
    const payload: PartyIntegrationEventPayload = {
        partyId: party.id,
        memberId: member?.entityId,
        timestamp: Date.now(),
    };
    eventBus.emit(eventType, payload);
}

// --- Party <-> Reputation Integration ---
partyManager.on(PartyEvents.MEMBER_KICKED, async (party: Party, member: PartyMember) => {
    // Decrease reputation for being kicked from a party
    const npc = partyMemberToNPCData(member);
    const result: InteractionResult = {
        success: false,
        type: InteractionType.GROUP_DECISION,
        participants: [member.entityId],
        outcome: {
            description: 'Kicked from party',
            effects: { reputation: -0.2 },
        },
        context: {
            npcId: member.entityId,
            targetId: party.id,
            type: InteractionType.GROUP_DECISION,
        },
        timestamp: Date.now(),
    };
    eventBus.emit(PartyIntegrationEventType.MEMBER_KICKED, {
        party,
        member,
        npc,
        result,
        eventType: PartyIntegrationEventType.MEMBER_KICKED,
        timestamp: Date.now(),
    });
});

partyManager.on(PartyEvents.MEMBER_JOINED, async (party: Party, member: PartyMember) => {
    // Slightly increase reputation for joining a party
    const npc = partyMemberToNPCData(member);
    const result: InteractionResult = {
        success: true,
        type: InteractionType.GROUP_DECISION,
        participants: [member.entityId],
        outcome: {
            description: 'Joined party',
            effects: { reputation: 0.05 },
        },
        context: {
            npcId: member.entityId,
            targetId: party.id,
            type: InteractionType.GROUP_DECISION,
        },
        timestamp: Date.now(),
    };
    eventBus.emit(PartyIntegrationEventType.MEMBER_JOINED, {
        party,
        member,
        npc,
        result,
        eventType: PartyIntegrationEventType.MEMBER_JOINED,
        timestamp: Date.now(),
    });
});

// --- Party <-> Emotion Integration ---
partyManager.on(PartyEvents.PARTY_DISBANDED, (party: Party) => {
    // Trigger a 'loss' emotion for all members
    party.members.forEach(member => {
        const npc = partyMemberToNPCData(member);
        const result: InteractionResult = {
            success: false,
            type: InteractionType.GROUP_DECISION,
            participants: [member.entityId],
            outcome: {
                description: 'Party disbanded',
                effects: { reputation: 0 },
            },
            context: {
                npcId: member.entityId,
                targetId: party.id,
                type: InteractionType.GROUP_DECISION,
            },
            timestamp: Date.now(),
        };
        eventBus.emit(PartyIntegrationEventType.PARTY_DISBANDED, {
            party,
            member,
            npc,
            result,
            eventType: PartyIntegrationEventType.PARTY_DISBANDED,
            timestamp: Date.now(),
        });
    });
});

// Example usage: Replace direct PartyManager event subscriptions with eventBus emissions
// (In actual PartyManager methods, call emitPartyEvent at the appropriate places)
//
// emitPartyEvent(PartyIntegrationEventType.MEMBER_KICKED, party, member);
// emitPartyEvent(PartyIntegrationEventType.MEMBER_JOINED, party, member);
// emitPartyEvent(PartyIntegrationEventType.PARTY_DISBANDED, party); 