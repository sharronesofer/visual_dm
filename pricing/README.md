# Supply/Demand Curve Module

This module provides the core logic for dynamic pricing based on supply and demand using a configurable sigmoid curve and time-weighted averaging.

## Usage

Import the functions and parameter types:

```typescript
import { calculatePrice, calculateWeightedDemand, CurveParams, PriceInput } from './supplyDemandCurve';
import { defaultCurveParams } from './curveConfig';
```

### Example

```typescript
const previousWeightedDemand = 50;
const recentTransactions = 60;
const inventoryLevel = 40;
const params = { ...defaultCurveParams, basePrice: 120 };

const price = calculatePrice({
  inventoryLevel,
  recentTransactions,
  previousWeightedDemand,
  params
});
console.log('Calculated price:', price);
```

## Parameter Reference

- **basePrice**: The baseline price for the item.
- **k**: Maximum adjustment factor (e.g., 0.5 = up to 50% increase).
- **a**: Steepness of the sigmoid curve (higher = more sensitive to demand/supply changes).
- **equilibrium**: Offset for the demand-supply balance point.
- **decayAlpha**: Time-weighting factor for demand averaging (0 = slow, 1 = instant).

## Edge Case Handling
- For new or rarely traded items, the function returns the base price.
- Price is always >= 0.01.

## Testing
- Unit tests should cover a range of supply/demand scenarios, including edge cases.

## Theory
The price is calculated as:

```
price = basePrice * (1 + k / (1 + exp(-a * (weightedDemand - inventoryLevel - equilibrium))))
```

Weighted demand is calculated as:

```
weightedDemand = currentDemand * alpha + previousWeighted * (1 - alpha)
``` 