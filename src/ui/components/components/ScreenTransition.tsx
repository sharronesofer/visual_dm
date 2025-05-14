import React, { useEffect, useState } from 'react';
import { ScreenType } from '../utils/screenNavigation';
import styles from './ScreenTransition.module.css';

interface ScreenTransitionProps {
  currentScreen: ScreenType;
  previousScreen?: ScreenType;
  children: React.ReactNode;
  isTransitioning: boolean;
  onTransitionEnd?: () => void;
  className?: string;
}

export const ScreenTransition: React.FC<ScreenTransitionProps> = ({
  currentScreen,
  previousScreen,
  children,
  isTransitioning,
  onTransitionEnd,
  className = '',
}) => {
  const [direction, setDirection] = useState<'next' | 'prev'>('next');
  const [isExiting, setIsExiting] = useState(false);
  const [currentChildren, setCurrentChildren] = useState(children);

  useEffect(() => {
    if (!previousScreen || !currentScreen) return;

    // Determine transition direction based on screen order
    const screenOrder = Object.values(ScreenType);
    const prevIndex = screenOrder.indexOf(previousScreen);
    const currentIndex = screenOrder.indexOf(currentScreen);

    // Handle wrap-around cases
    if (prevIndex === screenOrder.length - 1 && currentIndex === 0) {
      setDirection('next');
    } else if (prevIndex === 0 && currentIndex === screenOrder.length - 1) {
      setDirection('prev');
    } else {
      setDirection(currentIndex > prevIndex ? 'next' : 'prev');
    }

    // Start exit animation
    setIsExiting(true);

    // After exit animation, update content and start enter animation
    const timeout = setTimeout(() => {
      setCurrentChildren(children);
      setIsExiting(false);
    }, 300); // Match this with CSS animation duration

    return () => clearTimeout(timeout);
  }, [currentScreen, previousScreen, children]);

  // Handle animation end
  const handleTransitionEnd = () => {
    if (!isExiting && onTransitionEnd) {
      onTransitionEnd();
    }
  };

  return (
    <div
      className={`${styles.transitionContainer} ${className}`}
      data-transitioning={isTransitioning}
      data-direction={direction}
      data-exiting={isExiting}
      onTransitionEnd={handleTransitionEnd}
      role="region"
      aria-label={`${currentScreen} screen`}
    >
      {currentChildren}
    </div>
  );
};
