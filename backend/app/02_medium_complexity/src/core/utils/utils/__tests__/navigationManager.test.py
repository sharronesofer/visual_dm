from typing import Any, Dict



describe('NavigationManager', () => {
  let navigationManager: NavigationManager
  let mockGameState: GameState
  beforeEach(() => {
    (NavigationManager as any).instance = undefined
    navigationManager = NavigationManager.getInstance()
    mockGameState = {
      currentLocation: Dict[str, Any],
      party: Dict[str, Any],
      inventory: Dict[str, Any],
    }
  })
  describe('getInstance', () => {
    it('returns singleton instance', () => {
      const instance1 = NavigationManager.getInstance()
      const instance2 = NavigationManager.getInstance()
      expect(instance1).toBe(instance2)
    })
    it('initializes with RegionMap screen', () => {
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.RegionMap)
    })
  })
  describe('navigation methods', () => {
    it('navigates to specified screen', async () => {
      const success = await navigationManager.navigateTo(
        ScreenType.POI,
        mockGameState
      )
      expect(success).toBe(true)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.POI)
      expect(navigationManager.getPreviousScreen()).toBe(ScreenType.RegionMap)
    })
    it('prevents navigation to inaccessible screens', async () => {
      const restrictedGameState: GameState = {
        currentLocation: Dict[str, Any],
        party: Dict[str, Any],
        inventory: Dict[str, Any],
      }
      const success = await navigationManager.navigateTo(
        ScreenType.POI,
        restrictedGameState
      )
      expect(success).toBe(false)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.RegionMap)
    })
    it('navigates to next screen', async () => {
      await navigationManager.navigateToNext(mockGameState)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.POI)
    })
    it('navigates to previous screen', async () => {
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      await navigationManager.navigateToPrevious(mockGameState)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.RegionMap)
    })
    it('maintains navigation history', async () => {
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      await navigationManager.navigateTo(ScreenType.Party, mockGameState)
      const history = navigationManager.getHistory()
      expect(history).toEqual([
        ScreenType.RegionMap,
        ScreenType.POI,
        ScreenType.Party,
      ])
    })
    it('supports going back in history', async () => {
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      await navigationManager.navigateTo(ScreenType.Party, mockGameState)
      expect(navigationManager.canGoBack()).toBe(true)
      const success = await navigationManager.goBack(mockGameState)
      expect(success).toBe(true)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.POI)
    })
    it('prevents going back when at start of history', async () => {
      expect(navigationManager.canGoBack()).toBe(false)
      const success = await navigationManager.goBack(mockGameState)
      expect(success).toBe(false)
    })
  })
  describe('transition handling', () => {
    it('prevents concurrent navigation', async () => {
      const options: NavigationOptions = { animate: true }
      const firstNavigation = navigationManager.navigateTo(
        ScreenType.POI,
        mockGameState,
        options
      )
      const secondNavigation = navigationManager.navigateTo(
        ScreenType.Party,
        mockGameState,
        options
      )
      const [firstResult, secondResult] = await Promise.all([
        firstNavigation,
        secondNavigation,
      ])
      expect(firstResult).toBe(true)
      expect(secondResult).toBe(false)
    })
    it('allows navigation after transition completes', async () => {
      const options: NavigationOptions = { animate: true }
      await navigationManager.navigateTo(
        ScreenType.POI,
        mockGameState,
        options
      )
      const success = await navigationManager.navigateTo(
        ScreenType.Party,
        mockGameState,
        options
      )
      expect(success).toBe(true)
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.Party)
    })
  })
  describe('event handling', () => {
    it('emits navigation events', async () => {
      const beforeNavigate = jest.fn()
      const afterNavigate = jest.fn()
      const navigationBlocked = jest.fn()
      navigationManager.addEventListener('beforeNavigate', beforeNavigate)
      navigationManager.addEventListener('afterNavigate', afterNavigate)
      navigationManager.addEventListener(
        'navigationBlocked',
        navigationBlocked
      )
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      expect(beforeNavigate).toHaveBeenCalledWith(
        ScreenType.RegionMap,
        ScreenType.POI,
        expect.any(Object)
      )
      expect(afterNavigate).toHaveBeenCalledWith(
        ScreenType.RegionMap,
        ScreenType.POI,
        expect.any(Object)
      )
      expect(navigationBlocked).not.toHaveBeenCalled()
    })
    it('emits navigationBlocked event for inaccessible screens', async () => {
      const navigationBlocked = jest.fn()
      navigationManager.addEventListener(
        'navigationBlocked',
        navigationBlocked
      )
      const restrictedGameState: GameState = {
        currentLocation: Dict[str, Any],
        party: Dict[str, Any],
        inventory: Dict[str, Any],
      }
      await navigationManager.navigateTo(ScreenType.POI, restrictedGameState)
      expect(navigationBlocked).toHaveBeenCalledWith(
        ScreenType.RegionMap,
        ScreenType.POI,
        expect.any(Object)
      )
    })
    it('removes event listeners', async () => {
      const beforeNavigate = jest.fn()
      navigationManager.addEventListener('beforeNavigate', beforeNavigate)
      navigationManager.removeEventListener('beforeNavigate', beforeNavigate)
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      expect(beforeNavigate).not.toHaveBeenCalled()
    })
  })
  describe('reset', () => {
    it('resets navigation state', async () => {
      await navigationManager.navigateTo(ScreenType.POI, mockGameState)
      await navigationManager.navigateTo(ScreenType.Party, mockGameState)
      navigationManager.reset()
      expect(navigationManager.getCurrentScreen()).toBe(ScreenType.RegionMap)
      expect(navigationManager.getPreviousScreen()).toBeUndefined()
      expect(navigationManager.getHistory()).toEqual([ScreenType.RegionMap])
      expect(navigationManager.canGoBack()).toBe(false)
    })
  })
})