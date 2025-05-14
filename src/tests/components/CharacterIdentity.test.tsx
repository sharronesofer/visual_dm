import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CharacterIdentity } from '../../components/CharacterCreation/steps/CharacterIdentity';
import { GPTService } from '../../services/GPTService';
import useCharacterStore from '../../stores/characterStore';
import { useWizardStore } from '../../stores/wizardStore';

// Mock the stores
jest.mock('../../stores/characterStore');
jest.mock('../../stores/wizardStore');

// Mock GPTService
jest.mock('../../services/GPTService', () => ({
  getInstance: jest.fn(() => ({
    generateNames: jest.fn(),
    generateBackground: jest.fn(),
  })),
}));

describe('CharacterIdentity', () => {
  const mockSetCharacter = jest.fn();
  const mockSetStepValidation = jest.fn();

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup store mocks
    (useCharacterStore as unknown as jest.Mock).mockReturnValue({
      character: {
        name: '',
        race: 'Elf',
        class: 'Wizard',
        alignment: '',
        background: '',
      },
      setCharacter: mockSetCharacter,
    });

    (useWizardStore as unknown as jest.Mock).mockReturnValue({
      setStepValidation: mockSetStepValidation,
    });
  });

  it('renders all form fields correctly', () => {
    render(<CharacterIdentity />);

    expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/alignment/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/background story/i)).toBeInTheDocument();
  });

  it('updates character name when input changes', () => {
    render(<CharacterIdentity />);

    const nameInput = screen.getByLabelText(/character name/i);
    fireEvent.change(nameInput, { target: { value: 'Gandalf' } });

    expect(mockSetCharacter).toHaveBeenCalledWith({ name: 'Gandalf' });
  });

  it('updates alignment when selection changes', () => {
    render(<CharacterIdentity />);

    const alignmentSelect = screen.getByLabelText(/alignment/i);
    fireEvent.mouseDown(alignmentSelect);

    const lawfulGoodOption = screen.getByText('Lawful Good');
    fireEvent.click(lawfulGoodOption);

    expect(mockSetCharacter).toHaveBeenCalledWith({ alignment: 'Lawful Good' });
  });

  it('validates fields and updates step validation', async () => {
    render(<CharacterIdentity />);

    // Fill in all required fields
    fireEvent.change(screen.getByLabelText(/character name/i), {
      target: { value: 'Gandalf' },
    });
    fireEvent.mouseDown(screen.getByLabelText(/alignment/i));
    fireEvent.click(screen.getByText('Lawful Good'));
    fireEvent.change(screen.getByLabelText(/background story/i), {
      target: { value: 'A wise wizard...' },
    });

    await waitFor(() => {
      expect(mockSetStepValidation).toHaveBeenCalledWith(0, true);
    });
  });

  it('handles name generation correctly', async () => {
    const mockGenerateNames = jest.fn().mockResolvedValue([
      { name: 'Elindor', description: 'Ancient elven name' },
      { name: 'Thalanil', description: 'Mystic sage name' },
    ]);

    GPTService.getInstance().generateNames = mockGenerateNames;

    render(<CharacterIdentity />);

    const generateButton = screen.getByText(/generate name suggestions/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(screen.getByText('Name Suggestions')).toBeInTheDocument();
      expect(screen.getByText('Elindor')).toBeInTheDocument();
      expect(screen.getByText('Thalanil')).toBeInTheDocument();
    });
  });

  it('handles background generation correctly', async () => {
    const mockGenerateBackground = jest
      .fn()
      .mockResolvedValue('A fascinating tale...');
    GPTService.getInstance().generateBackground = mockGenerateBackground;

    render(<CharacterIdentity />);

    // Fill required fields first
    fireEvent.change(screen.getByLabelText(/character name/i), {
      target: { value: 'Gandalf' },
    });

    const generateButton = screen.getByText(/generate background story/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(mockGenerateBackground).toHaveBeenCalled();
      expect(mockSetCharacter).toHaveBeenCalledWith({
        background: 'A fascinating tale...',
      });
    });
  });

  it('displays error state when name generation fails', async () => {
    const mockError = new Error('API Error');
    GPTService.getInstance().generateNames = jest
      .fn()
      .mockRejectedValue(mockError);

    render(<CharacterIdentity />);

    const generateButton = screen.getByText(/generate name suggestions/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(
        screen.getByText(/failed to generate name suggestions/i)
      ).toBeInTheDocument();
    });
  });

  it('displays error state when background generation fails', async () => {
    const mockError = new Error('API Error');
    GPTService.getInstance().generateBackground = jest
      .fn()
      .mockRejectedValue(mockError);

    render(<CharacterIdentity />);

    // Fill required fields first
    fireEvent.change(screen.getByLabelText(/character name/i), {
      target: { value: 'Gandalf' },
    });

    const generateButton = screen.getByText(/generate background story/i);
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(
        screen.getByText(/failed to generate background story/i)
      ).toBeInTheDocument();
    });
  });

  it('disables generation buttons when required fields are missing', () => {
    render(<CharacterIdentity />);

    const nameButton = screen.getByText(/generate name suggestions/i);
    const backgroundButton = screen.getByText(/generate background story/i);

    expect(nameButton).toBeDisabled();
    expect(backgroundButton).toBeDisabled();
  });
});
