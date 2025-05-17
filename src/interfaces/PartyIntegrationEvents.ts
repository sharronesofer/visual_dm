export enum PartyIntegrationEventType {
    MEMBER_KICKED = 'party:member_kicked',
    MEMBER_JOINED = 'party:member_joined',
    PARTY_DISBANDED = 'party:disbanded',
    PARTY_CREATED = 'party:created',
    INVITATION_SENT = 'party:invitation_sent',
    INVITATION_ACCEPTED = 'party:invitation_accepted',
    INVITATION_DECLINED = 'party:invitation_declined',
    MEMBER_LEFT = 'party:member_left',
    PARTY_UPDATED = 'party:updated',
    LEADERSHIP_TRANSFERRED = 'party:leadership_transferred',
    ROLE_CHANGED = 'party:role_changed',
    QUEST_ADDED = 'party:quest_added',
    QUEST_COMPLETED = 'party:quest_completed',
    // ...add more as needed
}

export interface PartyIntegrationEventPayload {
    partyId: string;
    memberId?: string;
    timestamp: number;
    // Additional context as needed
} 