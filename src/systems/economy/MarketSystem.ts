import { v4 as uuidv4 } from 'uuid';
import {
  MarketData,
  TradeOffer,
  Transaction,
  MarketPriceData,
  ResourceType,
  ProductType,
  EconomicAgent,
  PriceStats,
  BundledTradeOffer,
  BundledTransaction
} from './EconomicTypes';
import { Logger } from '../../logging/Logger';
import { AppError, POIException, POIErrorCategory, POISeverityLevel, POIErrorCode } from '../../errors';
import * as fs from 'fs';
import * as path from 'path';
import { EventBus } from '../../core/interfaces/types/events';
import { ServiceEventType } from '../../core/interfaces/types/events';

// --- Validation Pipeline Types and Classes ---

type ValidationPhase = 'pre-trade' | 'execution' | 'post-trade';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  context?: Record<string, any>;
}

export interface TradeValidator {
  phase: ValidationPhase;
  validate(context: TradeValidationContext): ValidationResult | Promise<ValidationResult>;
}

export interface TradeValidationContext {
  offer: TradeOffer;
  buyerId: string;
  quantity: number;
  marketId?: string;
  [key: string]: any;
}

class ValidationPipeline {
  private validators: Map<ValidationPhase, TradeValidator[]> = new Map();

  constructor() {
    this.validators.set('pre-trade', []);
    this.validators.set('execution', []);
    this.validators.set('post-trade', []);
  }

  registerValidator(validator: TradeValidator) {
    const phase = validator.phase;
    if (!this.validators.has(phase)) {
      this.validators.set(phase, []);
    }
    this.validators.get(phase)!.push(validator);
  }

  async validate(phase: ValidationPhase, context: TradeValidationContext): Promise<ValidationResult> {
    const validators = this.validators.get(phase) || [];
    let allValid = true;
    let allErrors: string[] = [];
    for (const validator of validators) {
      const result = await validator.validate(context);
      if (!result.valid) {
        allValid = false;
        allErrors = allErrors.concat(result.errors);
      }
    }
    return { valid: allValid, errors: allErrors };
  }
}

// --- Standard Validators ---

const InventoryValidator: TradeValidator = {
  phase: 'pre-trade',
  validate: (context) => {
    // Placeholder: check if buyer has enough inventory space (implement actual logic as needed)
    // Assume always valid for now
    return { valid: true, errors: [] };
  }
};

const CurrencyValidator: TradeValidator = {
  phase: 'pre-trade',
  validate: (context) => {
    // Placeholder: check if buyer has enough currency (implement actual logic as needed)
    // Assume always valid for now
    return { valid: true, errors: [] };
  }
};

const OwnershipValidator: TradeValidator = {
  phase: 'execution',
  validate: (context) => {
    // Placeholder: check if seller still owns the item (implement actual logic as needed)
    // Assume always valid for now
    return { valid: true, errors: [] };
  }
};

// --- Trade Audit Logger ---

export interface TradeAuditEvent {
  timestamp: string;
  eventType: 'trade' | 'validation' | 'rollback' | 'error';
  transactionId?: string;
  offerId: string;
  buyerId: string;
  sellerId?: string;
  marketId?: string;
  phase?: string;
  beforeState?: any;
  afterState?: any;
  validationResult?: any;
  error?: string;
  message: string;
  context?: Record<string, any>;
}

export class TradeAuditLogger {
  private static logFilePath = path.resolve(process.cwd(), 'logs/trade_audit.log');
  private static instance: TradeAuditLogger;

  private constructor() {
    // Ensure log directory exists
    const dir = path.dirname(TradeAuditLogger.logFilePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  public static getInstance(): TradeAuditLogger {
    if (!TradeAuditLogger.instance) {
      TradeAuditLogger.instance = new TradeAuditLogger();
    }
    return TradeAuditLogger.instance;
  }

  public logEvent(event: TradeAuditEvent): void {
    const logEntry = JSON.stringify(event) + '\n';
    fs.appendFileSync(TradeAuditLogger.logFilePath, logEntry, { encoding: 'utf8' });
    if (process.env.NODE_ENV !== 'production') {
      // Also log to console in development
      // eslint-disable-next-line no-console
      console.log('[TradeAudit]', event);
    }
  }

  // Convenience static method
  public static log(event: TradeAuditEvent): void {
    TradeAuditLogger.getInstance().logEvent(event);
  }
}

// --- Cancellation Penalty Framework ---

interface PenaltyConfig {
  basePenalty: number;
  timeMultiplier: number;
  valueMultiplier: number;
  minPenalty: number;
  maxPenalty: number;
}

class PenaltyCalculator {
  private config: PenaltyConfig;
  constructor(config?: Partial<PenaltyConfig>) {
    this.config = {
      basePenalty: 10,
      timeMultiplier: 0.1,
      valueMultiplier: 0.05,
      minPenalty: 5,
      maxPenalty: 1000,
      ...config
    };
  }

  calculatePenalty({
    timeElapsedMs,
    tradeValue
  }: { timeElapsedMs: number; tradeValue: number }): number {
    let penalty = this.config.basePenalty;
    penalty += (timeElapsedMs / (60 * 60 * 1000)) * this.config.timeMultiplier; // per hour
    penalty += tradeValue * this.config.valueMultiplier;
    penalty = Math.max(this.config.minPenalty, Math.min(this.config.maxPenalty, Math.round(penalty)));
    return penalty;
  }
}

/**
 * MarketDirectory: Handles discovery, filtering, and notification of markets.
 */
class MarketDirectory {
  private markets: Map<string, MarketData>;
  private discoveredMarkets: Set<string>;
  private eventBus: EventBus;

  constructor(eventBus: EventBus) {
    this.markets = new Map();
    this.discoveredMarkets = new Set();
    this.eventBus = eventBus;
  }

  /**
   * Add or update a market in the directory.
   * Emits a notification if the market is newly discovered.
   */
  public addMarket(market: MarketData): void {
    const isNew = !this.markets.has(market.id);
    this.markets.set(market.id, market);
    if (isNew && !this.discoveredMarkets.has(market.id)) {
      this.discoveredMarkets.add(market.id);
      this.eventBus.emit(ServiceEventType.CREATED, {
        type: ServiceEventType.CREATED,
        timestamp: Date.now(),
        source: 'MarketDirectory',
        entityType: 'market',
        entityId: market.id,
        data: market,
        metadata: { discovered: true }
      });
    }
  }

  /**
   * Search for markets by type, goods, location, or name.
   */
  public searchMarkets({
    type,
    goods,
    location,
    radius,
    name
  }: {
    type?: ProductType;
    goods?: ResourceType | ProductType;
    location?: { x: number; y: number };
    radius?: number;
    name?: string;
  } = {}): MarketData[] {
    return Array.from(this.markets.values()).filter(market => {
      let match = true;
      if (type && (!market.specialization || !market.specialization.includes(type))) match = false;
      if (goods && (!market.specialization || !market.specialization.includes(goods as ProductType))) match = false;
      if (name && !market.name.toLowerCase().includes(name.toLowerCase())) match = false;
      if (location && typeof radius === 'number') {
        const dx = market.location.x - location.x;
        const dy = market.location.y - location.y;
        if (Math.sqrt(dx * dx + dy * dy) > radius) match = false;
      }
      return match;
    });
  }

  /**
   * Get all discovered markets.
   */
  public getDiscoveredMarkets(): MarketData[] {
    return Array.from(this.markets.values()).filter(m => this.discoveredMarkets.has(m.id));
  }
}

export class MarketSystem {
  private markets: Map<string, MarketData>;
  private offers: Map<string, TradeOffer>;
  private transactions: Transaction[];
  private priceHistory: Map<string, MarketPriceData[]>;
  private readonly MAX_HISTORY_LENGTH = 100;
  private readonly MAX_TRANSACTION_HISTORY = 1000;
  private readonly PRICE_UPDATE_INTERVAL = 60 * 60 * 1000; // 1 hour
  private readonly PRICE_HISTORY_LENGTH = 100;
  private validationPipeline: ValidationPipeline;
  private bundledOffers: Map<string, BundledTradeOffer> = new Map();
  private penaltyCalculator = new PenaltyCalculator();
  private marketDirectory: MarketDirectory;

  constructor() {
    this.markets = new Map();
    this.offers = new Map();
    this.transactions = [];
    this.priceHistory = new Map();
    this.validationPipeline = new ValidationPipeline();
    // Register standard validators
    this.validationPipeline.registerValidator(InventoryValidator);
    this.validationPipeline.registerValidator(CurrencyValidator);
    this.validationPipeline.registerValidator(OwnershipValidator);
    // Initialize MarketDirectory with EventBus
    this.marketDirectory = new MarketDirectory(EventBus.getInstance());
  }

  /**
   * Register a new market (and notify MarketDirectory).
   */
  public registerMarket(market: MarketData): void {
    this.markets.set(market.id, market);
    this.marketDirectory.addMarket(market);
  }

  /**
   * Search for markets using the MarketDirectory.
   */
  public searchMarkets(params: {
    type?: ProductType;
    goods?: ResourceType | ProductType;
    location?: { x: number; y: number };
    radius?: number;
    name?: string;
  } = {}): MarketData[] {
    return this.marketDirectory.searchMarkets(params);
  }

  /**
   * Get all discovered markets.
   */
  public getDiscoveredMarkets(): MarketData[] {
    return this.marketDirectory.getDiscoveredMarkets();
  }

  /**
   * Notify market discovery from exploration mechanics.
   * Call this when a player explores a new area and discovers a market.
   */
  public notifyMarketDiscovered(marketId: string): void {
    const market = this.markets.get(marketId);
    if (market) {
      this.marketDirectory.addMarket(market);
    }
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
   * Apply cancellation penalty to a user (currency, reputation, etc.)
   * Extend this to integrate with currency, reputation, and notification systems.
   */
  private applyCancellationPenalty(
    userId: string,
    penalty: number,
    context: { offerId: string; reason: string; tradeValue: number; timeElapsedMs: number }
  ) {
    // TODO: Integrate with currency and reputation systems
    // For now, just log the penalty
    TradeAuditLogger.log({
      timestamp: new Date().toISOString(),
      eventType: 'trade',
      offerId: context.offerId,
      buyerId: userId,
      message: `Cancellation penalty applied: ${penalty} (reason: ${context.reason})`,
      context: { ...context, penalty }
    });
    // TODO: Notify user of penalty
  }

  /**
   * Cancel a trade offer and apply penalty if appropriate
   */
  public cancelOffer(offerId: string, sellerId: string): boolean {
    const offer = this.offers.get(offerId);
    if (!offer || offer.sellerId !== sellerId) return false;
    // Calculate penalty based on time and value
    const now = Date.now();
    const timeElapsedMs = now - (offer.expiresAt - 24 * 60 * 60 * 1000); // assuming 24h default
    const tradeValue = offer.pricePerUnit * offer.quantity;
    const penalty = this.penaltyCalculator.calculatePenalty({ timeElapsedMs, tradeValue });
    this.applyCancellationPenalty(sellerId, penalty, {
      offerId,
      reason: 'Trade offer cancelled',
      tradeValue,
      timeElapsedMs
    });
    // Remove the offer
    return this.offers.delete(offerId);
  }

  /**
   * Execute a trade between two agents with atomic transaction, rollback, error handling, validation pipeline, and audit logging
   */
  public async executeTrade(
    offerId: string,
    buyerId: string,
    quantity: number,
    marketId?: string
  ): Promise<Transaction | null> {
    // Logger instance
    const logger = Logger.getInstance();
    // State snapshot for rollback
    let offerSnapshot: TradeOffer | null = null;
    let transaction: Transaction | null = null;
    try {
      const offer = this.offers.get(offerId);
      if (!offer) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          marketId,
          message: `Offer not found`,
          error: 'OFFER_NOT_FOUND',
        });
        throw new AppError(
          `Offer ${offerId} not found`,
          'OFFER_NOT_FOUND',
          404,
          { offerId, buyerId, quantity, marketId }
        );
      }
      // --- Pre-trade validation ---
      const preTradeResult = await this.validationPipeline.validate('pre-trade', { offer, buyerId, quantity, marketId });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'validation',
        offerId,
        buyerId,
        sellerId: offer.sellerId,
        marketId,
        phase: 'pre-trade',
        validationResult: preTradeResult,
        message: 'Pre-trade validation result',
      });
      if (!preTradeResult.valid) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          sellerId: offer.sellerId,
          marketId,
          phase: 'pre-trade',
          validationResult: preTradeResult,
          message: `Pre-trade validation failed: ${preTradeResult.errors.join('; ')}`,
          error: 'PRE_TRADE_VALIDATION_FAILED',
        });
        throw new AppError(
          `Pre-trade validation failed: ${preTradeResult.errors.join('; ')}`,
          'PRE_TRADE_VALIDATION_FAILED',
          400,
          { offerId, buyerId, quantity, marketId, errors: preTradeResult.errors }
        );
      }
      // Validate quantity
      if (quantity > offer.quantity) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          sellerId: offer.sellerId,
          marketId,
          message: `Requested quantity exceeds available`,
          error: 'QUANTITY_EXCEEDS_AVAILABLE',
        });
        throw new AppError(
          `Requested quantity exceeds available for offer ${offerId}`,
          'QUANTITY_EXCEEDS_AVAILABLE',
          400,
          { offerId, buyerId, quantity, available: offer.quantity }
        );
      }
      if (offer.minimumQuantity && quantity < offer.minimumQuantity) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          sellerId: offer.sellerId,
          marketId,
          message: `Requested quantity below minimum`,
          error: 'QUANTITY_BELOW_MINIMUM',
        });
        throw new AppError(
          `Requested quantity below minimum for offer ${offerId}`,
          'QUANTITY_BELOW_MINIMUM',
          400,
          { offerId, buyerId, quantity, minimum: offer.minimumQuantity }
        );
      }
      // Snapshot offer state for rollback
      offerSnapshot = { ...offer };
      // --- Execution validation ---
      const executionResult = await this.validationPipeline.validate('execution', { offer, buyerId, quantity, marketId });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'validation',
        offerId,
        buyerId,
        sellerId: offer.sellerId,
        marketId,
        phase: 'execution',
        validationResult: executionResult,
        message: 'Execution validation result',
      });
      if (!executionResult.valid) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          sellerId: offer.sellerId,
          marketId,
          phase: 'execution',
          validationResult: executionResult,
          message: `Execution validation failed: ${executionResult.errors.join('; ')}`,
          error: 'EXECUTION_VALIDATION_FAILED',
        });
        throw new AppError(
          `Execution validation failed: ${executionResult.errors.join('; ')}`,
          'EXECUTION_VALIDATION_FAILED',
          400,
          { offerId, buyerId, quantity, marketId, errors: executionResult.errors }
        );
      }
      // Create transaction
      transaction = {
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
      // --- Post-trade validation ---
      const postTradeResult = await this.validationPipeline.validate('post-trade', { offer, buyerId, quantity, marketId, transaction });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'validation',
        offerId,
        buyerId,
        sellerId: offer.sellerId,
        marketId,
        transactionId: transaction.id,
        phase: 'post-trade',
        validationResult: postTradeResult,
        message: 'Post-trade validation result',
      });
      if (!postTradeResult.valid) {
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'error',
          offerId,
          buyerId,
          sellerId: offer.sellerId,
          marketId,
          transactionId: transaction.id,
          phase: 'post-trade',
          validationResult: postTradeResult,
          message: `Post-trade validation failed: ${postTradeResult.errors.join('; ')}`,
          error: 'POST_TRADE_VALIDATION_FAILED',
        });
        throw new AppError(
          `Post-trade validation failed: ${postTradeResult.errors.join('; ')}`,
          'POST_TRADE_VALIDATION_FAILED',
          400,
          { offerId, buyerId, quantity, marketId, errors: postTradeResult.errors }
        );
      }
      // Log state change and audit
      Logger.logStateChange({
        poiId: offerId,
        poiType: 'TradeOffer',
        actor: buyerId,
        beforeState: offerSnapshot,
        afterState: offer,
        correlationId: transaction.id,
        eventSubtype: 'TRADE_EXECUTED',
        message: `Trade executed: ${quantity} x ${offer.itemType} from ${offer.sellerId} to ${buyerId}`
      });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'trade',
        offerId,
        buyerId,
        sellerId: offer.sellerId,
        marketId,
        transactionId: transaction.id,
        beforeState: offerSnapshot,
        afterState: offer,
        message: `Trade executed: ${quantity} x ${offer.itemType} from ${offer.sellerId} to ${buyerId}`,
        context: { transaction }
      });
      return transaction;
    } catch (error) {
      // Rollback logic
      if (offerSnapshot) {
        this.offers.set(offerSnapshot.id, offerSnapshot);
      }
      if (transaction) {
        this.transactions = this.transactions.filter(t => t.id !== transaction!.id);
      }
      // Log error with context
      Logger.logError({
        poiId: offerId,
        poiType: 'TradeOffer',
        actor: buyerId,
        eventSubtype: error instanceof AppError ? error.code : 'UNKNOWN_ERROR',
        correlationId: transaction ? transaction.id : uuidv4(),
        message: error instanceof Error ? error.message : String(error)
      });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'rollback',
        offerId,
        buyerId,
        sellerId: offerSnapshot?.sellerId,
        marketId,
        transactionId: transaction?.id,
        beforeState: offerSnapshot,
        afterState: this.offers.get(offerId),
        error: error instanceof Error ? error.message : String(error),
        message: 'Trade rollback due to error',
      });
      if (error instanceof AppError || error instanceof POIException) {
        throw error;
      } else {
        throw new POIException(
          'Unknown error during trade execution',
          POIErrorCategory.UNKNOWN,
          POISeverityLevel.MEDIUM,
          POIErrorCode.POI_UNKNOWN,
          { additionalData: { offerId, buyerId, quantity, marketId } },
        );
      }
    }
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

  /**
   * Create a bundled trade offer (multi-item atomic package)
   */
  public createBundledOffer(
    sellerId: string,
    items: Array<{ itemType: ResourceType | ProductType; quantity: number; pricePerUnit: number; minimumQuantity?: number; negotiable?: boolean }>,
    totalPrice: number,
    expiresIn: number = 24 * 60 * 60 * 1000, // 24 hours default
    negotiable: boolean = true
  ): string {
    const offer: BundledTradeOffer = {
      id: uuidv4(),
      sellerId,
      items,
      totalPrice,
      expiresAt: Date.now() + expiresIn,
      negotiable
    };
    this.bundledOffers.set(offer.id, offer);
    return offer.id;
  }

  /**
   * Execute a bundled trade (all-or-nothing multi-item trade)
   */
  public async executeBundledTrade(
    bundleId: string,
    buyerId: string,
    marketId?: string
  ): Promise<BundledTransaction | null> {
    const logger = Logger.getInstance();
    const bundle = this.bundledOffers.get(bundleId);
    if (!bundle) {
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'error',
        offerId: bundleId,
        buyerId,
        marketId,
        message: 'Bundled offer not found',
        error: 'BUNDLED_OFFER_NOT_FOUND',
      });
      throw new AppError(
        `Bundled offer ${bundleId} not found`,
        'BUNDLED_OFFER_NOT_FOUND',
        404,
        { bundleId, buyerId, marketId }
      );
    }
    // Snapshot for rollback
    const offerSnapshots = bundle.items.map(item => ({ ...item }));
    let transaction: BundledTransaction | null = null;
    try {
      // --- Pre-trade validation for all items ---
      for (const item of bundle.items) {
        // Construct a TradeOffer-like object for validation
        const offerForValidation = {
          id: `${bundle.id}:${item.itemType}`,
          sellerId: bundle.sellerId,
          itemType: item.itemType,
          quantity: item.quantity,
          pricePerUnit: item.pricePerUnit,
          expiresAt: bundle.expiresAt,
          minimumQuantity: item.minimumQuantity,
          negotiable: item.negotiable ?? bundle.negotiable
        };
        const context = { offer: offerForValidation, buyerId, quantity: item.quantity, marketId, bundleId };
        const preResult = await this.validationPipeline.validate('pre-trade', context);
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'validation',
          offerId: bundleId,
          buyerId,
          sellerId: bundle.sellerId,
          marketId,
          phase: 'pre-trade',
          validationResult: preResult,
          message: `Pre-trade validation for bundled item ${item.itemType}`
        });
        if (!preResult.valid) {
          TradeAuditLogger.log({
            timestamp: new Date().toISOString(),
            eventType: 'error',
            offerId: bundleId,
            buyerId,
            sellerId: bundle.sellerId,
            marketId,
            phase: 'pre-trade',
            validationResult: preResult,
            message: `Pre-trade validation failed for bundled item ${item.itemType}: ${preResult.errors.join('; ')}`,
            error: 'BUNDLE_PRE_TRADE_VALIDATION_FAILED',
          });
          throw new AppError(
            `Pre-trade validation failed for bundled item ${item.itemType}: ${preResult.errors.join('; ')}`,
            'BUNDLE_PRE_TRADE_VALIDATION_FAILED',
            400,
            { bundleId, buyerId, marketId, errors: preResult.errors }
          );
        }
      }
      // --- Execution validation for all items ---
      for (const item of bundle.items) {
        const offerForValidation = {
          id: `${bundle.id}:${item.itemType}`,
          sellerId: bundle.sellerId,
          itemType: item.itemType,
          quantity: item.quantity,
          pricePerUnit: item.pricePerUnit,
          expiresAt: bundle.expiresAt,
          minimumQuantity: item.minimumQuantity,
          negotiable: item.negotiable ?? bundle.negotiable
        };
        const context = { offer: offerForValidation, buyerId, quantity: item.quantity, marketId, bundleId };
        const execResult = await this.validationPipeline.validate('execution', context);
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'validation',
          offerId: bundleId,
          buyerId,
          sellerId: bundle.sellerId,
          marketId,
          phase: 'execution',
          validationResult: execResult,
          message: `Execution validation for bundled item ${item.itemType}`
        });
        if (!execResult.valid) {
          TradeAuditLogger.log({
            timestamp: new Date().toISOString(),
            eventType: 'error',
            offerId: bundleId,
            buyerId,
            sellerId: bundle.sellerId,
            marketId,
            phase: 'execution',
            validationResult: execResult,
            message: `Execution validation failed for bundled item ${item.itemType}: ${execResult.errors.join('; ')}`,
            error: 'BUNDLE_EXECUTION_VALIDATION_FAILED',
          });
          throw new AppError(
            `Execution validation failed for bundled item ${item.itemType}: ${execResult.errors.join('; ')}`,
            'BUNDLE_EXECUTION_VALIDATION_FAILED',
            400,
            { bundleId, buyerId, marketId, errors: execResult.errors }
          );
        }
      }
      // --- Execute all items atomically ---
      const transactionId = uuidv4();
      const now = Date.now();
      transaction = {
        id: transactionId,
        timestamp: now,
        buyerId,
        sellerId: bundle.sellerId,
        items: bundle.items.map(item => ({
          itemType: item.itemType,
          quantity: item.quantity,
          pricePerUnit: item.pricePerUnit
        })),
        totalPrice: bundle.totalPrice,
        marketId
      };
      // Remove the bundle offer after execution
      this.bundledOffers.delete(bundleId);
      // --- Post-trade validation for all items ---
      for (const item of bundle.items) {
        const offerForValidation = {
          id: `${bundle.id}:${item.itemType}`,
          sellerId: bundle.sellerId,
          itemType: item.itemType,
          quantity: item.quantity,
          pricePerUnit: item.pricePerUnit,
          expiresAt: bundle.expiresAt,
          minimumQuantity: item.minimumQuantity,
          negotiable: item.negotiable ?? bundle.negotiable
        };
        const context = { offer: offerForValidation, buyerId, quantity: item.quantity, marketId, bundleId, transaction };
        const postResult = await this.validationPipeline.validate('post-trade', context);
        TradeAuditLogger.log({
          timestamp: new Date().toISOString(),
          eventType: 'validation',
          offerId: bundleId,
          buyerId,
          sellerId: bundle.sellerId,
          marketId,
          transactionId: transactionId,
          phase: 'post-trade',
          validationResult: postResult,
          message: `Post-trade validation for bundled item ${item.itemType}`
        });
        if (!postResult.valid) {
          TradeAuditLogger.log({
            timestamp: new Date().toISOString(),
            eventType: 'error',
            offerId: bundleId,
            buyerId,
            sellerId: bundle.sellerId,
            marketId,
            transactionId: transactionId,
            phase: 'post-trade',
            validationResult: postResult,
            message: `Post-trade validation failed for bundled item ${item.itemType}: ${postResult.errors.join('; ')}`,
            error: 'BUNDLE_POST_TRADE_VALIDATION_FAILED',
          });
          throw new AppError(
            `Post-trade validation failed for bundled item ${item.itemType}: ${postResult.errors.join('; ')}`,
            'BUNDLE_POST_TRADE_VALIDATION_FAILED',
            400,
            { bundleId, buyerId, marketId, errors: postResult.errors }
          );
        }
      }
      // --- Audit log for bundled trade ---
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'trade',
        offerId: bundleId,
        buyerId,
        sellerId: bundle.sellerId,
        marketId,
        transactionId,
        beforeState: offerSnapshots,
        afterState: bundle.items,
        message: `Bundled trade executed: ${bundle.items.length} items from ${bundle.sellerId} to ${buyerId}`,
        context: { transaction }
      });
      return transaction;
    } catch (error) {
      // Rollback logic: restore all items to their original state if needed
      this.bundledOffers.set(bundleId, {
        ...bundle,
        items: offerSnapshots.map(snap => ({ ...snap }))
      });
      TradeAuditLogger.log({
        timestamp: new Date().toISOString(),
        eventType: 'rollback',
        offerId: bundleId,
        buyerId,
        sellerId: bundle.sellerId,
        marketId,
        transactionId: transaction?.id,
        beforeState: offerSnapshots,
        afterState: bundle.items,
        error: error instanceof Error ? error.message : String(error),
        message: 'Bundled trade rollback due to error',
      });
      if (error instanceof AppError || error instanceof POIException) {
        throw error;
      } else {
        throw new POIException(
          'Unknown error during bundled trade execution',
          POIErrorCategory.UNKNOWN,
          POISeverityLevel.MEDIUM,
          POIErrorCode.POI_UNKNOWN,
          { additionalData: { bundleId, buyerId, marketId } },
        );
      }
    }
  }
} 