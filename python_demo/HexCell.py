from typing import Union, List, Tuple, Optional


TerrainType = Union['plains', 'forest', 'mountain', 'water', 'desert', 'urban']
WeatherType = Union['clear', 'rain', 'snow', 'fog', 'storm', 'windy']


class HexCell:
    """Class representing a hexagonal cell in a grid."""

    def __init__(
        self,
        q: float,
        r: float,
        terrain: TerrainType = 'plains',
        weather: WeatherType = 'clear',
        elevation: float = 0,
        moisture: float = 0.5,
        temperature: float = 0.5
    ):
        self._q = q
        self._r = r
        self._terrain = terrain
        self._weather = weather
        self._elevation = elevation
        self._moisture = moisture
        self._temperature = temperature
        self._is_discovered = False
        self._has_feature = False
        self._feature_type = None

    @property
    def q(self) -> float:
        return self._q

    @property
    def r(self) -> float:
        return self._r

    @property
    def terrain(self) -> TerrainType:
        return self._terrain

    @terrain.setter
    def terrain(self, value: TerrainType):
        self._terrain = value

    @property
    def weather(self) -> WeatherType:
        return self._weather

    @weather.setter
    def weather(self, value: WeatherType):
        self._weather = value

    @property
    def elevation(self) -> float:
        return self._elevation

    @elevation.setter
    def elevation(self, value: float):
        self._elevation = value

    @property
    def moisture(self) -> float:
        return self._moisture

    @moisture.setter
    def moisture(self, value: float):
        self._moisture = value

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        self._temperature = value

    @property
    def is_discovered(self) -> bool:
        return self._is_discovered

    @is_discovered.setter
    def is_discovered(self, value: bool):
        self._is_discovered = value

    @property
    def has_feature(self) -> bool:
        return self._has_feature

    @property
    def feature_type(self) -> Optional[str]:
        return self._feature_type

    def add_feature(self, feature_type: str) -> None:
        self._has_feature = True
        self._feature_type = feature_type

    def remove_feature(self) -> None:
        self._has_feature = False
        self._feature_type = None

    def get_cost(self) -> float:
        cost = 1.0

        # Apply terrain factors
        if self._terrain == 'plains':
            cost = 1.0
        elif self._terrain == 'forest':
            cost = 1.5
        elif self._terrain == 'mountain':
            cost = 3.0
        elif self._terrain == 'water':
            cost = 2.0
        elif self._terrain == 'desert':
            cost = 1.8
        elif self._terrain == 'urban':
            cost = 1.2

        # Apply weather factors
        if self._weather == 'rain' or self._weather == 'fog':
            cost *= 1.2
        elif self._weather == 'snow' or self._weather == 'storm':
            cost *= 1.5

        # Apply elevation factor
        cost *= (1.0 + self._elevation * 0.1)

        return cost

    def is_adjacent(self, other: 'HexCell') -> bool:
        dx = self._q - other.q
        dy = self._r - other.r
        return (abs(dx) <= 1 and abs(dy) <= 1 and abs(dx + dy) <= 1)

    def get_neighbor_coordinates(self) -> List[Tuple[float, float]]:
        return [
            (self._q + 1, self._r),
            (self._q, self._r + 1),
            (self._q - 1, self._r + 1),
            (self._q - 1, self._r),
            (self._q, self._r - 1),
            (self._q + 1, self._r - 1)
        ]

    def equals(self, other: 'HexCell') -> bool:
        return self._q == other.q and self._r == other.r

    def __str__(self) -> str:
        return f"HexCell({self._q},{self._r},{self._terrain})"
