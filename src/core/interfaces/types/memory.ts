import { FactionType } from '../worldgen/faction/types';

export enum MemoryType {
  EVENT = 'event',
  INTERACTION = 'interaction',
  KNOWLEDGE = 'knowledge',
  RUMOR = 'rumor',
  BACKSTORY = 'backstory',
  KEYSTONE = 'keystone'
}

export enum MemoryLayer {
  IMMEDIATE = 'immediate',
  SHORT_TERM = 'short_term',
  MEDIUM_TERM = 'medium_term',
  LONG_TERM = 'long_term',
  PERMANENT = 'permanent'
}

export interface Memory {
  id: string;
  npcId: string;
  type: MemoryType;
  layer: MemoryLayer;
  content: string;
  timestamp: Date;
  lastAccessed: Date;
  importance: number;
  clarity: number;
  emotionalImpact: number;
  tags: string[];
  relatedNpcIds?: string[];
  relatedFactions?: FactionType[];
  location?: string;
  context?: Record<string, any>;
}

export interface MemorySummary {
  id: string;
  sourceMemoryIds: string[];
  content: string;
  layer: MemoryLayer;
  timestamp: Date;
  importance: number;
  tags: string[];
}

export interface NPCKnowledge {
  npcId: string;
  backstory: Record<string, any>;
  memories: Record<MemoryLayer, Memory[]>;
  summaries: Record<MemoryLayer, MemorySummary[]>;
  lastUpdate: Date;
}

export interface MemoryConfig {
  maxMemoriesPerLayer: Record<MemoryLayer, number>;
  decayRates: Record<MemoryLayer, number>;
  promotionThresholds: Record<MemoryLayer, number>;
  importanceThresholds: {
    low: number;
    medium: number;
    high: number;
  };
  compressionRatio: number;
  minClarityThreshold: number;
}

export interface MemoryQueryOptions {
  types?: MemoryType[];
  layers?: MemoryLayer[];
  minImportance?: number;
  minClarity?: number;
  tags?: string[];
  relatedNpcIds?: string[];
  relatedFactions?: FactionType[];
  startDate?: Date;
  endDate?: Date;
  location?: string;
  limit?: number;
} 