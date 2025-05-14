import { ScreenType } from '../utils/screenNavigation';

export interface GameState {
  currentLocation?: {
    hasPOI: boolean;
    poiId?: string;
  };
  party?: {
    members: string[];
  };
  inventory?: {
    hasItems: boolean;
  };
}

export interface NavigationState {
  currentScreen: ScreenType;
  previousScreen?: ScreenType;
  history: ScreenType[];
  isTransitioning: boolean;
}

export interface NavigationOptions {
  animate?: boolean;
  skipAccessibilityCheck?: boolean;
  preserveHistory?: boolean;
}

export type NavigationDirection = 'next' | 'previous' | 'specific';
