/**
 * EconomySystem.ts
 * 
 * Implements a comprehensive economy system for managing currency, item values,
 * price calculations, merchant inventories, and trading.
 */

import { BaseSystemManager, SystemConfig, SystemEvent } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    Currency,
    CurrencyType,
    EconomicValue,
    Item,
    ItemRarity,
    PriceFactors
} from './DataModels';

// Additional interfaces for the economy system
export interface MerchantData extends BaseEntity {
    name: string;
    regionId: string;
    specialization?: string; // Type of merchant (e.g., blacksmith, alchemist)
    buyPriceModifier: number; // Multiplier when buying from player (lower = cheaper)
    sellPriceModifier: number; // Multiplier when selling to player (higher = expensive)
    inventoryIds: string[];  // IDs of inventories this merchant manages
    restockInterval: number; // Time in ms between restocks
    lastRestockTime: number; // Timestamp of last restock
    reputation: number;      // 0-100 scale
    currencies: Currency[];  // Available currencies for transactions
}

export interface CurrencyConversionRates {
    [CurrencyType.GOLD]: number;
    [CurrencyType.SILVER]: number;
    [CurrencyType.COPPER]: number;
    [CurrencyType.SPECIAL]?: Record<string, number>;
}

export interface TradeResult {
    success: boolean;
    message: string;
    playerCurrencies?: Currency[];
    merchantCurrencies?: Currency[];
    itemsTraded?: Item[];
}

export interface PriceCalculationParams {
    baseValue: EconomicValue;
    regionId?: string;
    merchantId?: string;
    playerReputation?: number;
    season?: string;
    isBuying?: boolean; // true if merchant is buying from player
}

export interface RegionalPriceData extends BaseEntity {
    regionId: string;
    name: string;
    basePriceModifier: number;
    itemTypeModifiers: Record<string, number>;
    supplyDemandModifiers: Record<string, number>;
    seasonalModifiers: Record<string, Record<string, number>>;
}

/**
 * EconomySystem manages all economy-related operations
 */
export class EconomySystem extends BaseSystemManager {
    private merchantRepository: Repository<MerchantData>;
    private regionPriceRepository: Repository<RegionalPriceData>;

    // Default conversion rates between currencies
    private conversionRates: CurrencyConversionRates = {
        [CurrencyType.GOLD]: 1,
        [CurrencyType.SILVER]: 0.01, // 100 silver = 1 gold
        [CurrencyType.COPPER]: 0.0001, // 100 copper = 1 silver, 10000 copper = 1 gold
    };

    constructor(config: SystemConfig) {
        super({
            ...config,
            name: config.name || 'EconomySystem'
        });
    }

    /**
     * Initialize economy repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.merchantRepository = this.createRepository<MerchantData>(
            'merchants',
            ['regionId', 'specialization']
        );

        this.regionPriceRepository = this.createRepository<RegionalPriceData>(
            'region_prices',
            ['regionId']
        );
    }

    /**
     * Initialize system-specific functionality
     */
    protected async initializeSystem(): Promise<void> {
        // Set up event handlers
        this.on('merchant:created', this.handleMerchantCreated.bind(this));
        this.on('merchant:restocked', this.handleMerchantRestocked.bind(this));
        this.on('region:priceChanged', this.handleRegionPriceChanged.bind(this));

        // Set up periodic restock check
        setInterval(this.checkMerchantRestocks.bind(this), 60000); // Check every minute
    }

    /**
     * System shutdown
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down EconomySystem');
    }

    /**
     * Create a new merchant
     */
    public async createMerchant(data: Omit<MerchantData, 'id' | 'createdAt' | 'updatedAt'>): Promise<MerchantData> {
        this.logInfo(`Creating merchant: ${data.name} in region ${data.regionId}`);

        const merchant = await this.merchantRepository.create({
            ...data,
            buyPriceModifier: data.buyPriceModifier || 0.5, // Default to 50% of value when buying from player
            sellPriceModifier: data.sellPriceModifier || 1.5, // Default to 150% of value when selling to player
            inventoryIds: data.inventoryIds || [],
            restockInterval: data.restockInterval || 86400000, // Default to 24 hours
            lastRestockTime: data.lastRestockTime || Date.now(),
            reputation: data.reputation || 50, // Default to neutral reputation
            currencies: data.currencies || [
                { type: CurrencyType.GOLD, amount: 500 },
                { type: CurrencyType.SILVER, amount: 5000 },
                { type: CurrencyType.COPPER, amount: 10000 }
            ]
        });

        // Emit merchant created event
        await this.emitEvent({
            type: 'merchant:created',
            source: this.name,
            timestamp: Date.now(),
            data: { merchant }
        });

        return merchant;
    }

    /**
     * Create or update regional price data
     */
    public async setRegionalPrices(data: Omit<RegionalPriceData, 'id' | 'createdAt' | 'updatedAt'>): Promise<RegionalPriceData> {
        this.logInfo(`Setting price data for region: ${data.name} (${data.regionId})`);

        // Check if region already exists
        const existingRegions = await this.regionPriceRepository.findBy('regionId', data.regionId);

        if (existingRegions.length > 0) {
            // Update existing
            const updated = await this.regionPriceRepository.update(
                existingRegions[0].id,
                data
            );

            if (updated) {
                await this.emitEvent({
                    type: 'region:priceChanged',
                    source: this.name,
                    timestamp: Date.now(),
                    data: { region: updated }
                });
                return updated;
            }

            return existingRegions[0];
        } else {
            // Create new
            const newRegion = await this.regionPriceRepository.create(data);

            await this.emitEvent({
                type: 'region:priceChanged',
                source: this.name,
                timestamp: Date.now(),
                data: { region: newRegion }
            });

            return newRegion;
        }
    }

    /**
     * Calculate the price of an item based on various factors
     */
    public async calculatePrice(params: PriceCalculationParams): Promise<EconomicValue> {
        const { baseValue, regionId, merchantId, playerReputation, season, isBuying } = params;

        // Start with the base value
        let valueModifier = baseValue.valueModifier;

        // Initialize price factors
        const priceFactors: PriceFactors = {
            regionalModifier: 1.0,
            supplyModifier: 1.0,
            demandModifier: 1.0,
            reputationModifier: 1.0,
            seasonalModifier: 1.0
        };

        // Apply regional modifiers if available
        if (regionId) {
            const regionData = await this.getRegionPriceData(regionId);
            if (regionData) {
                priceFactors.regionalModifier = regionData.basePriceModifier;

                // Apply seasonal modifier if available
                if (season && regionData.seasonalModifiers && regionData.seasonalModifiers[season]) {
                    priceFactors.seasonalModifier = regionData.seasonalModifiers[season].default || 1.0;
                }
            }
        }

        // Apply merchant modifiers if available
        if (merchantId) {
            const merchant = await this.merchantRepository.findById(merchantId);
            if (merchant) {
                // Apply buy/sell modifier based on transaction direction
                if (isBuying) {
                    valueModifier *= merchant.buyPriceModifier;
                } else {
                    valueModifier *= merchant.sellPriceModifier;
                }
            }
        }

        // Apply reputation modifier if available
        if (playerReputation !== undefined) {
            // Scale from 0.8 (0 reputation) to 1.2 (100 reputation)
            priceFactors.reputationModifier = 0.8 + (Number(playerReputation) / 250);
        }

        // Calculate combined modifier
        const combinedModifier = Object.values(priceFactors).reduce((a, b) => a * b, 1.0);
        valueModifier *= combinedModifier;

        // Create new economic value object with adjusted pricing
        const result: EconomicValue = {
            currencies: baseValue.currencies.map(currency => ({
                type: currency.type,
                amount: Math.max(1, Math.round(currency.amount * valueModifier)),
                specialType: currency.specialType
            })),
            valueModifier
        };

        return result;
    }

    /**
     * Convert between different currency types
     */
    public convertCurrency(
        fromCurrency: Currency,
        toType: CurrencyType,
        toSpecialType?: string
    ): Currency {
        // Handle special currencies
        if (fromCurrency.type === CurrencyType.SPECIAL || toType === CurrencyType.SPECIAL) {
            if (!this.conversionRates[CurrencyType.SPECIAL] ||
                !fromCurrency.specialType ||
                !toSpecialType) {
                throw new Error('Special currency conversion requires specialType and conversion rates');
            }

            // This would handle special currency conversions
            throw new Error('Special currency conversion not implemented');
        }

        // Standard currency conversion
        const fromRate = this.conversionRates[fromCurrency.type];
        const toRate = this.conversionRates[toType];

        if (!fromRate || !toRate) {
            throw new Error(`Unknown currency type: ${fromCurrency.type} or ${toType}`);
        }

        // Calculate conversion
        const valueInGold = fromCurrency.amount * fromRate;
        const convertedAmount = valueInGold / toRate;

        // Round down to avoid fractions of currency
        return {
            type: toType,
            amount: Math.floor(convertedAmount)
        };
    }

    /**
     * Add currencies together
     */
    public combineCurrencies(currencies: Currency[]): Currency[] {
        const result = new Map<string, Currency>();

        for (const currency of currencies) {
            const key = currency.specialType ?
                `${currency.type}_${currency.specialType}` :
                currency.type;

            const existing = result.get(key);

            if (existing) {
                existing.amount += currency.amount;
            } else {
                result.set(key, { ...currency });
            }
        }

        return Array.from(result.values());
    }

    /**
     * Subtract currencies
     * Returns the remaining currencies after subtraction, or null if insufficient funds
     */
    public subtractCurrencies(from: Currency[], amount: Currency[]): Currency[] | null {
        // First, ensure sufficient funds by converting everything to gold
        const totalFrom = this.calculateTotalValue(from);
        const totalAmount = this.calculateTotalValue(amount);

        if (totalFrom < totalAmount) {
            return null; // Insufficient funds
        }

        // Clone the currencies to avoid modifying originals
        const result = from.map(c => ({ ...c }));

        // Process each currency to subtract
        for (const currencyToSubtract of amount) {
            // Find matching currency
            const matchIndex = result.findIndex(c =>
                c.type === currencyToSubtract.type &&
                (c.specialType === currencyToSubtract.specialType ||
                    (!c.specialType && !currencyToSubtract.specialType))
            );

            if (matchIndex >= 0 && result[matchIndex].amount >= currencyToSubtract.amount) {
                // Direct subtraction
                result[matchIndex].amount -= currencyToSubtract.amount;

                // Remove if zero
                if (result[matchIndex].amount === 0) {
                    result.splice(matchIndex, 1);
                }
            } else {
                // Need to convert currencies
                this.logInfo('Currency conversion needed for subtraction');

                // Implementation would handle conversion between currencies
                // This is complex and would require a separate function
                throw new Error('Complex currency conversion not implemented');
            }
        }

        return result;
    }

    /**
     * Calculate total value of currencies in gold equivalent
     */
    public calculateTotalValue(currencies: Currency[]): number {
        return currencies.reduce((total, currency) => {
            if (currency.type === CurrencyType.SPECIAL) {
                // Handle special currencies based on conversion rates
                if (this.conversionRates[CurrencyType.SPECIAL] &&
                    currency.specialType &&
                    this.conversionRates[CurrencyType.SPECIAL][currency.specialType]) {
                    return total + (currency.amount * this.conversionRates[CurrencyType.SPECIAL][currency.specialType]);
                }
                return total; // Ignore if no conversion rate
            }

            return total + (currency.amount * this.conversionRates[currency.type]);
        }, 0);
    }

    /**
     * Format currencies for display
     */
    public formatCurrencies(currencies: Currency[]): string {
        // Sort currencies by value
        const sorted = [...currencies].sort((a, b) => {
            const aValue = this.conversionRates[a.type] || 0;
            const bValue = this.conversionRates[b.type] || 0;
            return bValue - aValue; // Highest value first
        });

        return sorted.map(currency => {
            if (currency.type === CurrencyType.SPECIAL) {
                return `${currency.amount} ${currency.specialType || 'special'}`;
            }

            switch (currency.type) {
                case CurrencyType.GOLD:
                    return `${currency.amount}g`;
                case CurrencyType.SILVER:
                    return `${currency.amount}s`;
                case CurrencyType.COPPER:
                    return `${currency.amount}c`;
                default:
                    return `${currency.amount} ${currency.type}`;
            }
        }).join(' ');
    }

    /**
     * Break down a currency into smaller denominations
     */
    public breakdownCurrency(currency: Currency): Currency[] {
        if (currency.type === CurrencyType.SPECIAL) {
            // Special currencies can't be broken down
            return [{ ...currency }];
        }

        const result: Currency[] = [];

        // Convert to base units (copper)
        let totalCopper = 0;

        switch (currency.type) {
            case CurrencyType.GOLD:
                totalCopper = currency.amount * 10000;
                break;
            case CurrencyType.SILVER:
                totalCopper = currency.amount * 100;
                break;
            case CurrencyType.COPPER:
                totalCopper = currency.amount;
                break;
        }

        // Calculate gold
        const gold = Math.floor(totalCopper / 10000);
        if (gold > 0) {
            result.push({ type: CurrencyType.GOLD, amount: gold });
            totalCopper -= gold * 10000;
        }

        // Calculate silver
        const silver = Math.floor(totalCopper / 100);
        if (silver > 0) {
            result.push({ type: CurrencyType.SILVER, amount: silver });
            totalCopper -= silver * 100;
        }

        // Remaining copper
        if (totalCopper > 0) {
            result.push({ type: CurrencyType.COPPER, amount: totalCopper });
        }

        return result;
    }

    /**
     * Get regional price data
     */
    public async getRegionPriceData(regionId: string): Promise<RegionalPriceData | null> {
        const regions = await this.regionPriceRepository.findBy('regionId', regionId);
        return regions.length > 0 ? regions[0] : null;
    }

    /**
     * Modify item rarity-based value
     */
    public getRarityValueModifier(rarity: ItemRarity): number {
        switch (rarity) {
            case ItemRarity.COMMON:
                return 1.0;
            case ItemRarity.UNCOMMON:
                return 2.0;
            case ItemRarity.RARE:
                return 5.0;
            case ItemRarity.EPIC:
                return 15.0;
            case ItemRarity.LEGENDARY:
                return 50.0;
            case ItemRarity.UNIQUE:
                return 100.0;
            default:
                return 1.0;
        }
    }

    /**
     * Check and trigger merchant restocks
     */
    private async checkMerchantRestocks(): Promise<void> {
        this.logDebug('Checking for merchant restocks');

        const now = Date.now();
        const merchants = await this.merchantRepository.findAll();

        for (const merchant of merchants) {
            if (now - merchant.lastRestockTime >= merchant.restockInterval) {
                await this.restockMerchant(merchant.id);
            }
        }
    }

    /**
     * Restock a merchant's inventory
     */
    public async restockMerchant(merchantId: string): Promise<boolean> {
        this.logInfo(`Restocking merchant: ${merchantId}`);

        const merchant = await this.merchantRepository.findById(merchantId);
        if (!merchant) {
            this.logError(`Merchant not found: ${merchantId}`);
            return false;
        }

        // Update last restock time
        await this.merchantRepository.update(merchantId, {
            lastRestockTime: Date.now()
        });

        // Emit restock event - actual inventory changes will be handled by listeners
        await this.emitEvent({
            type: 'merchant:restocked',
            source: this.name,
            timestamp: Date.now(),
            data: { merchantId }
        });

        return true;
    }

    /**
     * Event handler for merchant created
     */
    private async handleMerchantCreated(event: SystemEvent): Promise<void> {
        const { merchant } = event.data;
        this.logDebug(`Handler: Merchant created - ${merchant.name}`);
    }

    /**
     * Event handler for merchant restocked
     */
    private async handleMerchantRestocked(event: SystemEvent): Promise<void> {
        const { merchantId } = event.data;
        this.logDebug(`Handler: Merchant restocked - ${merchantId}`);
    }

    /**
     * Event handler for region price changed
     */
    private async handleRegionPriceChanged(event: SystemEvent): Promise<void> {
        const { region } = event.data;
        this.logDebug(`Handler: Region price changed - ${region.name}`);
    }
} 