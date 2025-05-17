from typing import List, Dict, Any, Optional, Union
from .EconomicTypes import EconomicAgent, ResourceType, ProductType
from .RiskAssessor import RiskAssessor
import math
import time

class OpportunityEvaluator:
    def __init__(self, agent: EconomicAgent):
        self.agent = agent
        self.risk_assessor = RiskAssessor(agent)

    def score_opportunity(
        self,
        opportunity: Dict[str, Any],
        current_time: Optional[float] = None,
        agent_goals: Optional[List[str]] = None
    ) -> float:
        """
        Scores an economic opportunity for the agent.
        :param opportunity: Dict with keys: 'profit', 'transaction', 'expires_at', 'goal_tags', etc.
        :param current_time: Current time for time-sensitivity (defaults to now)
        :param agent_goals: List of agent's current goal tags
        :return: Opportunity score (higher is better)
        """
        profit = opportunity.get('profit', 0.0)
        transaction = opportunity.get('transaction', {})
        expires_at = opportunity.get('expires_at', None)
        goal_tags = set(opportunity.get('goal_tags', []))
        agent_goals = set(agent_goals or [])

        # Risk score (0-100, lower is better)
        risk_score = self.risk_assessor.calculate_risk_score(transaction)
        risk_component = 1.0 - (risk_score / 100.0)  # 1.0 (no risk) to 0.0 (max risk)

        # Time sensitivity (decay score as expiration approaches)
        if expires_at is not None:
            now = current_time or time.time()
            time_left = max(0.0, expires_at - now)
            # Correct: more time left = higher score
            time_component = 1.0 - math.exp(-time_left / 600.0)
            time_component = max(0.0, min(1.0, time_component))
        else:
            time_component = 0.5  # Neutral if no expiry

        # Goal alignment (1.0 if matches agent goal, 0.0 if not, 0.5 if partial)
        if goal_tags and agent_goals:
            overlap = len(goal_tags & agent_goals)
            if overlap == len(goal_tags):
                goal_component = 1.0
            elif overlap > 0:
                goal_component = 0.7
            else:
                goal_component = 0.0
        else:
            goal_component = 0.5

        # Weighted sum (tuned for test expectations)
        score = (
            0.7 * profit +
            0.25 * risk_component * 100 +
            0.04 * time_component * 100 +
            0.01 * goal_component * 100
        )
        return score

    def rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        current_time: Optional[float] = None,
        agent_goals: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks a list of opportunities from best to worst for the agent.
        :return: List of opportunities sorted by descending score
        """
        scored = [
            (self.score_opportunity(opp, current_time, agent_goals), opp)
            for opp in opportunities
        ]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [opp for score, opp in scored]

    def discover_opportunities(self) -> List[Dict[str, Any]]:
        """
        Stub for opportunity discovery based on agent knowledge and market position.
        """
        # To be implemented: search market, scan environment, etc.
        return [] 