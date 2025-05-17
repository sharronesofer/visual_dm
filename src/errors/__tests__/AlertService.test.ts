import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AlertService, AlertSeverity } from '../AlertService';

describe('AlertService', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it('routes CRITICAL alerts to Slack', () => {
        const spy = vi.spyOn(console, 'log').mockImplementation(() => { });
        AlertService.sendAlert({ message: 'Critical error', severity: AlertSeverity.CRITICAL });
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('[ALERT][SLACK][CRITICAL]'), 'Critical error', '');
    });

    it('routes ERROR alerts to email', () => {
        const spy = vi.spyOn(console, 'log').mockImplementation(() => { });
        AlertService.sendAlert({ message: 'Error occurred', severity: AlertSeverity.ERROR });
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('[ALERT][EMAIL][ERROR]'), 'Error occurred', '');
    });

    it('routes INFO alerts to console', () => {
        const spy = vi.spyOn(console, 'error').mockImplementation(() => { });
        AlertService.sendAlert({ message: 'Info message', severity: AlertSeverity.INFO });
        expect(spy).toHaveBeenCalledWith(expect.stringContaining('[ALERT][INFO]'), 'Info message', '');
    });

    it('throttles duplicate alerts within window', () => {
        const spy = vi.spyOn(console, 'error').mockImplementation(() => { });
        AlertService.sendAlert({ message: 'Throttle me', severity: AlertSeverity.INFO });
        AlertService.sendAlert({ message: 'Throttle me', severity: AlertSeverity.INFO });
        expect(spy).toHaveBeenCalledTimes(1);
    });

    it('allows different messages through', () => {
        const spy = vi.spyOn(console, 'error').mockImplementation(() => { });
        AlertService.sendAlert({ message: 'Msg1', severity: AlertSeverity.INFO });
        AlertService.sendAlert({ message: 'Msg2', severity: AlertSeverity.INFO });
        expect(spy).toHaveBeenCalledTimes(2);
    });
}); 