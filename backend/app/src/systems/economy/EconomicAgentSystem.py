from typing import Any, List
from .RiskAssessor import RiskAssessor, RiskToleranceProfile
from .OpportunityEvaluator import OpportunityEvaluator
from .GoalManager import GoalManager, Goal
from .EconomicTypes import EconomicAgent, EconomicRole, ResourceType, ProductType, ProductionRecipe, TradeOffer, Transaction

class EconomicAgentSystem:
    def __init__(self, market_system, spatial_grid):
        self.agents = {}
        self.market_system = market_system
        self.spatial_grid = spatial_grid
        self.TRADE_SEARCH_RADIUS = 50
        self.PRODUCTION_CHECK_INTERVAL = 5000
        self.TRADE_CHECK_INTERVAL = 10000
        self.goal_managers = {}  # agent_id -> GoalManager
        # Optionally: start production/trading loops if needed

    def initialize_agent(self, npc, role: EconomicRole):
        agent = EconomicAgent(
            id=npc.id,
            role=role,
            inventory={},
            currency=1000,
            reputation=50,
            activeOffers=set(),
            productionQueue=[],
            lastTransaction=0
        )
        self.agents[agent.id] = agent
        self.goal_managers[agent.id] = GoalManager(agent.id)

    def evaluate_transaction_risk(self, agent_id: str, transaction: dict, market_volatility: float = 0.0, counterparty_reliability: float = 1.0) -> float:
        """
        Evaluate the risk score for a given agent and transaction using the RiskAssessor.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return 100.0  # Max risk if agent not found
        resource_levels = getattr(agent, 'inventory', None)
        risk_assessor = RiskAssessor(agent)
        return risk_assessor.calculate_risk_score(
            transaction=transaction,
            market_volatility=market_volatility,
            counterparty_reliability=counterparty_reliability,
            resource_levels=resource_levels
        )

    def make_decision(self, agent_id: str, opportunities: list, env_factors: dict = None) -> dict:
        """
        Main decision-making method for an agent.
        - Uses goals, opportunity evaluation, and risk assessment.
        - Returns the selected opportunity and reasoning.
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return {'decision': None, 'reason': 'Agent not found'}
        goal_manager = self.goal_managers.get(agent_id)
        if not goal_manager:
            return {'decision': None, 'reason': 'No goal manager'}
        # Adjust goals based on environment
        if env_factors:
            goal_manager.adjust_goals_based_on_environment(env_factors)
        current_goals = goal_manager.get_active_goals()
        agent_goals = [g.name for g in current_goals]
        # Evaluate opportunities
        evaluator = OpportunityEvaluator(agent)
        ranked = evaluator.rank_opportunities(opportunities, agent_goals=agent_goals)
        # Filter by risk
        risk_assessor = RiskAssessor(agent)
        for opp in ranked:
            risk = risk_assessor.calculate_risk_score(opp.get('transaction', {}))
            if risk < 70:  # Acceptable risk threshold
                # Update goal progress/satisfaction (simple example)
                for g in current_goals:
                    if g.name in opp.get('goal_tags', []):
                        goal_manager.update_goal_progress(g.name, min(1.0, g.progress + 0.2))
                        goal_manager.update_goal_satisfaction(g.name, min(1.0, g.satisfaction + 0.2))
                return {'decision': opp, 'reason': f'Best opportunity with risk {risk:.1f}'}
        return {'decision': None, 'reason': 'No acceptable opportunities'}

    def start_production(self, agent_id, recipe_id):
        agent = self.agents.get(agent_id)
        if not agent or not agent.role.productionRecipes:
            return False
        recipe = next((r for r in agent.role.productionRecipes if r.output.type == recipe_id), None)
        if not recipe:
            return False
        if not self.has_required_resources(agent, recipe):
            return False
        self.consume_resources(agent, recipe)
        agent.productionQueue.append({
            'recipeId': recipe_id,
            'startedAt': time.time(),
            'completesAt': time.time() + recipe.productionTime,
            'inputs': recipe.inputs
        })
        return True

    def create_trade_offer(self, agent_id, item_type, quantity, price_per_unit):
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        current_quantity = agent.inventory.get(item_type) or 0
        if current_quantity < quantity:
            return None
        offer_id = self.market_system.create_offer(agent_id, item_type, quantity, price_per_unit)
        if offer_id:
            agent.activeOffers.add(offer_id)
            agent.inventory.set(item_type, current_quantity - quantity)
        return offer_id

    def execute_trade(self, buyer_id, offer_id, quantity, market_id=None):
        buyer = self.agents.get(buyer_id)
        if not buyer:
            return False
        transaction = self.market_system.execute_trade(offer_id, buyer_id, quantity, market_id)
        if transaction:
            seller = self.agents.get(transaction.sellerId)
            if seller:
                buyer.currency -= transaction.pricePerUnit * quantity
                self.add_to_inventory(buyer, transaction.itemType, quantity)
                buyer.lastTransaction = transaction.timestamp
                seller.currency += transaction.pricePerUnit * quantity
                seller.lastTransaction = transaction.timestamp
                seller.activeOffers.delete(offer_id)
                return True
        return False

    def find_best_offers(self, agent_id, item_type, max_price):
        agent = self.agents.get(agent_id)
        if not agent:
            return []
        nearby_agents = self.spatial_grid.get_entities_in_range(agent_id, self.TRADE_SEARCH_RADIUS)
        relevant_offers = []
        for nearby_agent_id in nearby_agents:
            nearby_agent = self.agents.get(nearby_agent_id)
            if nearby_agent:
                for offer_id in nearby_agent.activeOffers:
                    offer = self.market_system.get_offer(offer_id)
                    if offer and offer.itemType == item_type and offer.pricePerUnit <= max_price:
                        relevant_offers.append(offer)
        return sorted(relevant_offers, key=lambda o: o.pricePerUnit)

    def update_reputation(self, agent_id, change_amount):
        agent = self.agents.get(agent_id)
        if agent:
            agent.reputation = max(0, min(100, agent.reputation + change_amount))

    def has_required_resources(self, agent, recipe):
        for resource, amount in recipe.inputs:
            available = agent.inventory.get(resource) or 0
            if available < amount:
                return False
        return True

    def consume_resources(self, agent, recipe):
        for resource, amount in recipe.inputs:
            available = agent.inventory.get(resource) or 0
            agent.inventory.set(resource, available - amount)

    def add_to_inventory(self, agent, item_type, quantity):
        current = agent.inventory.get(item_type) or 0
        agent.inventory.set(item_type, current + quantity)

    def start_production_loop(self):
        set_interval(lambda: [self.check_production(agent) for agent in self.agents.values()], self.PRODUCTION_CHECK_INTERVAL)

    def check_production(self, agent):
        now = time.time()
        completed_productions = [p for p in agent.productionQueue if p['completesAt'] <= now]
        for production in completed_productions:
            recipe = next((r for r in agent.role.productionRecipes if r.output.type == production['recipeId']), None)
            if recipe:
                success = random() > recipe.failureChance
                if success:
                    self.add_to_inventory(agent, recipe.output.type, recipe.output.quantity)
            agent.productionQueue = [p for p in agent.productionQueue if p != production]

    def start_trading_loop(self):
        set_interval(lambda: [self.check_trading(agent) for agent in self.agents.values()], self.TRADE_CHECK_INTERVAL)

    def check_trading(self, agent):
        if not agent.role.tradingPreferences:
            return
        {preferred_resources, preferred_products, price_markup} = agent.role.tradingPreferences
        for item_type, quantity in agent.inventory.items():
            if quantity > 0:
                base_price = self.get_base_price(item_type)
                selling_price = base_price * (1 + price_markup)
                if agent.activeOffers.size < 5 and (
                    item_type in preferred_resources or
                    item_type in preferred_products
                ):
                    self.create_trade_offer(agent.id, item_type, quantity, selling_price)

        desired_items = list(preferred_resources) + list(preferred_products)
        for item_type in desired_items:
            current_quantity = agent.inventory.get(item_type) or 0
            if current_quantity < 10:
                base_price = self.get_base_price(item_type)
                offers = self.find_best_offers(agent.id, item_type, base_price * 1.5)
                for offer in offers:
                    if agent.currency >= offer.pricePerUnit * offer.quantity:
                        self.execute_trade(agent.id, offer.id, offer.quantity)
                        break

    def get_base_price(self, item_type):
        price_data = self.market_system.get_price_stats(item_type)
        return price_data['averagePrice'] if price_data else 100

    def process_trade(self, agent_id, target_id, offer):
        try:
            result = {
                'value': offer['economic']['value'],
                'success': True,
                'items': offer['economic']['items']
            }
            return result
        except Exception as e:
            print('Error processing trade:', e)
            return {
                'value': 0,
                'success': False,
                'error': 'Failed to process trade'
            } 