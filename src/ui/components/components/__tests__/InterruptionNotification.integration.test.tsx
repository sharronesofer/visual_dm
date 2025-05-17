import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
// @ts-expect-error: TypeScript path resolution false positive
import { useInteractionStore, setInterruptionState, clearInterruptionState, InterruptionState } from '../../../store/core/interactionStore';
import InterruptionNotificationContainer from '../InterruptionNotification';
import { describe, it, expect, vi } from 'vitest';

describe('InterruptionNotificationContainer integration', () => {
    function renderApp() {
        return render(
            React.createElement(ChakraProvider as any, null,
                <InterruptionNotificationContainer />
            )
        );
    }

    it('shows modal on interruption and handles user actions', async () => {
        renderApp();
        // Simulate interruption
        await act(async () => {
            await useInteractionStore.getState().dispatch(setInterruptionState(InterruptionState.SYSTEM_ERROR, 'Test error', { foo: 'bar' }));
        });
        expect(screen.getByRole('alertdialog')).toBeInTheDocument();
        expect(screen.getByText('System Error')).toBeInTheDocument();
        expect(screen.getByText('Test error')).toBeInTheDocument();

        // Simulate Retry
        const retryBtn = screen.getByRole('button', { name: /Retry/i });
        expect(retryBtn).toBeInTheDocument();
        await act(async () => {
            fireEvent.click(retryBtn);
        });
        // Progress bar should appear (loading state)
        expect(screen.getByRole('progressbar')).toBeInTheDocument();

        // Simulate Cancel
        const cancelBtn = screen.getByRole('button', { name: /Cancel/i });
        expect(cancelBtn).toBeInTheDocument();
        fireEvent.click(cancelBtn);
        // TODO: Verify store action (when implemented)

        // Simulate Continue
        const continueBtn = screen.getByRole('button', { name: /Continue/i });
        expect(continueBtn).toBeInTheDocument();
        fireEvent.click(continueBtn);
        // TODO: Verify store action (when implemented)

        // Simulate Close
        const closeBtn = screen.getByLabelText('Close');
        fireEvent.click(closeBtn);
        // TODO: Verify store action (when implemented)

        // Simulate clearing interruption
        await act(async () => {
            await useInteractionStore.getState().dispatch(clearInterruptionState());
        });
        expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
    });

    it('modal is accessible', async () => {
        renderApp();
        await act(async () => {
            await useInteractionStore.getState().dispatch(setInterruptionState(InterruptionState.TEMPORARY_PAUSE, 'Paused for test'));
        });
        const modal = screen.getByRole('alertdialog');
        expect(modal).toHaveAttribute('aria-modal', 'true');
        expect(modal).toHaveAttribute('aria-labelledby');
    });
}); 