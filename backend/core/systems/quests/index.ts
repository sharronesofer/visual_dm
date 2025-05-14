/**
 * Quest and Arc Generation Framework
 * 
 * This is the main entry point for the quest and narrative arc system.
 * It provides tools for generating, tracking, and progressing quests and narrative arcs.
 */

// Export all types
export * from './types';

// Export the main managers and generators
export { QuestManager, QuestEvents } from './QuestManager';
export { ArcManager, ArcEvents } from './ArcManager';
export { QuestGenerator } from './QuestGenerator';
// Export types with 'export type'
export type { QuestTemplate, ObjectiveTemplate, RewardTemplate } from './QuestGenerator';

// Provide singleton instances for easy access
import { QuestManager } from './QuestManager';
import { ArcManager } from './ArcManager';
import { QuestGenerator } from './QuestGenerator';

// Export singleton instances
export const questManager = QuestManager.getInstance();
export const arcManager = ArcManager.getInstance();
export const questGenerator = QuestGenerator.getInstance(); 