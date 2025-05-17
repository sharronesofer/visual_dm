export enum ResourceType {
  FOOD = 'FOOD',
  WOOD = 'WOOD',
  STONE = 'STONE',
  METAL = 'METAL',
  CLOTH = 'CLOTH',
  LEATHER = 'LEATHER',
  HERBS = 'HERBS',
  GEMS = 'GEMS',
  MAGIC = 'MAGIC'
}

export enum ProductType {
  WEAPON = 'WEAPON',
  ARMOR = 'ARMOR',
  TOOL = 'TOOL',
  POTION = 'POTION',
  CLOTHING = 'CLOTHING',
  FURNITURE = 'FURNITURE',
  JEWELRY = 'JEWELRY',
  SCROLL = 'SCROLL'
}

export interface ResourceData {
  type: ResourceType;
  name: string;
  baseValue: number;
  weight: number;
  perishable: boolean;
  shelfLife?: number; // Time in milliseconds before perishing
}

export interface ProductData {
  type: ProductType;
  name: string;
  baseValue: number;
  weight: number;
  quality: number; // 0-100
  durability: number; // 0-100
  ingredients: Map<ResourceType, number>;
}

export interface MarketData {
  id: string;
  name: string;
  location: { x: number; y: number };
  schedule: {
    openTime: number; // Hour of day (0-23)
    closeTime: number;
    openDays: number[]; // Days of week (0-6)
  };
  specialization?: ProductType[];
  reputation: number; // 0-100
  lastUpdated: number;
}

export interface TradeOffer {
  id: string;
  sellerId: string;
  itemType: ResourceType | ProductType;
  quantity: number;
  pricePerUnit: number;
  expiresAt: number;
  minimumQuantity?: number;
  negotiable: boolean;
}

export interface Transaction {
  id: string;
  timestamp: number;
  buyerId: string;
  sellerId: string;
  itemType: ResourceType | ProductType;
  quantity: number;
  pricePerUnit: number;
  marketId?: string;
}

export interface ProductionRecipe {
  output: {
    type: ProductType;
    quantity: number;
    baseQuality: number;
  };
  inputs: Map<ResourceType, number>;
  toolRequirements?: ProductType[];
  skillRequirements?: Map<string, number>;
  productionTime: number; // Time in milliseconds
  failureChance: number; // 0-1
}

export interface EconomicRole {
  type: string;
  productionRecipes?: ProductionRecipe[];
  tradingPreferences?: {
    preferredResources: ResourceType[];
    preferredProducts: ProductType[];
    priceMarkup: number; // Percentage above base value
    negotiationFlexibility: number; // 0-1
  };
  workSchedule?: {
    startHour: number;
    endHour: number;
    workDays: number[];
  };
}

export interface EconomicAgent {
  id: string;
  role: EconomicRole;
  inventory: Map<string, number>; // ResourceType/ProductType -> quantity
  currency: number;
  reputation: number; // 0-100
  activeOffers: Set<string>;
  productionQueue: {
    recipeId: string;
    startedAt: number;
    completesAt: number;
    inputs: Map<string, number>;
  }[];
  lastTransaction: number;
}

export interface PriceStats {
  averagePrice: number;
  medianPrice: number;
  minPrice: number;
  maxPrice: number;
  numTransactions: number;
}

export interface MarketPriceData {
  itemType: ResourceType | ProductType;
  averagePrice: number;
  minPrice: number;
  maxPrice: number;
  volume: number;
  trend: number;
  lastUpdate: number;
}

export interface EconomicEvent {
  type: string;
  affectedItems: (ResourceType | ProductType)[];
  multiplier: number; // Effect on prices/availability
  duration: number; // Time in milliseconds
  scope: {
    marketIds?: string[];
    regionIds?: string[];
    global: boolean;
  };
  startTime: number;
  description: string;
}

// --- Bundled/Multi-Item Trade Support ---

/**
 * Represents a bundled trade offer containing multiple items as a single atomic package.
 */
export interface BundledTradeOffer {
  id: string;
  sellerId: string;
  items: Array<{
    itemType: ResourceType | ProductType;
    quantity: number;
    pricePerUnit: number;
    minimumQuantity?: number;
    negotiable?: boolean;
  }>;
  totalPrice: number; // Total price for the bundle (could be sum or discounted)
  expiresAt: number;
  negotiable: boolean;
}

/**
 * Represents a bundled transaction for multiple items traded atomically.
 */
export interface BundledTransaction {
  id: string;
  timestamp: number;
  buyerId: string;
  sellerId: string;
  items: Array<{
    itemType: ResourceType | ProductType;
    quantity: number;
    pricePerUnit: number;
  }>;
  totalPrice: number;
  marketId?: string;
} 