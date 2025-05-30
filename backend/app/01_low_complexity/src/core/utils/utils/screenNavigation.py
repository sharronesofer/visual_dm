from typing import Any, List
from enum import Enum



class ScreenType(Enum):
    RegionMap = 'REGION_MAP'
    POI = 'POI'
    Party = 'PARTY'
    Equipment = 'EQUIPMENT'
    CharacterSheet = 'CHARACTER_SHEET'
    Settings = 'SETTINGS'
class NavigationOrder {
  private static readonly ORDER: List[ScreenType] = [
    ScreenType.RegionMap,
    ScreenType.POI,
    ScreenType.Party,
    ScreenType.Equipment,
    ScreenType.CharacterSheet,
    ScreenType.Settings,
  ]
  static getNextScreen(currentScreen: ScreenType): \'ScreenType\' {
    const currentIndex = this.ORDER.indexOf(currentScreen)
    if (currentIndex === -1) return ScreenType.RegionMap 
    const nextIndex = (currentIndex + 1) % this.ORDER.length
    return this.ORDER[nextIndex]
  }
  static getPreviousScreen(currentScreen: ScreenType): \'ScreenType\' {
    const currentIndex = this.ORDER.indexOf(currentScreen)
    if (currentIndex === -1) return ScreenType.RegionMap 
    const previousIndex =
      (currentIndex - 1 + this.ORDER.length) % this.ORDER.length
    return this.ORDER[previousIndex]
  }
  static isScreenAccessible(screen: \'ScreenType\', gameState: Any): bool {
    switch (screen) {
      case ScreenType.POI:
        return gameState.currentLocation?.hasPOI ?? false
      case ScreenType.Party:
        return gameState.party?.members?.length > 0
      case ScreenType.Equipment:
        return gameState.inventory?.hasItems ?? false
      default:
        return true 
    }
  }
  static getNextAccessibleScreen(
    currentScreen: \'ScreenType\',
    gameState: Any
  ): \'ScreenType\' {
    let nextScreen = this.getNextScreen(currentScreen)
    let iterations = 0
    while (
      !this.isScreenAccessible(nextScreen, gameState) &&
      iterations < this.ORDER.length
    ) {
      nextScreen = this.getNextScreen(nextScreen)
      iterations++
    }
    return nextScreen
  }
}