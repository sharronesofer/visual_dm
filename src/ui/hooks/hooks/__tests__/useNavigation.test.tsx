import { renderHook, act } from '@testing-library/react-hooks';
import { useNavigation } from '../useNavigation';
import { NavigationManager } from '../../utils/navigationManager';
import { ScreenType } from '../../utils/screenNavigation';
import { GameState } from '../../types/navigation';

describe('useNavigation', () => {
  beforeEach(() => {
    // Reset NavigationManager singleton
    (NavigationManager as any).instance = undefined;
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useNavigation());

    expect(result.current.currentScreen).toBe(ScreenType.RegionMap);
    expect(result.current.previousScreen).toBeUndefined();
    expect(result.current.history).toEqual([ScreenType.RegionMap]);
    expect(result.current.isTransitioning).toBe(false);
  });

  it('navigates to next screen', async () => {
    const { result } = renderHook(() => useNavigation());

    const gameState: GameState = {
      currentLocation: { hasPOI: true },
      party: { members: ['member1'] },
      inventory: { hasItems: true },
    };

    await act(async () => {
      result.current.updateGameState(gameState);
      await result.current.navigateToNext();
    });

    expect(result.current.currentScreen).toBe(ScreenType.POI);
    expect(result.current.previousScreen).toBe(ScreenType.RegionMap);
  });

  it('navigates to previous screen', async () => {
    const { result } = renderHook(() => useNavigation());

    await act(async () => {
      await result.current.navigateTo(ScreenType.Settings);
      await result.current.navigateToPrevious();
    });

    expect(result.current.currentScreen).toBe(ScreenType.CharacterSheet);
    expect(result.current.previousScreen).toBe(ScreenType.Settings);
  });

  it('updates game state and accessibility', async () => {
    const { result } = renderHook(() => useNavigation());

    expect(result.current.canNavigateTo(ScreenType.POI)).toBe(false);

    await act(async () => {
      result.current.updateGameState({
        currentLocation: { hasPOI: true },
      });
    });

    expect(result.current.canNavigateTo(ScreenType.POI)).toBe(true);
  });

  it('maintains navigation history', async () => {
    const { result } = renderHook(() => useNavigation());

    const gameState: GameState = {
      currentLocation: { hasPOI: true },
      party: { members: ['member1'] },
      inventory: { hasItems: true },
    };

    await act(async () => {
      result.current.updateGameState(gameState);
      await result.current.navigateToNext();
      await result.current.navigateToNext();
    });

    expect(result.current.history).toEqual([
      ScreenType.RegionMap,
      ScreenType.POI,
      ScreenType.Party,
    ]);
  });

  it('handles transition states', async () => {
    const { result } = renderHook(() => useNavigation());

    await act(async () => {
      const promise = result.current.navigateTo(ScreenType.Settings, {
        animate: true,
      });
      expect(result.current.isTransitioning).toBe(true);
      await promise;
    });

    expect(result.current.isTransitioning).toBe(false);
  });

  it('prevents navigation to inaccessible screens', async () => {
    const { result } = renderHook(() => useNavigation());
    let success = false;

    await act(async () => {
      success = await result.current.navigateTo(ScreenType.POI);
    });

    expect(success).toBe(false);
    expect(result.current.currentScreen).toBe(ScreenType.RegionMap);
  });

  it('returns accessible screens', async () => {
    const { result } = renderHook(() => useNavigation());

    await act(async () => {
      result.current.updateGameState({
        currentLocation: { hasPOI: true },
        party: { members: ['member1'] },
        inventory: { hasItems: false },
      });
    });

    const accessibleScreens = result.current.getAccessibleScreens();
    expect(accessibleScreens).toContain(ScreenType.RegionMap);
    expect(accessibleScreens).toContain(ScreenType.POI);
    expect(accessibleScreens).toContain(ScreenType.Party);
    expect(accessibleScreens).not.toContain(ScreenType.Equipment);
  });
});
