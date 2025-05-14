export enum ScreenType {
  RegionMap = 'REGION_MAP',
  POI = 'POI',
  Party = 'PARTY',
  Equipment = 'EQUIPMENT',
  CharacterSheet = 'CHARACTER_SHEET',
  Settings = 'SETTINGS',
}

export class NavigationOrder {
  private static readonly ORDER: ScreenType[] = [
    ScreenType.RegionMap,
    ScreenType.POI,
    ScreenType.Party,
    ScreenType.Equipment,
    ScreenType.CharacterSheet,
    ScreenType.Settings,
  ];

  // Get next screen with circular wrap-around
  static getNextScreen(currentScreen: ScreenType): ScreenType {
    const currentIndex = this.ORDER.indexOf(currentScreen);
    if (currentIndex === -1) return ScreenType.RegionMap; // Default fallback
    const nextIndex = (currentIndex + 1) % this.ORDER.length;
    return this.ORDER[nextIndex];
  }

  // Get previous screen with circular wrap-around
  static getPreviousScreen(currentScreen: ScreenType): ScreenType {
    const currentIndex = this.ORDER.indexOf(currentScreen);
    if (currentIndex === -1) return ScreenType.RegionMap; // Default fallback
    const previousIndex =
      (currentIndex - 1 + this.ORDER.length) % this.ORDER.length;
    return this.ORDER[previousIndex];
  }

  // Check if screen is accessible based on game state
  static isScreenAccessible(screen: ScreenType, gameState: any): boolean {
    switch (screen) {
      case ScreenType.POI:
        return gameState.currentLocation?.hasPOI ?? false;
      case ScreenType.Party:
        return gameState.party?.members?.length > 0;
      case ScreenType.Equipment:
        return gameState.inventory?.hasItems ?? false;
      default:
        return true; // Other screens always accessible
    }
  }

  // Get next accessible screen
  static getNextAccessibleScreen(
    currentScreen: ScreenType,
    gameState: any
  ): ScreenType {
    let nextScreen = this.getNextScreen(currentScreen);
    let iterations = 0;
    while (
      !this.isScreenAccessible(nextScreen, gameState) &&
      iterations < this.ORDER.length
    ) {
      nextScreen = this.getNextScreen(nextScreen);
      iterations++;
    }
    return nextScreen;
  }
}
