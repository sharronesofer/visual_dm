export interface MovementState {
  speed: number;
  staminaCost: number;
  // Add any other movement-related stats that can be affected by weather
  jumpHeight?: number;
  climbSpeed?: number;
  swimSpeed?: number;
  terrainPenalty?: number;
} 