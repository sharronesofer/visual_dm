import { ValidationService, ValidationSeverity, ValidationContext } from '../ValidationService';
import * as rules from '../validationRules';
import { EventBus } from '../../events/EventBus';
import { SceneEventType } from '../../events/SceneEventTypes';
import { ErrorHandlingService } from '../ErrorHandlingService';
import { jest } from '@jest/globals';

describe('Validation Framework', () => {
    let validationService: ValidationService;
    let eventBusEmitSpy: jest.SpyInstance;
    let errorLogSpy: jest.SpyInstance;

    beforeEach(() => {
        validationService = ValidationService.getInstance();
        eventBusEmitSpy = jest.spyOn(EventBus.getInstance(), 'emit').mockImplementation(async () => true);
        errorLogSpy = jest.spyOn(ErrorHandlingService.getInstance(), 'logError').mockImplementation(() => { });
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Unit: Validation Rules', () => {
        it('NoNegativeBalanceRule: fails on negative balances', () => {
            const rule = new rules.NoNegativeBalanceRule();
            expect(rule.validate({ fromAgent: { currency: -1 } })).toBe(false);
            expect(rule.validate({ toAgent: { currency: -5 } })).toBe(false);
            expect(rule.validate({ fromAgent: { currency: 10 }, toAgent: { currency: 0 } })).toBe(true);
        });
        it('SufficientFundsRule: fails if not enough funds', () => {
            const rule = new rules.SufficientFundsRule();
            expect(rule.validate({ fromAgent: { currency: 5 }, amount: 10 })).toBe(false);
            expect(rule.validate({ fromAgent: { currency: 20 }, amount: 10 })).toBe(true);
        });
        it('ReputationBoundsRule: enforces 0-100', () => {
            const rule = new rules.ReputationBoundsRule();
            expect(rule.validate({ agent: { reputation: 50 }, delta: 60 })).toBe(false);
            expect(rule.validate({ agent: { reputation: 50 }, delta: -60 })).toBe(false);
            expect(rule.validate({ agent: { reputation: 50 }, delta: 0 })).toBe(true);
        });
        it('InventorySlotLimitRule: fails if no empty slot', () => {
            const rule = new rules.InventorySlotLimitRule();
            expect(rule.validate({ inventory: { slots: [{ itemId: 'a' }, { itemId: 'b' }] } })).toBe(false);
            expect(rule.validate({ inventory: { slots: [{ itemId: null }, { itemId: 'b' }] } })).toBe(true);
        });
        it('InventoryWeightLimitRule: fails if over weight', () => {
            const rule = new rules.InventoryWeightLimitRule();
            expect(rule.validate({ inventory: { currentWeight: 10, maxWeight: 15 }, item: { weight: 10 }, quantity: 1 })).toBe(false);
            expect(rule.validate({ inventory: { currentWeight: 5, maxWeight: 15 }, item: { weight: 5 }, quantity: 2 })).toBe(true);
        });
        it('ValidItemRule: fails if item is missing', () => {
            const rule = new rules.ValidItemRule();
            expect(rule.validate({})).toBe(false);
            expect(rule.validate({ item: { id: 'x' } })).toBe(true);
        });
    });

    describe('Integration: ValidationService', () => {
        it('validateSync adds errors and emits events', () => {
            const context = validationService.validateSync('economic', { fromAgent: { currency: -1 }, toAgent: { currency: 10 }, amount: 5 });
            expect(context.errors.length).toBeGreaterThan(0);
            expect(eventBusEmitSpy).toHaveBeenCalledWith(expect.objectContaining({ type: SceneEventType.VALIDATION_EVENT }));
            expect(errorLogSpy).toHaveBeenCalled();
        });
        it('validateAsync adds errors and emits events', async () => {
            const context = await validationService.validateAsync('economic', { fromAgent: { currency: -1 }, toAgent: { currency: 10 }, amount: 5 });
            expect(context.errors.length).toBeGreaterThan(0);
            expect(eventBusEmitSpy).toHaveBeenCalledWith(expect.objectContaining({ type: SceneEventType.VALIDATION_EVENT }));
            expect(errorLogSpy).toHaveBeenCalled();
        });
    });

    describe('Cross-System Consistency', () => {
        it('EconomicInventoryConsistencyRule calls ConsistencyChecker', async () => {
            const rule = new rules.EconomicInventoryConsistencyRule();
            const checker = require('../ValidationService');
            const spy = jest.spyOn(checker.ConsistencyChecker, 'checkEconomicInventory').mockResolvedValue(true);
            await expect(rule.validate({ economicData: {}, inventoryData: {} })).resolves.toBe(true);
            spy.mockRestore();
        });
    });
}); 