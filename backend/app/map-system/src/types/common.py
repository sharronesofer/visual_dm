from typing import Any, Union


Position = {
  x: float
  y: float
}
Dimensions = {
  width: float
  height: float
}
Range = {
  start: Position
  end: Position
}
TerrainType = Union[, 'plains', 'forest', 'mountain', 'water', 'desert', 'swamp']
VisibilityState = Union[, 'visible', 'discovered', 'hidden']
MovementType = Union[, 'walk', 'swim', 'fly']
FactionAffiliation = Union[, 'neutral', 'friendly', 'hostile', 'unknown']
Direction = Union[, 'north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest'] 