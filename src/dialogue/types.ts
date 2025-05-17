export interface ConversationTurn {
    role: 'user' | 'system' | 'assistant' | 'npc';
    content: string;
    timestamp?: number;
}

export interface DialogueMetadata {
    tokensUsed: number;
    responseTimeMs: number;
    model: string;
    [key: string]: any;
}

export type DialogueRole = 'user' | 'system' | 'assistant' | 'npc'; 