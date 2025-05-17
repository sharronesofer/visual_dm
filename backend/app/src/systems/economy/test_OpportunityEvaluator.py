import pytest
import time
from .OpportunityEvaluator import OpportunityEvaluator
from .EconomicTypes import EconomicAgent
from .RiskAssessor import RiskToleranceProfile

class DummyAgent:
    def __init__(self, id='a1'):
        self.id = id
        self.role = None
        self.inventory = {}
        self.currency = 1000
        self.reputation = 50
        self.activeOffers = set()
        self.productionQueue = []
        self.lastTransaction = 0

def test_score_opportunity_high_profit_low_risk():
    agent = DummyAgent()
    evaluator = OpportunityEvaluator(agent)
    opp = {
        'profit': 100,
        'transaction': {'itemType': 'FOOD', 'size': 10},
        'goal_tags': ['trade'],
        'expires_at': time.time() + 3600
    }
    score = evaluator.score_opportunity(opp, agent_goals=['trade'])
    assert score > 80

def test_score_opportunity_high_risk():
    agent = DummyAgent()
    evaluator = OpportunityEvaluator(agent)
    # Force high risk by using a large transaction size
    opp = {
        'profit': 50,
        'transaction': {'itemType': 'FOOD', 'size': 100},
        'goal_tags': ['explore'],
        'expires_at': time.time() + 3600
    }
    score = evaluator.score_opportunity(opp, agent_goals=['trade'])
    assert score < 70

def test_score_opportunity_time_decay():
    agent = DummyAgent()
    evaluator = OpportunityEvaluator(agent)
    now = time.time()
    opp_fresh = {
        'profit': 50,
        'transaction': {'itemType': 'FOOD', 'size': 10},
        'goal_tags': ['trade'],
        'expires_at': now + 3600 * 10
    }
    opp_expiring = {
        'profit': 50,
        'transaction': {'itemType': 'FOOD', 'size': 10},
        'goal_tags': ['trade'],
        'expires_at': now + 60
    }
    score_fresh = evaluator.score_opportunity(opp_fresh, current_time=now, agent_goals=['trade'])
    score_expiring = evaluator.score_opportunity(opp_expiring, current_time=now, agent_goals=['trade'])
    assert score_fresh > score_expiring

def test_rank_opportunities():
    agent = DummyAgent()
    evaluator = OpportunityEvaluator(agent)
    now = time.time()
    opps = [
        {'profit': 10, 'transaction': {'itemType': 'FOOD', 'size': 10}, 'goal_tags': ['a'], 'expires_at': now + 3600},
        {'profit': 100, 'transaction': {'itemType': 'FOOD', 'size': 10}, 'goal_tags': ['b'], 'expires_at': now + 3600},
        {'profit': 50, 'transaction': {'itemType': 'FOOD', 'size': 10}, 'goal_tags': ['a'], 'expires_at': now + 3600}
    ]
    ranked = evaluator.rank_opportunities(opps, current_time=now, agent_goals=['a'])
    assert ranked[0]['profit'] == 100 or ranked[0]['goal_tags'] == ['a'] 