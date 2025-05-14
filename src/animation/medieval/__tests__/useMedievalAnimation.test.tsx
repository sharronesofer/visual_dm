import { renderHook, act } from '@testing-library/react-hooks';
import { useMedievalAnimation } from '../useMedievalAnimation';
import { ANIMATION_TIMING } from '../constants';

describe('useMedievalAnimation', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useMedievalAnimation());

    expect(result.current.isAnimating).toBe(false);
    expect(result.current.progress).toBe(0);
    expect(result.current.foregroundStyle).toBeDefined();
    expect(result.current.backgroundStyle).toBeDefined();
  });

  it('should start animation when play is called', () => {
    const { result } = renderHook(() => useMedievalAnimation());

    act(() => {
      result.current.play();
    });

    expect(result.current.isAnimating).toBe(true);
  });

  it('should pause and resume animation', () => {
    const { result } = renderHook(() => useMedievalAnimation());

    act(() => {
      result.current.play();
      result.current.pause();
    });

    expect(result.current.isAnimating).toBe(false);

    act(() => {
      result.current.resume();
    });

    expect(result.current.isAnimating).toBe(true);
  });

  it('should reverse animation direction', () => {
    const { result } = renderHook(() => useMedievalAnimation());

    act(() => {
      result.current.play();
      result.current.reverse();
    });

    // The animation should still be playing but in reverse
    expect(result.current.isAnimating).toBe(true);
  });

  it('should call onComplete when animation finishes', async () => {
    const onComplete = jest.fn();
    const { result } = renderHook(() => 
      useMedievalAnimation({ 
        duration: ANIMATION_TIMING.DURATION.FAST,
        onComplete 
      })
    );

    act(() => {
      result.current.play();
    });

    // Fast forward through the animation
    act(() => {
      jest.advanceTimersByTime(ANIMATION_TIMING.DURATION.FAST);
    });

    expect(onComplete).toHaveBeenCalled();
  });

  it('should call onUpdate with progress', () => {
    const onUpdate = jest.fn();
    const { result } = renderHook(() => 
      useMedievalAnimation({ 
        duration: ANIMATION_TIMING.DURATION.FAST,
        onUpdate 
      })
    );

    act(() => {
      result.current.play();
    });

    // Fast forward halfway through the animation
    act(() => {
      jest.advanceTimersByTime(ANIMATION_TIMING.DURATION.FAST / 2);
    });

    expect(onUpdate).toHaveBeenCalledWith(expect.any(Number));
  });

  it('should apply custom timing', () => {
    const customDuration = 1000;
    const customEasing = 'ease-in-out';
    const customDelay = 200;

    const { result } = renderHook(() => 
      useMedievalAnimation({
        duration: customDuration,
        easing: customEasing,
        delay: customDelay
      })
    );

    act(() => {
      result.current.play();
    });

    // Animation should not start until after delay
    expect(result.current.progress).toBe(0);

    act(() => {
      jest.advanceTimersByTime(customDelay);
    });

    expect(result.current.isAnimating).toBe(true);
  });

  it('should provide performance metrics', () => {
    const { result } = renderHook(() => useMedievalAnimation());

    act(() => {
      result.current.play();
    });

    const metrics = result.current.getPerformanceMetrics();
    expect(metrics.averageFrameTime).toBeDefined();
    expect(metrics.averageFPS).toBeDefined();
    expect(metrics.frameCount).toBeDefined();
    expect(metrics.isPerformant).toBeDefined();
  });

  it('should cleanup on unmount', () => {
    const { unmount } = renderHook(() => useMedievalAnimation());
    
    unmount();
    // Should not throw any errors
  });
}); 