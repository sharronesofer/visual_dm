export type FactionType = 'guild' | 'order' | 'syndicate' | 'militia' | 'cult';

export interface FactionStyle {
  id: string;
  name: string;
  description: string;
  colorScheme: string[];
  architecturalFeatures: string[];
  decor: string[];
}

export interface FactionRoom {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  length: number;
  specialPurpose?: string;
}

export interface FactionNPC {
  id: string;
  role: string;
  hierarchyLevel: number;
  behaviorProfile: string;
}

export interface SecurityFeature {
  id: string;
  type: string;
  location: { x: number; y: number };
  strength: number;
}

export interface FactionHQLayout {
  rooms: FactionRoom[];
  npcs: FactionNPC[];
  security: SecurityFeature[];
  style: FactionStyle;
  decor: string[];
} 