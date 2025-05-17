/**
 * Default configuration for supply/demand curve parameters.
 */
import { CurveParams } from './supplyDemandCurve';

export const defaultCurveParams: CurveParams = {
    basePrice: 100,
    k: 0.5, // max 50% price adjustment
    a: 0.1, // moderate steepness
    equilibrium: 0, // no offset by default
    decayAlpha: 0.3 // moderate time-weighting
}; 