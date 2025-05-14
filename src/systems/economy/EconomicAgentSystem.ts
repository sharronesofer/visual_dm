import { v4 as uuidv4 } from 'uuid';
import {
  EconomicAgent,
  EconomicRole,
  ResourceType,
  ProductType,
  ProductionRecipe,
  TradeOffer,
  Transaction
} from './EconomicTypes';
import { MarketSystem } from './MarketSystem';
import { NPCData } from '../../types/npc/npc';
import { SpatialGrid } from '../../utils/SpatialGrid';

export class EconomicAgentSystem {
  private agents: Map<string, EconomicAgent>;
  private marketSystem: MarketSystem;
  private spatialGrid: SpatialGrid;
  private readonly TRADE_SEARCH_RADIUS = 50;
  private readonly PRODUCTION_CHECK_INTERVAL = 5000; // 5 seconds
  private readonly TRADE_CHECK_INTERVAL = 10000; // 10 seconds

  constructor(marketSystem: MarketSystem, spatialGrid: SpatialGrid) {
    this.agents = new Map();
    this.marketSystem = marketSystem;
    this.spatialGrid = spatialGrid;
    this.startProductionLoop();
    this.startTradingLoop();
  }

  /**
   * Initialize a new economic agent for an NPC
   */
  public initializeAgent(npc: NPCData, role: EconomicRole): void {
    const agent: EconomicAgent = {
      id: npc.id,
      role,
      inventory: new Map(),
      currency: 1000, // Starting currency
      reputation: 50, // Neutral starting reputation
      activeOffers: new Set(),
      productionQueue: [],
      lastTransaction: 0
    };

    this.agents.set(agent.id, agent);
  }

  /**
   * Start production for an agent if they have available recipes
   */
  public startProduction(agentId: string, recipeId: string): boolean {
    const agent = this.agents.get(agentId);
    if (!agent || !agent.role.productionRecipes) return false;

    const recipe = agent.role.productionRecipes.find(r => r.output.type === recipeId);
    if (!recipe) return false;

    // Check if agent has required resources
    if (!this.hasRequiredResources(agent, recipe)) return false;

    // Consume resources and start production
    this.consumeResources(agent, recipe);
    agent.productionQueue.push({
      recipeId,
      startedAt: Date.now(),
      completesAt: Date.now() + recipe.productionTime,
      inputs: recipe.inputs
    });

    return true;
  }

  /**
   * Create a trade offer for an agent
   */
  public createTradeOffer(
    agentId: string,
    itemType: ResourceType | ProductType,
    quantity: number,
    pricePerUnit: number
  ): string | null {
    const agent = this.agents.get(agentId);
    if (!agent) return null;

    // Check if agent has enough items
    const currentQuantity = agent.inventory.get(itemType) || 0;
    if (currentQuantity < quantity) return null;

    // Create the offer
    const offerId = this.marketSystem.createOffer(
      agentId,
      itemType,
      quantity,
      pricePerUnit
    );

    if (offerId) {
      agent.activeOffers.add(offerId);
      agent.inventory.set(itemType, currentQuantity - quantity);
    }

    return offerId;
  }

  /**
   * Execute a trade between two agents
   */
  public executeTrade(
    buyerId: string,
    offerId: string,
    quantity: number,
    marketId?: string
  ): boolean {
    const buyer = this.agents.get(buyerId);
    if (!buyer) return false;

    const transaction = this.marketSystem.executeTrade(
      offerId,
      buyerId,
      quantity,
      marketId
    );

    if (transaction) {
      const seller = this.agents.get(transaction.sellerId);
      if (seller) {
        // Update buyer
        buyer.currency -= transaction.pricePerUnit * quantity;
        this.addToInventory(buyer, transaction.itemType, quantity);
        buyer.lastTransaction = transaction.timestamp;

        // Update seller
        seller.currency += transaction.pricePerUnit * quantity;
        seller.lastTransaction = transaction.timestamp;
        seller.activeOffers.delete(offerId);

        return true;
      }
    }

    return false;
  }

  /**
   * Find the best trade offers for an agent
   */
  public findBestOffers(
    agentId: string,
    itemType: ResourceType | ProductType,
    maxPrice: number
  ): TradeOffer[] {
    const agent = this.agents.get(agentId);
    if (!agent) return [];

    // Get nearby agents using spatial grid
    const nearbyAgents = this.spatialGrid
      .getEntitiesInRange(agent.id, this.TRADE_SEARCH_RADIUS)
      .map(id => this.agents.get(id))
      .filter((a): a is EconomicAgent => a !== undefined);

    // Collect all relevant offers
    const relevantOffers: TradeOffer[] = [];
    for (const nearbyAgent of nearbyAgents) {
      for (const offerId of nearbyAgent.activeOffers) {
        const offer = this.marketSystem.getOffer(offerId);
        if (
          offer &&
          offer.itemType === itemType &&
          offer.pricePerUnit <= maxPrice
        ) {
          relevantOffers.push(offer);
        }
      }
    }

    // Sort by price and return
    return relevantOffers.sort((a, b) => a.pricePerUnit - b.pricePerUnit);
  }

  /**
   * Update agent's reputation based on successful trades
   */
  private updateReputation(agentId: string, changeAmount: number): void {
    const agent = this.agents.get(agentId);
    if (!agent) return;

    agent.reputation = Math.max(0, Math.min(100, agent.reputation + changeAmount));
  }

  /**
   * Check if agent has required resources for a recipe
   */
  private hasRequiredResources(
    agent: EconomicAgent,
    recipe: ProductionRecipe
  ): boolean {
    for (const [resource, amount] of recipe.inputs) {
      const available = agent.inventory.get(resource) || 0;
      if (available < amount) return false;
    }
    return true;
  }

  /**
   * Consume resources for production
   */
  private consumeResources(
    agent: EconomicAgent,
    recipe: ProductionRecipe
  ): void {
    for (const [resource, amount] of recipe.inputs) {
      const available = agent.inventory.get(resource) || 0;
      agent.inventory.set(resource, available - amount);
    }
  }

  /**
   * Add items to agent's inventory
   */
  private addToInventory(
    agent: EconomicAgent,
    itemType: ResourceType | ProductType,
    quantity: number
  ): void {
    const current = agent.inventory.get(itemType) || 0;
    agent.inventory.set(itemType, current + quantity);
  }

  /**
   * Start the production checking loop
   */
  private startProductionLoop(): void {
    setInterval(() => {
      for (const agent of this.agents.values()) {
        this.checkProduction(agent);
      }
    }, this.PRODUCTION_CHECK_INTERVAL);
  }

  /**
   * Check and complete production for an agent
   */
  private checkProduction(agent: EconomicAgent): void {
    const now = Date.now();
    const completedProductions = agent.productionQueue.filter(
      p => p.completesAt <= now
    );

    for (const production of completedProductions) {
      const recipe = agent.role.productionRecipes?.find(
        r => r.output.type === production.recipeId
      );

      if (recipe) {
        // Check for production failure
        const success = Math.random() > recipe.failureChance;
        if (success) {
          this.addToInventory(
            agent,
            recipe.output.type,
            recipe.output.quantity
          );
        }
      }

      // Remove from queue regardless of success
      agent.productionQueue = agent.productionQueue.filter(
        p => p !== production
      );
    }
  }

  /**
   * Start the trading behavior loop
   */
  private startTradingLoop(): void {
    setInterval(() => {
      for (const agent of this.agents.values()) {
        this.checkTrading(agent);
      }
    }, this.TRADE_CHECK_INTERVAL);
  }

  /**
   * Check and update trading behavior for an agent
   */
  private checkTrading(agent: EconomicAgent): void {
    if (!agent.role.tradingPreferences) return;

    const { preferredResources, preferredProducts, priceMarkup } = agent.role.tradingPreferences;

    // Check inventory for items to sell
    for (const [itemType, quantity] of agent.inventory) {
      if (quantity > 0) {
        const basePrice = this.getBasePrice(itemType as ResourceType | ProductType);
        const sellingPrice = basePrice * (1 + priceMarkup);

        // Create sell offer if none exists
        if (
          agent.activeOffers.size < 5 && // Limit active offers
          (preferredResources.includes(itemType as ResourceType) ||
            preferredProducts.includes(itemType as ProductType))
        ) {
          this.createTradeOffer(
            agent.id,
            itemType as ResourceType | ProductType,
            quantity,
            sellingPrice
          );
        }
      }
    }

    // Look for items to buy
    const desiredItems = [...preferredResources, ...preferredProducts];
    for (const itemType of desiredItems) {
      const currentQuantity = agent.inventory.get(itemType) || 0;
      if (currentQuantity < 10) { // Maintain minimum stock
        const basePrice = this.getBasePrice(itemType);
        const offers = this.findBestOffers(agent.id, itemType, basePrice * 1.5);
        
        for (const offer of offers) {
          if (agent.currency >= offer.pricePerUnit * offer.quantity) {
            this.executeTrade(agent.id, offer.id, offer.quantity);
            break;
          }
        }
      }
    }
  }

  /**
   * Get base price for an item type
   */
  private getBasePrice(itemType: ResourceType | ProductType): number {
    const priceData = this.marketSystem.getPriceStats(itemType);
    return priceData ? priceData.averagePrice : 100; // Default price if no history
  }

  public async processTrade(
    agentId: string,
    targetId: string,
    offer: any
  ): Promise<any> {
    try {
      // Process the trade based on the offer
      const result = {
        value: offer.economic.value,
        success: true,
        items: offer.economic.items
      };

      // Update agent's resources/inventory
      // Implementation depends on your specific economic system

      return result;
    } catch (error) {
      console.error('Error processing trade:', error);
      return {
        value: 0,
        success: false,
        error: 'Failed to process trade'
      };
    }
  }
} 