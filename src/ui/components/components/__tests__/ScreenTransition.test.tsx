import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { ScreenTransition } from '../ScreenTransition';
import { ScreenType } from '../../utils/screenNavigation';

describe('ScreenTransition', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders children content', () => {
    render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        isTransitioning={false}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies transition classes based on direction', () => {
    const { container, rerender } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        previousScreen={ScreenType.POI}
        isTransitioning={true}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;
    expect(transitionContainer.getAttribute('data-direction')).toBe('prev');

    rerender(
      <ScreenTransition
        currentScreen={ScreenType.POI}
        previousScreen={ScreenType.RegionMap}
        isTransitioning={true}
      >
        <div>New Content</div>
      </ScreenTransition>
    );

    expect(transitionContainer.getAttribute('data-direction')).toBe('next');
  });

  it('handles wrap-around transitions correctly', () => {
    const { container } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        previousScreen={ScreenType.Settings}
        isTransitioning={true}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;
    expect(transitionContainer.getAttribute('data-direction')).toBe('next');
  });

  it('calls onTransitionEnd after animation completes', () => {
    const onTransitionEnd = jest.fn();
    const { container } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        previousScreen={ScreenType.POI}
        isTransitioning={true}
        onTransitionEnd={onTransitionEnd}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;

    // Simulate transition end
    act(() => {
      transitionContainer.dispatchEvent(new Event('transitionend'));
      jest.runAllTimers();
    });

    expect(onTransitionEnd).toHaveBeenCalled();
  });

  it('updates content after exit animation', () => {
    const { container, rerender } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        isTransitioning={false}
      >
        <div>Initial Content</div>
      </ScreenTransition>
    );

    rerender(
      <ScreenTransition
        currentScreen={ScreenType.POI}
        previousScreen={ScreenType.RegionMap}
        isTransitioning={true}
      >
        <div>New Content</div>
      </ScreenTransition>
    );

    // Content should not update immediately
    expect(screen.queryByText('New Content')).not.toBeInTheDocument();

    // After animation timeout
    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(screen.getByText('New Content')).toBeInTheDocument();
  });

  it('disables interaction during transition', () => {
    const { container } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        isTransitioning={true}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;
    expect(transitionContainer.getAttribute('data-transitioning')).toBe('true');
    expect(window.getComputedStyle(transitionContainer).pointerEvents).toBe(
      'none'
    );
  });

  it('sets correct ARIA attributes', () => {
    const { container } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        isTransitioning={false}
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;
    expect(transitionContainer.getAttribute('role')).toBe('region');
    expect(transitionContainer.getAttribute('aria-label')).toBe(
      'REGION_MAP screen'
    );
  });

  it('applies custom className', () => {
    const { container } = render(
      <ScreenTransition
        currentScreen={ScreenType.RegionMap}
        isTransitioning={false}
        className="custom-class"
      >
        <div>Test Content</div>
      </ScreenTransition>
    );

    const transitionContainer = container.firstChild as HTMLElement;
    expect(transitionContainer.classList.contains('custom-class')).toBe(true);
  });
});
