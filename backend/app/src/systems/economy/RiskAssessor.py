import enum
from typing import Dict, Any, Optional, Union
from .EconomicTypes import EconomicAgent, ResourceType, ProductType, TradeOffer

class RiskToleranceProfile(enum.Enum):
    CONSERVATIVE = 'conservative'
    MODERATE = 'moderate'
    AGGRESSIVE = 'aggressive'

class RiskAssessor:
    def __init__(self, agent: EconomicAgent, profile: Optional[RiskToleranceProfile] = None):
        self.agent = agent
        self.profile = profile or self._infer_profile_from_agent()

    def _infer_profile_from_agent(self) -> RiskToleranceProfile:
        # Placeholder: infer from agent attributes, fallback to MODERATE
        return RiskToleranceProfile.MODERATE

    def calculate_risk_score(
        self,
        transaction: Dict[str, Any],
        market_volatility: float = 0.0,
        counterparty_reliability: float = 1.0,
        resource_levels: Optional[Dict[Union[ResourceType, ProductType], float]] = None
    ) -> float:
        """
        Calculates a normalized risk score (0-100) for a potential transaction.
        :param transaction: Dict with transaction details (type, size, etc.)
        :param market_volatility: Float (0-1), higher means more volatile
        :param counterparty_reliability: Float (0-1), higher means more reliable
        :param resource_levels: Optional dict of agent's current resources
        :return: Risk score (0 = no risk, 100 = max risk)
        """
        base_risk = self._base_risk_from_profile()
        size_factor = min(1.0, transaction.get('size', 1.0) / 100.0)
        volatility_factor = market_volatility
        reliability_factor = 1.0 - counterparty_reliability
        resource_factor = self._resource_risk_factor(transaction, resource_levels)

        # Increase resource factor and base risk impact
        risk = (
            0.4 * base_risk +
            0.05 * size_factor * 100 +
            0.15 * volatility_factor * 100 +
            0.05 * reliability_factor * 100 +
            0.5 * resource_factor * 100
        )
        return max(0.0, min(100.0, risk))

    def _base_risk_from_profile(self) -> float:
        if self.profile == RiskToleranceProfile.CONSERVATIVE:
            return 100.0
        elif self.profile == RiskToleranceProfile.MODERATE:
            return 50.0
        elif self.profile == RiskToleranceProfile.AGGRESSIVE:
            return 0.0
        return 50.0

    def _resource_risk_factor(self, transaction: Dict[str, Any], resource_levels: Optional[Dict[Union[ResourceType, ProductType], float]]) -> float:
        if not resource_levels or 'itemType' not in transaction:
            return 0.5  # Neutral if unknown
        item = transaction['itemType']
        required = transaction.get('size', 1.0)
        available = resource_levels.get(item, 0.0)
        if available == 0:
            return 1.0  # High risk if agent has none
        ratio = required / available
        if ratio >= 1.0:
            return 1.0  # High risk if using all or more than available
        elif ratio >= 0.5:
            return 0.95
        elif ratio >= 0.2:
            return 0.8
        else:
            return 0.1  # Low risk if plenty available

    def get_risk_profile(self) -> RiskToleranceProfile:
        return self.profile

    def set_risk_profile(self, profile: RiskToleranceProfile):
        self.profile = profile 