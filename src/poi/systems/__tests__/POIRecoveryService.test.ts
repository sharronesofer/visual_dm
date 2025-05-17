import { describe, it, expect, vi, beforeEach } from 'vitest';
import { POIRecoveryService } from '../POIRecoveryService';

describe('POIRecoveryService', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it('validateData returns list of issues', async () => {
        const issues = await POIRecoveryService.validateData();
        expect(Array.isArray(issues)).toBe(true);
        expect(issues.length).toBeGreaterThan(0);
    });

    it('repairData logs and returns repairs', async () => {
        const spy = vi.spyOn(console, 'log').mockImplementation(() => { });
        const repairs = await POIRecoveryService.repairData();
        expect(Array.isArray(repairs)).toBe(true);
        expect(repairs.length).toBeGreaterThan(0);
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('[POIRecoveryService][Repair]'), expect.any(String));
    });

    it('orchestrateRecovery runs validation and repair', async () => {
        const spy = vi.spyOn(console, 'log').mockImplementation(() => { });
        await POIRecoveryService.orchestrateRecovery();
        expect(spy).toHaveBeenCalledWith('[POIRecoveryService] Starting orchestrated recovery...');
        expect(spy).toHaveBeenCalledWith('[POIRecoveryService] Recovery complete.');
    });
}); 