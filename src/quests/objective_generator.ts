import { QuestObjective, ObjectiveType, QuestType } from './types';

/**
 * Procedural Objective Generator
 * Generates quest objectives based on player state, quest type, location, and context.
 * Each generator returns a QuestObjective[] for injection into quest templates.
 */

export interface ObjectiveGenerationContext {
  playerLevel: number;
  location: string;
  availableTargets: string[];
  questHistory: string[];
  difficulty: number;
  [key: string]: any;
}

// Utility to avoid repetition
const recentObjectives: Set<string> = new Set();

function isObjectiveUnique(objective: QuestObjective): boolean {
  return !recentObjectives.has(objective.id);
}

function markObjectiveUsed(objective: QuestObjective) {
  recentObjectives.add(objective.id);
  if (recentObjectives.size > 50) {
    // Keep only the last 50
    const arr = Array.from(recentObjectives);
    recentObjectives.clear();
    arr.slice(-50).forEach(id => recentObjectives.add(id));
  }
}

export function generateKillObjectives(context: ObjectiveGenerationContext): QuestObjective[] {
  const { availableTargets, difficulty } = context;
  if (!availableTargets.length) return [];
  const target = availableTargets[Math.floor(Math.random() * availableTargets.length)];
  const amount = Math.max(1, Math.floor(Math.random() * (difficulty * 3)));
  const id = `kill_${target}_${Date.now()}`;
  const objective: QuestObjective = {
    id,
    description: `Defeat ${amount} ${target}${amount > 1 ? 's' : ''}`,
    type: 'KILL',
    target,
    amount,
    completed: false
  };
  if (!isObjectiveUnique(objective)) return [];
  markObjectiveUsed(objective);
  return [objective];
}

export function generateCollectObjectives(context: ObjectiveGenerationContext): QuestObjective[] {
  const { availableTargets, difficulty } = context;
  if (!availableTargets.length) return [];
  const target = availableTargets[Math.floor(Math.random() * availableTargets.length)];
  const amount = Math.max(1, Math.floor(Math.random() * (difficulty * 2)));
  const id = `collect_${target}_${Date.now()}`;
  const objective: QuestObjective = {
    id,
    description: `Collect ${amount} ${target}${amount > 1 ? 's' : ''}`,
    type: 'COLLECT',
    target,
    amount,
    completed: false
  };
  if (!isObjectiveUnique(objective)) return [];
  markObjectiveUsed(objective);
  return [objective];
}

export function generateExploreObjectives(context: ObjectiveGenerationContext): QuestObjective[] {
  const { location, difficulty } = context;
  const amount = Math.max(1, Math.floor(Math.random() * (difficulty + 2)));
  const id = `explore_${location}_${Date.now()}`;
  const objective: QuestObjective = {
    id,
    description: `Explore ${amount} locations in ${location}`,
    type: 'EXPLORE',
    location,
    amount,
    completed: false
  };
  if (!isObjectiveUnique(objective)) return [];
  markObjectiveUsed(objective);
  return [objective];
}

export function generateDiplomaticObjectives(context: ObjectiveGenerationContext): QuestObjective[] {
  const { availableTargets, difficulty } = context;
  if (!availableTargets.length) return [];
  const target = availableTargets[Math.floor(Math.random() * availableTargets.length)];
  const id = `diplomatic_${target}_${Date.now()}`;
  const objective: QuestObjective = {
    id,
    description: `Negotiate with ${target}`,
    type: 'DIPLOMATIC_MEETING',
    target,
    completed: false
  };
  if (!isObjectiveUnique(objective)) return [];
  markObjectiveUsed(objective);
  return [objective];
}

export function generateObjectiveForType(type: QuestType, context: ObjectiveGenerationContext): QuestObjective[] {
  switch (type) {
    case 'KILL':
      return generateKillObjectives(context);
    case 'COLLECT':
      return generateCollectObjectives(context);
    case 'EXPLORE':
      return generateExploreObjectives(context);
    case 'DIPLOMATIC':
      return generateDiplomaticObjectives(context);
    default:
      return [];
  }
}

/**
 * Validate that a generated objective conforms to the QuestObjective interface.
 */
export function validateObjective(obj: any): boolean {
  return obj && typeof obj.id === 'string' && typeof obj.description === 'string' && typeof obj.type === 'string';
} 