import { ScreenType, NavigationOrder } from './screenNavigation';
import {
  GameState,
  NavigationState,
  NavigationOptions,
} from '../types/navigation';

type NavigationEventType =
  | 'beforeNavigate'
  | 'afterNavigate'
  | 'navigationBlocked';
type NavigationEventHandler = (
  from: ScreenType,
  to: ScreenType,
  options?: NavigationOptions
) => void;

export class NavigationManager {
  private static instance: NavigationManager;
  private state: NavigationState;
  private eventHandlers: Map<NavigationEventType, Set<NavigationEventHandler>>;
  private isTransitioning: boolean = false;

  private constructor() {
    this.state = {
      currentScreen: ScreenType.RegionMap,
      previousScreen: undefined,
      history: [ScreenType.RegionMap],
      isTransitioning: false,
    };
    this.eventHandlers = new Map();
  }

  static getInstance(): NavigationManager {
    if (!NavigationManager.instance) {
      NavigationManager.instance = new NavigationManager();
    }
    return NavigationManager.instance;
  }

  // Event handling methods
  addEventListener(
    type: NavigationEventType,
    handler: NavigationEventHandler
  ): void {
    if (!this.eventHandlers.has(type)) {
      this.eventHandlers.set(type, new Set());
    }
    this.eventHandlers.get(type)!.add(handler);
  }

  removeEventListener(
    type: NavigationEventType,
    handler: NavigationEventHandler
  ): void {
    this.eventHandlers.get(type)?.delete(handler);
  }

  private emitEvent(
    type: NavigationEventType,
    from: ScreenType,
    to: ScreenType,
    options?: NavigationOptions
  ): void {
    this.eventHandlers
      .get(type)
      ?.forEach(handler => handler(from, to, options));
  }

  // Navigation methods
  async navigateTo(
    screen: ScreenType,
    gameState: GameState,
    options: NavigationOptions = {}
  ): Promise<boolean> {
    if (this.isTransitioning && !options.skipTransitionCheck) {
      return false;
    }

    const currentScreen = this.state.currentScreen;

    // Check if screen is accessible
    if (
      !options.skipAccessibilityCheck &&
      !NavigationOrder.isScreenAccessible(screen, gameState)
    ) {
      this.emitEvent('navigationBlocked', currentScreen, screen, options);
      return false;
    }

    this.emitEvent('beforeNavigate', currentScreen, screen, options);

    // Start transition
    this.isTransitioning = true;
    this.state.isTransitioning = true;

    try {
      // Update navigation state
      this.state.previousScreen = currentScreen;
      this.state.currentScreen = screen;

      if (!options.preserveHistory) {
        this.state.history.push(screen);
      }

      // Wait for transition animation if needed
      if (options.animate) {
        await new Promise(resolve => setTimeout(resolve, 300)); // Match with CSS transition duration
      }

      this.emitEvent('afterNavigate', currentScreen, screen, options);
      return true;
    } finally {
      this.isTransitioning = false;
      this.state.isTransitioning = false;
    }
  }

  async navigateToNext(
    gameState: GameState,
    options: NavigationOptions = {}
  ): Promise<boolean> {
    const nextScreen = NavigationOrder.getNextAccessibleScreen(
      this.state.currentScreen,
      gameState
    );
    return this.navigateTo(nextScreen, gameState, options);
  }

  async navigateToPrevious(
    gameState: GameState,
    options: NavigationOptions = {}
  ): Promise<boolean> {
    const prevScreen = NavigationOrder.getPreviousAccessibleScreen(
      this.state.currentScreen,
      gameState
    );
    return this.navigateTo(prevScreen, gameState, options);
  }

  canNavigateTo(screen: ScreenType, gameState: GameState): boolean {
    return NavigationOrder.isScreenAccessible(screen, gameState);
  }

  // State access methods
  getCurrentScreen(): ScreenType {
    return this.state.currentScreen;
  }

  getPreviousScreen(): ScreenType | undefined {
    return this.state.previousScreen;
  }

  getNavigationState(): NavigationState {
    return { ...this.state };
  }

  getHistory(): ScreenType[] {
    return [...this.state.history];
  }

  // History navigation
  canGoBack(): boolean {
    return this.state.history.length > 1;
  }

  async goBack(
    gameState: GameState,
    options: NavigationOptions = {}
  ): Promise<boolean> {
    if (!this.canGoBack()) {
      return false;
    }

    const previousScreen = this.state.history[this.state.history.length - 2];
    if (
      await this.navigateTo(previousScreen, gameState, {
        ...options,
        preserveHistory: true,
      })
    ) {
      this.state.history.pop();
      return true;
    }
    return false;
  }

  // Reset navigation state
  reset(): void {
    this.state = {
      currentScreen: ScreenType.RegionMap,
      previousScreen: undefined,
      history: [ScreenType.RegionMap],
      isTransitioning: false,
    };
  }
}
