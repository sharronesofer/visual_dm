from typing import Any, Dict



describe('NavigationOrder', () => {
  describe('getNextScreen', () => {
    test('returns correct next screen in sequence', () => {
      expect(NavigationOrder.getNextScreen(ScreenType.RegionMap)).toBe(
        ScreenType.POI
      )
      expect(NavigationOrder.getNextScreen(ScreenType.POI)).toBe(
        ScreenType.Party
      )
      expect(NavigationOrder.getNextScreen(ScreenType.Party)).toBe(
        ScreenType.Equipment
      )
      expect(NavigationOrder.getNextScreen(ScreenType.Equipment)).toBe(
        ScreenType.CharacterSheet
      )
      expect(NavigationOrder.getNextScreen(ScreenType.CharacterSheet)).toBe(
        ScreenType.Settings
      )
    })
    test('wraps around to first screen after last screen', () => {
      expect(NavigationOrder.getNextScreen(ScreenType.Settings)).toBe(
        ScreenType.RegionMap
      )
    })
    test('returns RegionMap for invalid screen type', () => {
      expect(NavigationOrder.getNextScreen('INVALID' as ScreenType)).toBe(
        ScreenType.RegionMap
      )
    })
  })
  describe('getPreviousScreen', () => {
    test('returns correct previous screen in sequence', () => {
      expect(NavigationOrder.getPreviousScreen(ScreenType.POI)).toBe(
        ScreenType.RegionMap
      )
      expect(NavigationOrder.getPreviousScreen(ScreenType.Party)).toBe(
        ScreenType.POI
      )
      expect(NavigationOrder.getPreviousScreen(ScreenType.Equipment)).toBe(
        ScreenType.Party
      )
      expect(NavigationOrder.getPreviousScreen(ScreenType.CharacterSheet)).toBe(
        ScreenType.Equipment
      )
      expect(NavigationOrder.getPreviousScreen(ScreenType.Settings)).toBe(
        ScreenType.CharacterSheet
      )
    })
    test('wraps around to last screen from first screen', () => {
      expect(NavigationOrder.getPreviousScreen(ScreenType.RegionMap)).toBe(
        ScreenType.Settings
      )
    })
    test('returns RegionMap for invalid screen type', () => {
      expect(NavigationOrder.getPreviousScreen('INVALID' as ScreenType)).toBe(
        ScreenType.RegionMap
      )
    })
  })
  describe('isScreenAccessible', () => {
    test('POI screen accessibility depends on currentLocation.hasPOI', () => {
      const gameState = { currentLocation: Dict[str, Any] }
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.POI, gameState)
      ).toBe(true)
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.POI, {
          currentLocation: Dict[str, Any],
        })
      ).toBe(false)
    })
    test('Party screen accessibility depends on party members', () => {
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.Party, {
          party: Dict[str, Any],
        })
      ).toBe(true)
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.Party, {
          party: Dict[str, Any],
        })
      ).toBe(false)
    })
    test('Equipment screen accessibility depends on inventory', () => {
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.Equipment, {
          inventory: Dict[str, Any],
        })
      ).toBe(true)
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.Equipment, {
          inventory: Dict[str, Any],
        })
      ).toBe(false)
    })
    test('other screens are always accessible', () => {
      const emptyGameState = {}
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.RegionMap, emptyGameState)
      ).toBe(true)
      expect(
        NavigationOrder.isScreenAccessible(
          ScreenType.CharacterSheet,
          emptyGameState
        )
      ).toBe(true)
      expect(
        NavigationOrder.isScreenAccessible(ScreenType.Settings, emptyGameState)
      ).toBe(true)
    })
  })
  describe('getNextAccessibleScreen', () => {
    test('skips inaccessible screens', () => {
      const mockGameState = {
        currentLocation: Dict[str, Any],
        party: Dict[str, Any],
        inventory: Dict[str, Any],
      }
      expect(
        NavigationOrder.getNextAccessibleScreen(
          ScreenType.RegionMap,
          mockGameState
        )
      ).toBe(ScreenType.Equipment)
    })
    test('returns next screen if accessible', () => {
      const mockGameState = {
        currentLocation: Dict[str, Any],
        party: Dict[str, Any],
        inventory: Dict[str, Any],
      }
      expect(
        NavigationOrder.getNextAccessibleScreen(
          ScreenType.RegionMap,
          mockGameState
        )
      ).toBe(ScreenType.POI)
    })
    test('handles case where no screens are accessible', () => {
      const mockGameState = {
        currentLocation: Dict[str, Any],
        party: Dict[str, Any],
        inventory: Dict[str, Any],
      }
      expect(
        NavigationOrder.getNextAccessibleScreen(
          ScreenType.RegionMap,
          mockGameState
        )
      ).toBe(ScreenType.RegionMap)
    })
  })
})