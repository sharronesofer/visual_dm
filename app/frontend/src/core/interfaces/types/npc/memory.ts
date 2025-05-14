export interface MemoryEvent {
  id: string;
  timestamp: number;
  type: MemoryEventType;
  importance: number;  // 0-100, higher is more important
  participants: string[];  // NPC IDs involved
  location?: string;
  details: {
    description: string;
    emotionalImpact: number;  // -10 to 10
    [key: string]: any;  // Additional event-specific details
  };
  tags: string[];  // For categorization and retrieval
  relatedMemories?: string[];  // IDs of related memory events
}

export enum MemoryEventType {
  INTERACTION = 'interaction',
  OBSERVATION = 'observation',
  EXPERIENCE = 'experience',
  INFORMATION = 'information',
  DECISION = 'decision',
  EMOTIONAL = 'emotional',
  ACHIEVEMENT = 'achievement',
  CONFLICT = 'conflict',
  TRADE = 'trade',
  QUEST = 'quest',
  RELATIONSHIP_CHANGE = 'relationship_change',
  FACTION_EVENT = 'faction_event',
  WORLD_EVENT = 'world_event',
  DECEPTION = 'deception',
  COOPERATION = 'cooperation',
  COMPETITION = 'competition'
}

export interface NPCMemory {
  npcId: string;
  shortTermMemory: MemoryEvent[];  // Recent events, not yet processed
  longTermMemory: MemoryEvent[];   // Processed and stored events
  memoryStats: {
    totalMemories: number;
    lastProcessed: number;
    significantEventCount: number;  // Events with importance > threshold
  };
  relationships: Map<string, {
    trust: number;  // -10 to 10
    lastInteraction: number;
    sharedMemories: string[];  // Memory event IDs
  }>;
}

export interface MemoryQuery {
  type?: MemoryEventType;
  participants?: string[];
  requireAllParticipants?: boolean;
  tags?: string[];
  matchAllTags?: boolean;
  minImportance?: number;
  limit?: number;
}

export interface MemoryProcessingResult {
  compressedEvents: MemoryEvent[];
  significantEvents: MemoryEvent[];
  forgottenEvents: string[];  // IDs of events that were forgotten
  updatedRelationships: {
    [npcId: string]: {
      oldTrust: number;
      newTrust: number;
      reason: string;
    };
  };
}

// Constants for memory system configuration
export const MEMORY_CONSTANTS = {
  SHORT_TERM_CAPACITY: 50,  // Maximum events in short-term memory
  PROCESSING_INTERVAL: 3600000,  // Process memories every hour (in ms)
  IMPORTANCE_THRESHOLD: 70,  // Minimum importance for long-term storage
  MEMORY_DECAY_RATE: 0.1,   // Rate at which memory importance decays
  COMPRESSION_THRESHOLD: 3,  // Number of similar events before compression
  MAX_MEMORY_AGE: 30 * 24 * 3600000,  // Maximum age of memories (30 days in ms)
  RELATIONSHIP_DECAY_RATE: 0.05,  // Rate at which relationship values decay
  EMOTIONAL_IMPACT_WEIGHT: 0.3,  // Weight of emotional impact in importance
  MEMORY_SHARING_THRESHOLD: 0.7,  // Minimum trust for memory sharing
} as const;

// Helper type for memory importance calculation
export interface ImportanceFactors {
  baseImportance: number;
  emotionalImpact: number;
  participantCount: number;
  relationshipStrength: number;
  timeRelevance: number;
  eventType: MemoryEventType;
}

// Memory compression strategies
export enum CompressionStrategy {
  SUMMARIZE = 'summarize',  // Combine similar events into a summary
  PRUNE = 'prune',         // Remove less important details
  AGGREGATE = 'aggregate'   // Group related events together
}

// Memory retrieval context
export interface MemoryContext {
  currentLocation?: string;
  currentActivity?: string;
  emotionalState?: number;  // -10 to 10
  timeOfDay?: number;       // 0-23
  recentEvents?: string[];  // IDs of recent events
  activeFactions?: string[];
  activeQuests?: string[];
}

export interface Memory {
  id: string;
  type: MemoryEventType;
  time: number;
  participants: string[];
  location: string;
  details: {
    eventType: string;
    description: string;
    outcome: string;
    emotionalImpact: number;
    importance: number;
  };
  relationships: {
    npcId: string;
    impact: number;
    type: string;
  }[];
  tags: string[];
  associatedMemories: string[];
  lastRecallTime?: number;
  recallCount: number;
  decayRate: number;
}

export interface MemoryManager {
  getRelevantMemories(
    npcId: string,
    context: string,
    targetId?: string
  ): Promise<Memory[]>;
  
  addMemory(
    npcId: string,
    memory: Omit<Memory, 'id' | 'recallCount' | 'lastRecallTime'>
  ): Promise<Memory>;
  
  updateMemory(
    npcId: string,
    memoryId: string,
    updates: Partial<Memory>
  ): Promise<Memory>;
  
  getMemoryById(
    npcId: string,
    memoryId: string
  ): Promise<Memory | null>;
  
  searchMemories(
    npcId: string,
    query: {
      type?: MemoryEventType;
      tags?: string[];
      participants?: string[];
      timeRange?: {
        start: number;
        end: number;
      };
      importance?: {
        min: number;
        max: number;
      };
    }
  ): Promise<Memory[]>;
  
  forgetMemory(
    npcId: string,
    memoryId: string
  ): Promise<boolean>;
  
  calculateMemoryImportance(
    memory: Memory,
    currentContext?: any
  ): Promise<number>;
  
  associateMemories(
    npcId: string,
    memoryIds: string[]
  ): Promise<boolean>;
} 