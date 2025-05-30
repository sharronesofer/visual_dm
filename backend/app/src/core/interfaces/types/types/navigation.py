from typing import Any, List, Union


class GameState:
    currentLocation?: {
    hasPOI: bool
    poiId?: str
  party?: {
    members: List[string]
  }
  inventory?: {
    hasItems: bool
  }
}
class NavigationState:
    currentScreen: ScreenType
    previousScreen?: ScreenType
    history: List[ScreenType]
    isTransitioning: bool
class NavigationOptions:
    animate?: bool
    skipAccessibilityCheck?: bool
    preserveHistory?: bool
NavigationDirection = Union['next', 'previous', 'specific']