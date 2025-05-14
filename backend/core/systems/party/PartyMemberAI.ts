/**
 * Party Member AI
 * 
 * Implements behavior patterns for AI-controlled party members.
 * Handles decision making, path finding, combat behavior, and interactions.
 */

import { EventEmitter } from 'events';
import { UUID } from '../../core/types';
import { PartyManager } from './PartyManager';
import { Party, PartyMember, PartyRole } from './types';

// Behavior types to control party member actions
export enum BehaviorType {
  AGGRESSIVE = 'aggressive', // Attack enemies on sight
  DEFENSIVE = 'defensive',   // Only attack when attacked or when leader attacks
  SUPPORTIVE = 'supportive', // Focus on healing and buffing allies
  CAUTIOUS = 'cautious',     // Stay back, avoid danger
  RECKLESS = 'reckless',     // Charge in, take risks
  PROTECTIVE = 'protective', // Prioritize protecting other party members
  RANGED = 'ranged',         // Stay at distance, use ranged attacks
  BALANCED = 'balanced'      // Default balanced behavior
}

// Combat role types
export enum CombatRole {
  TANK = 'tank',             // Absorb damage, hold aggro
  DAMAGE = 'damage',         // Deal damage
  SUPPORT = 'support',       // Heal, buff, debuff
  CONTROL = 'control',       // Crowd control
  SCOUT = 'scout'            // Detect enemies, traps
}

// Follow behavior types
export enum FollowBehavior {
  CLOSE = 'close',           // Stay very close to leader
  NORMAL = 'normal',         // Standard following distance
  FAR = 'far',               // Hang back
  INDEPENDENT = 'independent' // Act independently, return when called
}

// AI events
export enum AIEvents {
  DECISION_MADE = 'ai:decision_made',
  STATE_CHANGED = 'ai:state_changed',
  BEHAVIOR_CHANGED = 'ai:behavior_changed',
  TARGET_SELECTED = 'ai:target_selected',
  PATH_CALCULATED = 'ai:path_calculated',
  COMBAT_ACTION_SELECTED = 'ai:combat_action_selected'
}

// AI state
export enum AIState {
  IDLE = 'idle',
  FOLLOWING = 'following',
  MOVING = 'moving',
  COMBAT = 'combat',
  INTERACTING = 'interacting',
  USING_SKILL = 'using_skill',
  FLEEING = 'fleeing',
  UNCONSCIOUS = 'unconscious'
}

// AI settings interface
export interface AISettings {
  behavior: BehaviorType;
  combatRole: CombatRole;
  followBehavior: FollowBehavior;
  useItems: boolean;
  reactToThreats: boolean;
  assistAllies: boolean;
  fleeThreshold: number; // Health percentage to flee at
  aggroRadius: number;   // How far to detect enemies
  returnRadius: number;  // How far from leader before returning
  skillPreferences: string[]; // Skills to prioritize
  targetPreferences: string[]; // Target types to prioritize
  defaultFollowDistance: number;
  customParameters: Record<string, any>;
}

/**
 * AI Behavior class for party members
 */
export class PartyMemberAI {
  private entityId: UUID;
  private partyId: UUID;
  private partyManager: PartyManager;
  private settings: AISettings;
  private currentState: AIState = AIState.IDLE;
  private currentTarget?: UUID;
  private currentPath?: UUID[];
  private lastDecisionTime: number = 0;
  private eventEmitter: EventEmitter = new EventEmitter();
  private decisionInterval: number = 1000; // Milliseconds between decisions
  
  /**
   * Constructor
   */
  constructor(
    entityId: UUID,
    partyId: UUID,
    initialSettings?: Partial<AISettings>
  ) {
    this.entityId = entityId;
    this.partyId = partyId;
    this.partyManager = PartyManager.getInstance();
    
    // Default settings
    this.settings = {
      behavior: BehaviorType.BALANCED,
      combatRole: CombatRole.DAMAGE,
      followBehavior: FollowBehavior.NORMAL,
      useItems: true,
      reactToThreats: true,
      assistAllies: true,
      fleeThreshold: 25, // Flee at 25% health
      aggroRadius: 10,
      returnRadius: 20,
      skillPreferences: [],
      targetPreferences: [],
      defaultFollowDistance: 3,
      customParameters: {}
    };
    
    // Override with initial settings if provided
    if (initialSettings) {
      this.settings = {
        ...this.settings,
        ...initialSettings
      };
    }
  }
  
  /**
   * Update AI state and make decisions
   */
  public update(currentTime: number, worldState: any): void {
    // Check if it's time to make a new decision
    if (currentTime - this.lastDecisionTime < this.decisionInterval) {
      return; // Not time to update yet
    }
    
    // Get party information
    const party = this.partyManager.getParty(this.partyId);
    if (!party) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Get member information
    const member = party.members.find(m => m.entityId === this.entityId);
    if (!member) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Make decisions based on current state and world state
    switch (this.currentState) {
      case AIState.IDLE:
        this.decideFromIdleState(party, member, worldState);
        break;
      case AIState.FOLLOWING:
        this.decideFromFollowingState(party, member, worldState);
        break;
      case AIState.MOVING:
        this.decideFromMovingState(party, member, worldState);
        break;
      case AIState.COMBAT:
        this.decideFromCombatState(party, member, worldState);
        break;
      case AIState.INTERACTING:
        this.decideFromInteractingState(party, member, worldState);
        break;
      case AIState.USING_SKILL:
        this.decideFromUsingSkillState(party, member, worldState);
        break;
      case AIState.FLEEING:
        this.decideFromFleeingState(party, member, worldState);
        break;
      case AIState.UNCONSCIOUS:
        this.decideFromUnconsciousState(party, member, worldState);
        break;
    }
    
    this.lastDecisionTime = currentTime;
  }
  
  /**
   * Make decisions when in IDLE state
   */
  private decideFromIdleState(party: Party, member: PartyMember, worldState: any): void {
    // If we're a follower, switch to following the leader
    if (member.role !== PartyRole.LEADER) {
      this.setState(AIState.FOLLOWING);
      return;
    }
    
    // Check for threats based on behavior
    if (this.settings.reactToThreats) {
      const threats = this.detectThreats(worldState);
      if (threats.length > 0) {
        this.selectTarget(threats[0]);
        this.setState(AIState.COMBAT);
        return;
      }
    }
    
    // Check for nearby interactable objects
    const interactables = this.detectInteractables(worldState);
    if (interactables.length > 0 && this.shouldInteract(interactables[0], worldState)) {
      this.currentTarget = interactables[0];
      this.setState(AIState.INTERACTING);
      return;
    }
    
    // Stay idle
  }
  
  /**
   * Make decisions when in FOLLOWING state
   */
  private decideFromFollowingState(party: Party, member: PartyMember, worldState: any): void {
    // Get leader
    const leader = party.members.find(m => m.entityId === party.leaderId);
    if (!leader) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Get positions
    const myPosition = this.getPosition(worldState, this.entityId);
    const leaderPosition = this.getPosition(worldState, leader.entityId);
    
    if (!myPosition || !leaderPosition) {
      return;
    }
    
    // Check for threats based on behavior
    if (this.settings.reactToThreats) {
      const threats = this.detectThreats(worldState);
      if (threats.length > 0) {
        // Only engage if the threat is close enough or our behavior dictates it
        const shouldEngage = this.shouldEngageThreats(threats, worldState);
        if (shouldEngage) {
          this.selectTarget(threats[0]);
          this.setState(AIState.COMBAT);
          return;
        }
      }
    }
    
    // Check distance to leader
    const distance = this.calculateDistance(myPosition, leaderPosition);
    
    // Determine target follow distance based on follow behavior
    let targetDistance = this.settings.defaultFollowDistance;
    switch (this.settings.followBehavior) {
      case FollowBehavior.CLOSE:
        targetDistance = 1;
        break;
      case FollowBehavior.NORMAL:
        targetDistance = 3;
        break;
      case FollowBehavior.FAR:
        targetDistance = 5;
        break;
      case FollowBehavior.INDEPENDENT:
        targetDistance = 10;
        break;
    }
    
    // If too far from leader, move to follow
    if (distance > targetDistance) {
      // Calculate path to leader
      const path = this.calculatePath(myPosition, leaderPosition, worldState);
      if (path && path.length > 0) {
        this.currentPath = path;
        this.setState(AIState.MOVING);
        return;
      }
    }
    
    // Check if leader is in combat
    if (this.isEntityInCombat(party.leaderId, worldState)) {
      const leaderTarget = this.getEntityTarget(party.leaderId, worldState);
      if (leaderTarget) {
        this.selectTarget(leaderTarget);
        this.setState(AIState.COMBAT);
        return;
      }
    }
    
    // Continue following
  }
  
  /**
   * Make decisions when in MOVING state
   */
  private decideFromMovingState(party: Party, member: PartyMember, worldState: any): void {
    // Check if we've reached our destination
    const myPosition = this.getPosition(worldState, this.entityId);
    if (!myPosition || !this.currentPath || this.currentPath.length === 0) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Check for threats along the path
    if (this.settings.reactToThreats) {
      const threats = this.detectThreats(worldState);
      if (threats.length > 0) {
        const shouldEngage = this.shouldEngageThreats(threats, worldState);
        if (shouldEngage) {
          this.selectTarget(threats[0]);
          this.setState(AIState.COMBAT);
          return;
        }
      }
    }
    
    // Check if we've reached the next point in the path
    const nextPointId = this.currentPath[0];
    const nextPosition = this.getPosition(worldState, nextPointId);
    
    if (!nextPosition) {
      // Invalid path point, recalculate
      this.currentPath = undefined;
      this.setState(AIState.IDLE);
      return;
    }
    
    const distanceToNext = this.calculateDistance(myPosition, nextPosition);
    if (distanceToNext < 0.5) { // Node reached threshold
      // Remove this point from the path
      this.currentPath.shift();
      
      // If no more points, we've arrived
      if (this.currentPath.length === 0) {
        this.currentPath = undefined;
        
        // If we were following, go back to following state
        if (member.role !== PartyRole.LEADER) {
          this.setState(AIState.FOLLOWING);
        } else {
          this.setState(AIState.IDLE);
        }
        return;
      }
    }
    
    // Continue moving
  }
  
  /**
   * Make decisions when in COMBAT state
   */
  private decideFromCombatState(party: Party, member: PartyMember, worldState: any): void {
    // Check if we have a valid target
    if (!this.currentTarget) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Check if target is still valid
    const targetValid = this.isTargetValid(this.currentTarget, worldState);
    if (!targetValid) {
      // Try to find a new target
      const threats = this.detectThreats(worldState);
      if (threats.length > 0) {
        this.selectTarget(threats[0]);
      } else {
        this.currentTarget = undefined;
        if (member.role !== PartyRole.LEADER) {
          this.setState(AIState.FOLLOWING);
        } else {
          this.setState(AIState.IDLE);
        }
        return;
      }
    }
    
    // Check health for fleeing
    const myHealth = this.getEntityHealth(this.entityId, worldState);
    if (myHealth && myHealth.percentRemaining <= this.settings.fleeThreshold) {
      this.setState(AIState.FLEEING);
      return;
    }
    
    // Select combat action based on role and behavior
    const action = this.selectCombatAction(worldState);
    this.eventEmitter.emit(AIEvents.COMBAT_ACTION_SELECTED, action);
    
    // If action requires a skill, switch to using skill state
    if (action && action.type === 'skill') {
      this.setState(AIState.USING_SKILL);
      return;
    }
    
    // Otherwise continue combat
  }
  
  /**
   * Make decisions when in INTERACTING state
   */
  private decideFromInteractingState(party: Party, member: PartyMember, worldState: any): void {
    // Check if we have a valid interaction target
    if (!this.currentTarget) {
      this.setState(AIState.IDLE);
      return;
    }
    
    // Check if interaction is complete
    const interactionComplete = this.isInteractionComplete(this.currentTarget, worldState);
    if (interactionComplete) {
      this.currentTarget = undefined;
      if (member.role !== PartyRole.LEADER) {
        this.setState(AIState.FOLLOWING);
      } else {
        this.setState(AIState.IDLE);
      }
      return;
    }
    
    // Check for threats that interrupt interaction
    if (this.settings.reactToThreats) {
      const threats = this.detectThreats(worldState);
      if (threats.length > 0 && this.shouldInterruptForThreat(threats[0], worldState)) {
        this.selectTarget(threats[0]);
        this.setState(AIState.COMBAT);
        return;
      }
    }
    
    // Continue interacting
  }
  
  /**
   * Make decisions when in USING_SKILL state
   */
  private decideFromUsingSkillState(party: Party, member: PartyMember, worldState: any): void {
    // Check if skill usage is complete
    const skillComplete = this.isSkillComplete(worldState);
    if (skillComplete) {
      // Return to appropriate state
      if (this.currentTarget && this.isTargetValid(this.currentTarget, worldState)) {
        this.setState(AIState.COMBAT);
      } else if (member.role !== PartyRole.LEADER) {
        this.setState(AIState.FOLLOWING);
      } else {
        this.setState(AIState.IDLE);
      }
      return;
    }
    
    // Continue using skill
  }
  
  /**
   * Make decisions when in FLEEING state
   */
  private decideFromFleeingState(party: Party, member: PartyMember, worldState: any): void {
    // Check if we're now safe
    const threats = this.detectThreats(worldState);
    if (threats.length === 0) {
      // We're safe, return to following/idle
      if (member.role !== PartyRole.LEADER) {
        this.setState(AIState.FOLLOWING);
      } else {
        this.setState(AIState.IDLE);
      }
      return;
    }
    
    // Check health to see if we're recovered enough to fight
    const myHealth = this.getEntityHealth(this.entityId, worldState);
    if (myHealth && myHealth.percentRemaining > this.settings.fleeThreshold * 1.5) {
      // We've recovered enough to return to combat
      this.selectTarget(threats[0]);
      this.setState(AIState.COMBAT);
      return;
    }
    
    // Calculate safety position (away from threats, toward party)
    const safePosition = this.calculateSafePosition(threats, party, worldState);
    if (safePosition) {
      const myPosition = this.getPosition(worldState, this.entityId);
      if (myPosition) {
        // See if we need to update our path
        if (!this.currentPath || this.currentPath.length === 0) {
          this.currentPath = this.calculatePath(myPosition, safePosition, worldState);
        }
      }
    }
    
    // Continue fleeing
  }
  
  /**
   * Make decisions when in UNCONSCIOUS state
   */
  private decideFromUnconsciousState(party: Party, member: PartyMember, worldState: any): void {
    // Check if we're revived
    const myHealth = this.getEntityHealth(this.entityId, worldState);
    if (myHealth && myHealth.current > 0) {
      // We're revived, return to appropriate state
      if (member.role !== PartyRole.LEADER) {
        this.setState(AIState.FOLLOWING);
      } else {
        this.setState(AIState.IDLE);
      }
      return;
    }
    
    // Continue being unconscious
  }
  
  /**
   * Set AI state
   */
  public setState(newState: AIState): void {
    const oldState = this.currentState;
    this.currentState = newState;
    this.eventEmitter.emit(AIEvents.STATE_CHANGED, oldState, newState);
  }
  
  /**
   * Get current AI state
   */
  public getState(): AIState {
    return this.currentState;
  }
  
  /**
   * Set AI behavior
   */
  public setBehavior(behavior: BehaviorType): void {
    const oldBehavior = this.settings.behavior;
    this.settings.behavior = behavior;
    this.eventEmitter.emit(AIEvents.BEHAVIOR_CHANGED, oldBehavior, behavior);
  }
  
  /**
   * Update AI settings
   */
  public updateSettings(newSettings: Partial<AISettings>): void {
    this.settings = {
      ...this.settings,
      ...newSettings
    };
  }
  
  /**
   * Get current settings
   */
  public getSettings(): AISettings {
    return { ...this.settings };
  }
  
  /**
   * Select a target
   */
  private selectTarget(targetId: UUID): void {
    const oldTarget = this.currentTarget;
    this.currentTarget = targetId;
    this.eventEmitter.emit(AIEvents.TARGET_SELECTED, oldTarget, targetId);
  }
  
  /**
   * Calculate distance between two positions
   */
  private calculateDistance(pos1: any, pos2: any): number {
    // Simple distance calculation (can be replaced with more complex logic)
    const dx = pos1.x - pos2.x;
    const dy = pos1.y - pos2.y;
    return Math.sqrt(dx * dx + dy * dy);
  }
  
  /**
   * Calculate path between two positions
   */
  private calculatePath(start: any, end: any, worldState: any): UUID[] | undefined {
    // This would normally use a pathfinding algorithm
    // For now, return a dummy path
    const path: UUID[] = [];
    
    // Add some intermediate points
    path.push(crypto.randomUUID() as UUID);
    path.push(crypto.randomUUID() as UUID);
    
    this.eventEmitter.emit(AIEvents.PATH_CALCULATED, path);
    return path;
  }
  
  /**
   * Detect threats in the world state
   */
  private detectThreats(worldState: any): UUID[] {
    // This would be implemented to scan the world state for threats
    // Return a list of entity IDs that are threats
    return [];
  }
  
  /**
   * Detect interactable objects in the world state
   */
  private detectInteractables(worldState: any): UUID[] {
    // This would be implemented to scan the world state for interactable objects
    // Return a list of entity IDs that can be interacted with
    return [];
  }
  
  /**
   * Get entity position from world state
   */
  private getPosition(worldState: any, entityId: UUID): any {
    // This would extract position data from the world state
    return { x: 0, y: 0 };
  }
  
  /**
   * Get entity health from world state
   */
  private getEntityHealth(entityId: UUID, worldState: any): { current: number, max: number, percentRemaining: number } | undefined {
    // This would extract health data from the world state
    return {
      current: 100,
      max: 100,
      percentRemaining: 100
    };
  }
  
  /**
   * Check if an entity is in combat
   */
  private isEntityInCombat(entityId: UUID, worldState: any): boolean {
    // This would check if an entity is in combat state
    return false;
  }
  
  /**
   * Get entity's current target
   */
  private getEntityTarget(entityId: UUID, worldState: any): UUID | undefined {
    // This would get the entity's current target
    return undefined;
  }
  
  /**
   * Check if a target is still valid
   */
  private isTargetValid(targetId: UUID, worldState: any): boolean {
    // This would check if a target is still valid (alive, in range, etc)
    return true;
  }
  
  /**
   * Check if an interaction is complete
   */
  private isInteractionComplete(targetId: UUID, worldState: any): boolean {
    // This would check if an interaction with an object is complete
    return false;
  }
  
  /**
   * Check if skill usage is complete
   */
  private isSkillComplete(worldState: any): boolean {
    // This would check if a skill usage is complete
    return true;
  }
  
  /**
   * Calculate a safe position to flee to
   */
  private calculateSafePosition(threats: UUID[], party: Party, worldState: any): any {
    // This would calculate a safe position to flee to
    return { x: 0, y: 0 };
  }
  
  /**
   * Determine if the AI should interact with an object
   */
  private shouldInteract(objectId: UUID, worldState: any): boolean {
    // This would determine if the AI should interact with an object
    return true;
  }
  
  /**
   * Determine if the AI should engage threats
   */
  private shouldEngageThreats(threats: UUID[], worldState: any): boolean {
    // This would determine if the AI should engage threats based on behavior
    switch (this.settings.behavior) {
      case BehaviorType.AGGRESSIVE:
        return true;
      case BehaviorType.DEFENSIVE:
        // Only if we're attacked or leader is attacked
        return false;
      case BehaviorType.CAUTIOUS:
        // Only if no choice
        return false;
      case BehaviorType.RECKLESS:
        return true;
      default:
        return false;
    }
  }
  
  /**
   * Determine if an interaction should be interrupted for a threat
   */
  private shouldInterruptForThreat(threatId: UUID, worldState: any): boolean {
    // This would determine if an interaction should be interrupted
    return true;
  }
  
  /**
   * Select a combat action based on role and behavior
   */
  private selectCombatAction(worldState: any): any {
    // This would select a combat action based on role and behavior
    return {
      type: 'attack',
      target: this.currentTarget,
      skill: null
    };
  }
  
  /**
   * Subscribe to AI events
   */
  public on(event: AIEvents, listener: (...args: any[]) => void): void {
    this.eventEmitter.on(event, listener);
  }
  
  /**
   * Unsubscribe from AI events
   */
  public off(event: AIEvents, listener: (...args: any[]) => void): void {
    this.eventEmitter.off(event, listener);
  }
} 