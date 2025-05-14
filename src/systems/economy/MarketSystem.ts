import { v4 as uuidv4 } from 'uuid';
import {
  MarketData,
  TradeOffer,
  Transaction,
  MarketPriceData,
  ResourceType,
  ProductType,
  EconomicAgent,
  PriceStats
} from './EconomicTypes';

export class MarketSystem {
  private markets: Map<string, MarketData>;
  private offers: Map<string, TradeOffer>;
  private transactions: Transaction[];
  private priceHistory: Map<string, MarketPriceData[]>;
  private readonly MAX_HISTORY_LENGTH = 100;
  private readonly MAX_TRANSACTION_HISTORY = 1000;
  private readonly PRICE_UPDATE_INTERVAL = 60 * 60 * 1000; // 1 hour
  private readonly PRICE_HISTORY_LENGTH = 100;

  constructor() {
    this.markets = new Map();
    this.offers = new Map();
    this.transactions = [];
    this.priceHistory = new Map();
  }

  /**
   * Register a new market
   */
  public registerMarket(market: MarketData): void {
    this.markets.set(market.id, market);
  }

  /**
   * Check if a market is currently open
   */
  public isMarketOpen(marketId: string): boolean {
    const market = this.markets.get(marketId);
    if (!market) return false;

    const now = new Date();
    const currentHour = now.getHours();
    const currentDay = now.getDay();

    return (
      market.schedule.openDays.includes(currentDay) &&
      currentHour >= market.schedule.openTime &&
      currentHour < market.schedule.closeTime
    );
  }

  /**
   * Create a new trade offer
   */
  public createOffer(
    sellerId: string,
    itemType: ResourceType | ProductType,
    quantity: number,
    pricePerUnit: number,
    expiresIn: number = 24 * 60 * 60 * 1000, // 24 hours default
    minimumQuantity?: number,
    negotiable: boolean = true
  ): string {
    const offer: TradeOffer = {
      id: uuidv4(),
      sellerId,
      itemType,
      quantity,
      pricePerUnit,
      expiresAt: Date.now() + expiresIn,
      minimumQuantity,
      negotiable
    };

    this.offers.set(offer.id, offer);
    return offer.id;
  }

  /**
   * Cancel a trade offer
   */
  public cancelOffer(offerId: string, sellerId: string): boolean {
    const offer = this.offers.get(offerId);
    if (!offer || offer.sellerId !== sellerId) return false;

    return this.offers.delete(offerId);
  }

  /**
   * Execute a trade between two agents
   */
  public executeTrade(
    offerId: string,
    buyerId: string,
    quantity: number,
    marketId?: string
  ): Transaction | null {
    const offer = this.offers.get(offerId);
    if (!offer) return null;

    // Validate quantity
    if (quantity > offer.quantity) return null;
    if (offer.minimumQuantity && quantity < offer.minimumQuantity) return null;

    // Create transaction
    const transaction: Transaction = {
      id: uuidv4(),
      timestamp: Date.now(),
      buyerId,
      sellerId: offer.sellerId,
      itemType: offer.itemType,
      quantity,
      pricePerUnit: offer.pricePerUnit,
      marketId
    };

    // Update offer quantity or remove if fully consumed
    offer.quantity -= quantity;
    if (offer.quantity === 0) {
      this.offers.delete(offer.id);
    }

    // Record transaction
    this.transactions.push(transaction);
    if (this.transactions.length > this.MAX_TRANSACTION_HISTORY) {
      this.transactions.shift();
    }

    // Update price history
    this.updatePriceData(transaction);

    return transaction;
  }

  /**
   * Get all active offers in a market
   */
  public getMarketOffers(
    marketId: string,
    itemType?: ResourceType | ProductType
  ): TradeOffer[] {
    const now = Date.now();
    return Array.from(this.offers.values())
      .filter(offer => {
        const withinMarket = !marketId || this.isOfferInMarket(offer, marketId);
        const notExpired = offer.expiresAt > now;
        const matchesType = !itemType || offer.itemType === itemType;
        return withinMarket && notExpired && matchesType;
      });
  }

  /**
   * Check if an offer is valid in a specific market
   */
  private isOfferInMarket(offer: TradeOffer, marketId: string): boolean {
    const market = this.markets.get(marketId);
    if (!market) return false;

    // Check if market specializes in this type of item
    if (market.specialization) {
      return market.specialization.includes(offer.itemType as ProductType);
    }

    return true;
  }

  /**
   * Update price history with a new transaction
   */
  private updatePriceData(transaction: Transaction): void {
    const key = `${transaction.marketId || 'global'}_${transaction.itemType}`;
    
    if (!this.priceHistory.has(key)) {
      this.priceHistory.set(key, []);
    }

    const history = this.priceHistory.get(key)!;
    const lastPrice = history[history.length - 1];
    
    const newPrice: MarketPriceData = {
      itemType: transaction.itemType,
      averagePrice: transaction.pricePerUnit,
      minPrice: transaction.pricePerUnit,
      maxPrice: transaction.pricePerUnit,
      volume: transaction.quantity,
      trend: lastPrice ? 
        (transaction.pricePerUnit - lastPrice.averagePrice) / lastPrice.averagePrice : 
        0,
      lastUpdate: transaction.timestamp
    };

    history.push(newPrice);
    if (history.length > this.MAX_HISTORY_LENGTH) {
      history.shift();
    }
  }

  /**
   * Get price statistics for a resource or product
   */
  public getPriceStats(itemType: ResourceType | ProductType): PriceStats | undefined {
    const history = this.priceHistory.get(itemType);
    if (!history || history.length === 0) return undefined;

    const recent = history.slice(-10); // Last 10 data points
    const prices = recent.map(p => p.averagePrice);
    const sum = prices.reduce((a, b) => a + b, 0);
    const avg = sum / prices.length;
    const sorted = [...prices].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];
    const min = Math.min(...recent.map(p => p.minPrice));
    const max = Math.max(...recent.map(p => p.maxPrice));

    return {
      averagePrice: avg,
      medianPrice: median,
      minPrice: min,
      maxPrice: max,
      numTransactions: recent.reduce((sum, p) => sum + p.volume, 0)
    };
  }

  /**
   * Find the best offer for an item
   */
  public findBestOffer(
    itemType: ResourceType | ProductType,
    quantity: number,
    maxPrice?: number
  ): TradeOffer | null {
    const validOffers = Array.from(this.offers.values())
      .filter(offer => 
        offer.itemType === itemType &&
        offer.quantity >= quantity &&
        offer.expiresAt > Date.now() &&
        (!maxPrice || offer.pricePerUnit <= maxPrice)
      )
      .sort((a, b) => a.pricePerUnit - b.pricePerUnit);

    return validOffers[0] || null;
  }

  /**
   * Get recent transactions for an agent
   */
  public getAgentTransactions(
    agentId: string,
    limit: number = 10
  ): Transaction[] {
    return this.transactions
      .filter(t => t.buyerId === agentId || t.sellerId === agentId)
      .slice(-limit);
  }

  /**
   * Clean up expired offers
   */
  public cleanupExpiredOffers(): void {
    const now = Date.now();
    for (const [id, offer] of this.offers) {
      if (offer.expiresAt <= now) {
        this.offers.delete(id);
      }
    }
  }

  /**
   * Calculate market activity score
   */
  public getMarketActivity(marketId: string): number {
    const market = this.markets.get(marketId);
    if (!market) return 0;

    const recentTransactions = this.transactions
      .filter(t => 
        t.marketId === marketId &&
        t.timestamp > Date.now() - 24 * 60 * 60 * 1000 // Last 24 hours
      );

    const uniqueTraders = new Set([
      ...recentTransactions.map(t => t.buyerId),
      ...recentTransactions.map(t => t.sellerId)
    ]).size;

    const transactionVolume = recentTransactions.reduce((sum, t) => 
      sum + t.quantity * t.pricePerUnit, 0);

    // Score from 0-100 based on traders and volume
    return Math.min(100, 
      (uniqueTraders * 5) + // 5 points per unique trader
      (transactionVolume / 1000) // 1 point per 1000 currency volume
    );
  }

  /**
   * Get a specific trade offer by ID
   */
  public getOffer(offerId: string): TradeOffer | undefined {
    return this.offers.get(offerId);
  }
} 