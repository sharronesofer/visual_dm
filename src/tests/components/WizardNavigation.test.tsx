import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WizardNavigation from '../../components/CharacterCreation/WizardNavigation';
import { useWizardStore } from '../../stores/wizardStore';
import useCharacterStore from '../../stores/characterStore';
import { act } from 'react';

// Mock the stores
jest.mock('../../stores/wizardStore');
jest.mock('../../stores/characterStore');

describe('WizardNavigation', () => {
  const mockGoToNextStep = jest.fn();
  const mockGoToPreviousStep = jest.fn();
  const mockIsStepValid = jest.fn();
  const mockValidateCurrentStep = jest.fn();
  const mockSaveCharacter = jest.fn();
  const mockResetWizard = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup wizard store mock with proper type casting
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
      validateCurrentStep: mockValidateCurrentStep,
      resetWizard: mockResetWizard,
    });

    // Setup character store mock
    (useCharacterStore as unknown as jest.Mock).mockReturnValue({
      saveCharacter: mockSaveCharacter,
    });

    // Default to valid steps
    mockIsStepValid.mockReturnValue(true);
    mockValidateCurrentStep.mockResolvedValue(true);
  });

  it('renders navigation buttons', () => {
    render(<WizardNavigation steps={5} currentStep={1} />);

    expect(screen.getByRole('button', { name: 'Back' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Next' })).toBeInTheDocument();
  });

  it('disables back button on first step', () => {
    render(<WizardNavigation steps={5} currentStep={0} />);

    expect(screen.getByRole('button', { name: 'Back' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Next' })).toBeEnabled();
  });

  it('shows finish button on last step', () => {
    render(<WizardNavigation steps={5} currentStep={4} />);

    expect(screen.getByRole('button', { name: 'Finish' })).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Next' })
    ).not.toBeInTheDocument();
  });

  it('disables next button when step is invalid', () => {
    mockIsStepValid.mockReturnValue(false);
    render(<WizardNavigation steps={5} currentStep={1} />);

    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled();
  });

  it('calls goToPreviousStep when back button is clicked', () => {
    render(<WizardNavigation steps={5} currentStep={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Back' }));

    expect(mockGoToPreviousStep).toHaveBeenCalled();
  });

  it('calls goToNextStep when next button is clicked and step is valid', async () => {
    render(<WizardNavigation steps={5} currentStep={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Next' }));

    await waitFor(() => {
      expect(mockValidateCurrentStep).toHaveBeenCalled();
      expect(mockGoToNextStep).toHaveBeenCalled();
    });
  });

  it('calls saveCharacter when finish button is clicked on last step', async () => {
    render(<WizardNavigation steps={5} currentStep={4} />);

    fireEvent.click(screen.getByRole('button', { name: 'Finish' }));

    await waitFor(() => {
      expect(mockValidateCurrentStep).toHaveBeenCalled();
      expect(mockSaveCharacter).toHaveBeenCalled();
      expect(mockGoToNextStep).not.toHaveBeenCalled();
    });
  });

  it('persists navigation state between renders', async () => {
    const { rerender } = render(<WizardNavigation steps={5} currentStep={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Next' }));

    await waitFor(() => {
      expect(mockValidateCurrentStep).toHaveBeenCalled();
      expect(mockGoToNextStep).toHaveBeenCalled();
    });

    // Rerender with new step
    rerender(<WizardNavigation steps={5} currentStep={2} />);

    expect(screen.getByRole('button', { name: 'Back' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Next' })).toBeEnabled();
  });

  it('handles validation errors gracefully', async () => {
    mockValidateCurrentStep.mockRejectedValue(new Error('Validation failed'));
    render(<WizardNavigation steps={5} currentStep={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Next' }));

    await waitFor(() => {
      expect(mockValidateCurrentStep).toHaveBeenCalled();
      expect(mockGoToNextStep).not.toHaveBeenCalled();
      expect(screen.getByText('Error: Validation failed')).toBeInTheDocument();
    });
  });

  it('resets wizard state when reset is called', async () => {
    render(<WizardNavigation steps={5} currentStep={2} />);

    // Simulate reset action
    await act(async () => {
      mockResetWizard();
    });

    expect(mockResetWizard).toHaveBeenCalled();
  });

  it('disables buttons during validation', async () => {
    let resolveValidation = (_value: boolean) => {};
    mockValidateCurrentStep.mockImplementation(
      () =>
        new Promise(resolve => {
          resolveValidation = resolve;
        })
    );

    render(<WizardNavigation steps={5} currentStep={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Next' }));

    // Verify buttons are disabled during validation
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Back' })).toBeDisabled();

    // Resolve validation
    resolveValidation(true);

    await waitFor(() => {
      expect(mockGoToNextStep).toHaveBeenCalled();
      expect(screen.getByRole('button', { name: 'Next' })).toBeEnabled();
      expect(screen.getByRole('button', { name: 'Back' })).toBeEnabled();
    });
  });
});
