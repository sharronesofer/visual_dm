import { useState, useEffect, useCallback } from 'react';
import { NavigationManager } from '../utils/navigationManager';
import { ScreenType } from '../utils/screenNavigation';
import {
  NavigationState,
  NavigationOptions,
  GameState,
} from '../types/navigation';

export function useNavigation() {
  const navigationManager = NavigationManager.getInstance();
  const [navigationState, setNavigationState] = useState<NavigationState>(
    navigationManager.getNavigationState()
  );

  useEffect(() => {
    // Re-render when navigation state changes
    const interval = setInterval(() => {
      const newState = navigationManager.getNavigationState();
      if (JSON.stringify(newState) !== JSON.stringify(navigationState)) {
        setNavigationState(newState);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [navigationState]);

  const navigateToNext = useCallback(async (options?: NavigationOptions) => {
    const success = await navigationManager.navigateToNext(options);
    if (success) {
      setNavigationState(navigationManager.getNavigationState());
    }
    return success;
  }, []);

  const navigateToPrevious = useCallback(
    async (options?: NavigationOptions) => {
      const success = await navigationManager.navigateToPrevious(options);
      if (success) {
        setNavigationState(navigationManager.getNavigationState());
      }
      return success;
    },
    []
  );

  const navigateTo = useCallback(
    async (screen: ScreenType, options?: NavigationOptions) => {
      const success = await navigationManager.navigateTo(screen, options);
      if (success) {
        setNavigationState(navigationManager.getNavigationState());
      }
      return success;
    },
    []
  );

  const updateGameState = useCallback((newState: Partial<GameState>) => {
    navigationManager.updateGameState(newState);
    setNavigationState(navigationManager.getNavigationState());
  }, []);

  return {
    currentScreen: navigationState.currentScreen,
    previousScreen: navigationState.previousScreen,
    history: navigationState.history,
    isTransitioning: navigationState.isTransitioning,
    navigateToNext,
    navigateToPrevious,
    navigateTo,
    updateGameState,
    canNavigateTo: navigationManager.canNavigateTo.bind(navigationManager),
    getAccessibleScreens:
      navigationManager.getAccessibleScreens.bind(navigationManager),
  };
}
