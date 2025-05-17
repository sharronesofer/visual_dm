import { expect } from 'chai';
import { ErrorCategory } from '../ErrorCategory';
import { ErrorMessage, SeverityLevel } from '../ErrorMessage';
import { ErrorSuggestion } from '../ErrorSuggestion';
import { ErrorEventSystem } from '../ErrorEventSystem';
import { ErrorVisualizer } from '../ErrorVisualizer';

describe('Error System', () => {
    it('creates error messages with correct fields', () => {
        const error = new ErrorMessage(
            ErrorCategory.INVALID_TARGET,
            SeverityLevel.ERROR,
            'Invalid target selected.',
            'Select a valid target.',
            { action: 'attack' }
        );
        expect(error.category).to.equal(ErrorCategory.INVALID_TARGET);
        expect(error.severity).to.equal(SeverityLevel.ERROR);
        expect(error.description).to.include('Invalid target');
        expect(error.suggestion).to.include('valid target');
        expect(error.metadata?.action).to.equal('attack');
    });

    it('suggests alternatives based on error category', () => {
        expect(ErrorSuggestion.suggest(ErrorCategory.INSUFFICIENT_RESOURCES)).to.include('replenish');
        expect(ErrorSuggestion.suggest(ErrorCategory.COOLDOWN_ACTIVE)).to.include('cooldown');
    });

    it('dispatches and receives error events', () => {
        const error = new ErrorMessage(
            ErrorCategory.STATE_CONFLICT,
            SeverityLevel.WARNING,
            'State conflict detected.'
        );
        let received = false;
        const listener = (err: ErrorMessage) => { received = true; };
        ErrorEventSystem.subscribe(listener, ErrorCategory.STATE_CONFLICT);
        ErrorEventSystem.dispatch(error);
        expect(received).to.equal(true);
        ErrorEventSystem.unsubscribe(listener, ErrorCategory.STATE_CONFLICT);
    });

    it('prints error to console', () => {
        const error = new ErrorMessage(
            ErrorCategory.PERMISSION_DENIED,
            SeverityLevel.CRITICAL,
            'Permission denied.'
        );
        ErrorVisualizer.printToConsole(error);
    });
}); 