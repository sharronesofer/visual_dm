from typing import Any, Union


class PriceStats:
    average: float
    min: float
    max: float
    trend: Union['rising', 'falling', 'stable']
    volatility: float
    lastUpdate: float 