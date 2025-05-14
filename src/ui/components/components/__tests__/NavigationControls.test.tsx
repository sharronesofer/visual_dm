import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { NavigationControls } from '../NavigationControls';
import { useNavigation } from '../../hooks/useNavigation';
import { ScreenType } from '../../utils/screenNavigation';

// Mock the useNavigation hook
jest.mock('../../hooks/useNavigation');

describe('NavigationControls', () => {
  const mockNavigateToNext = jest.fn();
  const mockNavigateToPrevious = jest.fn();
  const mockNavigateTo = jest.fn();
  const mockGetAccessibleScreens = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useNavigation as jest.Mock).mockReturnValue({
      currentScreen: ScreenType.RegionMap,
      isTransitioning: false,
      navigateToNext: mockNavigateToNext,
      navigateToPrevious: mockNavigateToPrevious,
      navigateTo: mockNavigateTo,
      getAccessibleScreens: mockGetAccessibleScreens.mockReturnValue([
        ScreenType.RegionMap,
        ScreenType.POI,
        ScreenType.Settings,
      ]),
    });
  });

  it('renders navigation buttons', () => {
    render(<NavigationControls />);

    expect(screen.getByLabelText('Previous Screen')).toBeInTheDocument();
    expect(screen.getByLabelText('Next Screen')).toBeInTheDocument();
    expect(screen.getAllByRole('button')).toHaveLength(5); // 2 nav buttons + 3 screen buttons
  });

  it('calls navigateToNext when next button is clicked', () => {
    render(<NavigationControls />);

    fireEvent.click(screen.getByLabelText('Next Screen'));
    expect(mockNavigateToNext).toHaveBeenCalledWith({ animate: true });
  });

  it('calls navigateToPrevious when previous button is clicked', () => {
    render(<NavigationControls />);

    fireEvent.click(screen.getByLabelText('Previous Screen'));
    expect(mockNavigateToPrevious).toHaveBeenCalledWith({ animate: true });
  });

  it('disables buttons during transition', () => {
    (useNavigation as jest.Mock).mockReturnValue({
      currentScreen: ScreenType.RegionMap,
      isTransitioning: true,
      navigateToNext: mockNavigateToNext,
      navigateToPrevious: mockNavigateToPrevious,
      navigateTo: mockNavigateTo,
      getAccessibleScreens: mockGetAccessibleScreens.mockReturnValue([
        ScreenType.RegionMap,
        ScreenType.POI,
      ]),
    });

    render(<NavigationControls />);

    expect(screen.getByLabelText('Next Screen')).toBeDisabled();
    expect(screen.getByLabelText('Previous Screen')).toBeDisabled();
  });

  it('handles keyboard navigation', () => {
    render(<NavigationControls />);

    fireEvent.keyDown(window, { key: 'ArrowRight' });
    expect(mockNavigateToNext).toHaveBeenCalledWith({ animate: true });

    fireEvent.keyDown(window, { key: 'ArrowLeft' });
    expect(mockNavigateToPrevious).toHaveBeenCalledWith({ animate: true });

    fireEvent.keyDown(window, { key: 'Tab' });
    expect(mockNavigateToNext).toHaveBeenCalledWith({ animate: true });

    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(mockNavigateToPrevious).toHaveBeenCalledWith({ animate: true });
  });

  it('disables inaccessible screen buttons', () => {
    mockGetAccessibleScreens.mockReturnValue([ScreenType.RegionMap]);

    render(<NavigationControls />);

    const buttons = screen.getAllByRole('button');
    const screenButtons = buttons.filter(
      button =>
        !['Previous Screen', 'Next Screen'].includes(
          button.getAttribute('aria-label') || ''
        )
    );

    screenButtons.forEach(button => {
      if (button.textContent === 'REGION MAP') {
        expect(button).not.toBeDisabled();
      } else {
        expect(button).toBeDisabled();
      }
    });
  });

  it('calls onScreenChange when screen changes', () => {
    const mockOnScreenChange = jest.fn();
    render(<NavigationControls onScreenChange={mockOnScreenChange} />);

    expect(mockOnScreenChange).toHaveBeenCalledWith(ScreenType.RegionMap);
  });

  it('applies custom className', () => {
    render(<NavigationControls className="custom-class" />);

    expect(screen.getByRole('navigation')).toHaveClass('custom-class');
  });
});
