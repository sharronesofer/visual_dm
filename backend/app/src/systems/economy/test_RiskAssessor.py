import pytest
from .RiskAssessor import RiskAssessor, RiskToleranceProfile
from .EconomicTypes import EconomicAgent, ResourceType, ProductType

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

def test_risk_score_conservative_profile():
    agent = DummyAgent()
    assessor = RiskAssessor(agent, profile=RiskToleranceProfile.CONSERVATIVE)
    transaction = {'itemType': ResourceType.FOOD, 'size': 10}
    score = assessor.calculate_risk_score(transaction, market_volatility=0.2, counterparty_reliability=0.8, resource_levels={ResourceType.FOOD: 100})
    assert 60 <= score <= 100

def test_risk_score_aggressive_profile():
    agent = DummyAgent()
    assessor = RiskAssessor(agent, profile=RiskToleranceProfile.AGGRESSIVE)
    transaction = {'itemType': ResourceType.WOOD, 'size': 10}
    score = assessor.calculate_risk_score(transaction, market_volatility=0.1, counterparty_reliability=0.95, resource_levels={ResourceType.WOOD: 100})
    assert 20 <= score <= 60

def test_risk_score_high_volatility():
    agent = DummyAgent()
    assessor = RiskAssessor(agent)
    transaction = {'itemType': ResourceType.STONE, 'size': 10}
    score = assessor.calculate_risk_score(transaction, market_volatility=1.0, counterparty_reliability=1.0, resource_levels={ResourceType.STONE: 100})
    assert score > 50

def test_risk_score_low_resources():
    agent = DummyAgent()
    assessor = RiskAssessor(agent)
    transaction = {'itemType': ResourceType.METAL, 'size': 50}
    score = assessor.calculate_risk_score(transaction, market_volatility=0.0, counterparty_reliability=1.0, resource_levels={ResourceType.METAL: 10})
    assert score > 80

def test_risk_score_missing_resource_info():
    agent = DummyAgent()
    assessor = RiskAssessor(agent)
    transaction = {'itemType': ResourceType.CLOTH, 'size': 10}
    score = assessor.calculate_risk_score(transaction, market_volatility=0.0, counterparty_reliability=1.0, resource_levels=None)
    assert 0 <= score <= 100 