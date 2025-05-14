import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { WizardStepRenderer } from '../../components/CharacterCreation/WizardStepRenderer';
import { useWizardStore } from '../../stores/wizardStore';
import { wizardSteps } from '../../config/wizardSteps';

// Mock the wizard store
jest.mock('../../stores/wizardStore');

describe('WizardStepRenderer', () => {
  const mockGoToNextStep = jest.fn();
  const mockGoToPreviousStep = jest.fn();
  const mockIsStepValid = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup store mock with proper type casting
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      currentStep: 0,
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
    });
  });

  it('renders the current step component', () => {
    mockIsStepValid.mockReturnValue(true);
    render(<WizardStepRenderer />);

    // Verify stepper labels are rendered
    wizardSteps.forEach(step => {
      expect(screen.getByText(step.title)).toBeInTheDocument();
    });

    // Verify current step component is rendered
    const CurrentStepComponent = wizardSteps[0].component;
    expect(screen.getByRole('button', { name: 'Next' })).toBeInTheDocument();
  });

  it('handles navigation correctly', () => {
    mockIsStepValid.mockReturnValue(true);
    render(<WizardStepRenderer />);

    // Click next button
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(mockGoToNextStep).toHaveBeenCalled();

    // Update current step to 1
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      currentStep: 1,
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
    });

    // Click back button
    fireEvent.click(screen.getByRole('button', { name: 'Back' }));
    expect(mockGoToPreviousStep).toHaveBeenCalled();
  });

  it('disables navigation when step is invalid', () => {
    mockIsStepValid.mockReturnValue(false);
    render(<WizardStepRenderer />);

    // Verify next button is disabled
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled();
  });

  it('disables back button on first step', () => {
    mockIsStepValid.mockReturnValue(true);
    render(<WizardStepRenderer />);

    // Verify back button is disabled on first step
    expect(screen.getByRole('button', { name: 'Back' })).toBeDisabled();
  });

  it('shows finish button on second-to-last step', () => {
    mockIsStepValid.mockReturnValue(true);

    // Set current step to second-to-last step
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      currentStep: wizardSteps.length - 2,
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
    });

    render(<WizardStepRenderer />);

    // Verify finish button is shown
    expect(screen.getByRole('button', { name: 'Finish' })).toBeInTheDocument();
  });

  it('handles missing step component gracefully', () => {
    mockIsStepValid.mockReturnValue(true);

    // Mock invalid step index
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      currentStep: 999,
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
    });

    render(<WizardStepRenderer />);

    // Verify error message is shown
    expect(screen.getByText('Error: Step not found')).toBeInTheDocument();
  });

  it('updates step validation on component mount', () => {
    mockIsStepValid.mockReturnValue(true);
    render(<WizardStepRenderer />);

    // Verify validation is checked on mount
    expect(mockIsStepValid).toHaveBeenCalledWith(0);
  });

  it('updates step validation when current step changes', () => {
    mockIsStepValid.mockReturnValue(true);
    const { rerender } = render(<WizardStepRenderer />);

    // Change current step
    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      currentStep: 1,
      goToNextStep: mockGoToNextStep,
      goToPreviousStep: mockGoToPreviousStep,
      isStepValid: mockIsStepValid,
    });

    rerender(<WizardStepRenderer />);

    // Verify validation is checked for new step
    expect(mockIsStepValid).toHaveBeenCalledWith(1);
  });
});
