# Economy System

This directory contains the integrated economy system for Visual DM. The economy system manages resources, trade routes, markets, and shops in the game world.

## Directory Structure

```
backend/systems/economy/
├── __init__.py              # Main module exports
├── README.md                # This documentation
├── config/                  # Configuration files
│   ├── price_modifiers.json # Price modifier configurations
│   └── player_economy.json  # Player economy balance settings
├── events/                  # Event system integration
│   ├── __init__.py          # Event exports
│   └── economy_events.py    # Economy event definitions
├── models/                  # Data models
│   ├── __init__.py          # Model exports
│   ├── resource.py          # Resource model
│   ├── trade_route.py       # Trade route model
│   ├── market.py            # Market model
│   └── commodity_future.py  # Futures contract model
├── resource/                # Legacy resource directory
│   └── __init__.py          # Resource exports
├── services/                # Business logic services
│   ├── __init__.py          # Service exports
│   ├── economy_manager.py   # Main economy manager (unified API)
│   ├── resource_service.py  # Resource management
│   ├── trade_service.py     # Trade route management
│   ├── market_service.py    # Market and pricing management
│   ├── futures_service.py   # Futures contract management
│   └── advanced_economy_service.py # Advanced economic features
└── utils/                   # Utility functions
    ├── __init__.py          # Utility exports
    ├── config_loader.py     # Configuration loading
    └── shop_utils.py        # Shop utilities (integrated with economy)
```

## Architecture

The economy system follows a clean, layered architecture:

1. **Models**: Data structures representing resources, trade routes, markets, and futures
2. **Services**: Business logic services with clear separation of concerns
3. **Manager**: Central unified API (EconomyManager) for accessing all economy functionality
4. **Configuration**: JSON-based configuration for economic parameters
5. **Events**: Integration with the game's event system
6. **Utilities**: Helper functions and shop integration

### Removed Legacy Components

As part of recent architecture cleanup, the following stub directories were removed:
- `market_service/` - Was a stub redirect to main services
- `economy_manager/` - Was a stub redirect to main services  
- `resource_service/` - Was a stub redirect to main services
- `schemas/` - Was empty with no implementation
- `repositories/` - Was empty with no implementation

All functionality is now consolidated in the main `services/` directory with clear, single-purpose service classes.

## Core Components

### Resources
Resources represent goods, materials, and assets within the economy.
- **Resource Types**: Raw materials, manufactured goods, food, luxury items, etc.
- **Properties**: Rarity, base value, weight, perishability
- **Location**: Resources are tied to specific regions

### Trade Routes
Trade routes facilitate the movement of resources between regions.
- **Properties**: Origin, destination, distance, safety, cost, capacity
- **Effects**: Regional resource availability, price stabilization

### Markets
Markets represent trading centers where resources are bought and sold.
- **Properties**: Size, specialty, tax rate
- **Pricing**: Dynamic pricing based on supply, demand, and market conditions

### Futures Contracts
Futures contracts allow entities to buy or sell resources at a predetermined price at a future date.
- **Properties**: Resource, quantity, strike price, expiration date
- **Types**: Standard futures, options, forward contracts
- **Uses**: Price speculation, hedging against price volatility

## Key Features

### Price Dynamics
- Dynamic pricing based on supply and demand
- Regional price variations
- Price modifiers from events and market conditions
- Price indices to track economic health

### Resource Flows
- Resource transfer between regions via trade routes
- Production and consumption rates affecting supply
- Resource shortages triggering economic events

### Economic Indicators
- Price indices showing regional economic health
- Market strength measurements
- Economic forecasts predicting future conditions
- Futures markets indicating expected future prices

### Taxation and Revenue
- Market taxation generating revenue
- Tax rates affecting market activity
- Revenue calculations and distribution

### Event-Based Effects
- Economic events (booms, busts, famines, etc.)
- Population-based consumption and production rates
- Regional competition and advantages
- Market disruptions from external events

### Futures Trading
- Creation and settlement of futures contracts
- Price forecasting based on futures market
- Risk management through contract structures
- Market speculation via futures positions

## Usage

The economy system is accessed through the `EconomyManager` class, which provides a unified API for all economy functionality:

```python
from backend.systems.economy.economy_manager import EconomyManager

# Get the economy manager instance
economy = EconomyManager.get_instance(db_session)

# Resource operations
resources = economy.get_resources_by_region(region_id)
resource = economy.create_resource(resource_data)

# Market operations
market = economy.get_market(market_id)
price, price_info = economy.calculate_price(resource_id, market_id, quantity)

# Trade operations
route = economy.create_trade_route(route_data)
trades_processed, events = economy.process_trade_routes()

# Economic indicators
price_index = economy.calculate_price_index(region_id=region_id)
forecast = economy.generate_economic_forecast(region_id)

# Futures operations
future = economy.create_future(future_data)
matched = economy.match_buyer(future_id, buyer_id)
settlement = economy.settle_future(future_id)
price_forecast = economy.forecast_future_prices(resource_id)

# Process economy for a game tick
results = economy.process_tick(tick_count)
```

## Shop API Routes

The shop API routes are fully integrated with EconomyManager:

```python
from backend.systems.economy import shop_bp

# Register shop API routes with Flask app
app.register_blueprint(shop_bp, url_prefix='/api/shops')
```

Available routes:
- POST `/sell_item_to_shop`: Sell an item to a shop
- GET `/get_shop_inventory/<shop_id>`: Get a shop's inventory
- POST `/buy_item_from_shop/<shop_id>`: Buy an item from a shop
- POST `/shops/preview_price`: Preview item price with modifiers
- GET `/view_shop_inventory/<npc_id>`: View shop inventory with filtering and sorting
- GET `/shops/view_inventory/<npc_id>`: Get simplified shop inventory
- POST `/restock_shop/<shop_id>`: Restock a shop with new items

## Shop Utilities

The shop utilities provide functions for shop operations:

```python
from backend.systems.economy import EconomyManager
from backend.systems.economy.shop_utils import calculate_sale_value, calculate_resale_value

# Get economy manager
economy = EconomyManager.get_instance(db_session)

# Calculate sale value with EconomyManager integration
sale_price = calculate_sale_value(item, player_level, economy)

# Calculate resale value with EconomyManager integration
resale_price = calculate_resale_value(item, player_level, economy)
```

## Integration Points

The economy system integrates with other game systems through:

1. **Event System**: Economic events are published to the central event system
2. **Population System**: Population changes affect resource consumption rates
3. **Faction System**: Faction decisions can impact trade routes and market conditions
4. **Region System**: Regional properties affect resource availability and market strength
5. **Time System**: Economic processes are advanced through game ticks

## Recent Refactoring

The economy system was recently refactored to:

1. **Remove Duplication**: Consolidated shop functionality with the EconomyManager
2. **Storage Consistency**: Moved from Firebase to SQLAlchemy for all data storage
3. **Integration**: Integrated shop API with the central economy system
4. **Error Handling**: Added comprehensive error handling and logging
5. **Model Integration**: Connected item data to the Resource model
6. **Functionality Preservation**: Maintained all previous functionality while removing duplication

The result is a more robust, consistent economy system with integrated shop functionality.
