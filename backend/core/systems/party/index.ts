/**
 * Party Management System
 * 
 * This is the main entry point for the party management system.
 * It provides tools for creating and managing parties, handling party members,
 * and controlling party member AI behavior.
 */

// Export all types and enums
export * from './types';
export { PartyManager, PartyEvents } from './PartyManager';
export { 
  PartyMemberAI, 
  BehaviorType, 
  CombatRole, 
  FollowBehavior, 
  AIEvents, 
  AIState
} from './PartyMemberAI';
// Export types with 'export type'
export type { AISettings } from './PartyMemberAI';

// Provide singleton instance for easy access
import { PartyManager } from './PartyManager';
export const partyManager = PartyManager.getInstance(); 