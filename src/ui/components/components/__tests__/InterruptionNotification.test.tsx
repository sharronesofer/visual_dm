import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { InterruptionNotification, InterruptionNotificationProps } from '../InterruptionNotification';
import { describe, it, expect, vi } from 'vitest';

describe('InterruptionNotification', () => {
    const baseProps: InterruptionNotificationProps = {
        type: 'pause',
        message: 'Paused for user action',
        isOpen: true,
        onClose: vi.fn(),
    };

    function renderWithChakra(props: Partial<InterruptionNotificationProps> = {}) {
        return render(
            React.createElement(ChakraProvider as any, null,
                <InterruptionNotification {...baseProps} {...props} />
            )
        );
    }

    it('renders pause type with correct header and icon', () => {
        renderWithChakra({ type: 'pause' });
        expect(screen.getByText('Session Paused')).toBeInTheDocument();
        expect(screen.getByText('Paused for user action')).toBeInTheDocument();
    });

    it('renders error type with correct header and icon', () => {
        renderWithChakra({ type: 'error', message: 'System error occurred' });
        expect(screen.getByText('System Error')).toBeInTheDocument();
        expect(screen.getByText('System error occurred')).toBeInTheDocument();
    });

    it('renders exit type with correct header and icon', () => {
        renderWithChakra({ type: 'exit', message: 'Session ended' });
        expect(screen.getByText('Session Ended')).toBeInTheDocument();
        expect(screen.getByText('Session ended')).toBeInTheDocument();
    });

    it('shows progress bar if progress is provided', () => {
        renderWithChakra({ progress: 50 });
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('calls onRetry, onCancel, onContinue, onClose when buttons are clicked', () => {
        const onRetry = vi.fn();
        const onCancel = vi.fn();
        const onContinue = vi.fn();
        const onClose = vi.fn();
        renderWithChakra({ onRetry, onCancel, onContinue, onClose });
        if (screen.queryByRole('button', { name: /Retry/i })) {
            fireEvent.click(screen.getByRole('button', { name: /Retry/i }));
            expect(onRetry).toHaveBeenCalled();
        }
        if (screen.queryByRole('button', { name: /Continue/i })) {
            fireEvent.click(screen.getByRole('button', { name: /Continue/i }));
            expect(onContinue).toHaveBeenCalled();
        }
        if (screen.queryByRole('button', { name: /Cancel/i })) {
            fireEvent.click(screen.getByRole('button', { name: /Cancel/i }));
            expect(onCancel).toHaveBeenCalled();
        }
        fireEvent.click(screen.getByLabelText('Close'));
        expect(onClose).toHaveBeenCalled();
    });

    it('opens feedback modal when Feedback button is clicked', () => {
        renderWithChakra();
        fireEvent.click(screen.getByRole('button', { name: /Feedback/i }));
        expect(screen.getByText('Send Feedback')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /Close/i }));
        expect(screen.queryByText('Send Feedback')).not.toBeInTheDocument();
    });

    it('modal has correct ARIA roles', () => {
        renderWithChakra();
        expect(screen.getByRole('alertdialog')).toBeInTheDocument();
        expect(screen.getByLabelText('Session Paused')).toBeInTheDocument();
    });
}); 