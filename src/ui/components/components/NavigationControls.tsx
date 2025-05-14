import React, { useCallback, useEffect } from 'react';
import { useNavigation } from '../hooks/useNavigation';
import { ScreenType } from '../utils/screenNavigation';
import styles from './NavigationControls.module.css';

interface NavigationControlsProps {
  onScreenChange?: (screen: ScreenType) => void;
  className?: string;
}

export const NavigationControls: React.FC<NavigationControlsProps> = ({
  onScreenChange,
  className = '',
}) => {
  const {
    currentScreen,
    isTransitioning,
    navigateToNext,
    navigateToPrevious,
    navigateTo,
    getAccessibleScreens,
  } = useNavigation();

  useEffect(() => {
    onScreenChange?.(currentScreen);
  }, [currentScreen, onScreenChange]);

  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      if (isTransitioning) return;

      switch (event.key) {
        case 'ArrowRight':
        case 'Tab':
          if (!event.shiftKey) {
            event.preventDefault();
            navigateToNext({ animate: true });
          }
          break;
        case 'ArrowLeft':
          event.preventDefault();
          navigateToPrevious({ animate: true });
          break;
        case 'Tab':
          if (event.shiftKey) {
            event.preventDefault();
            navigateToPrevious({ animate: true });
          }
          break;
      }
    },
    [isTransitioning, navigateToNext, navigateToPrevious]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);

  const accessibleScreens = getAccessibleScreens();

  return (
    <nav
      className={`${styles.navigationControls} ${className}`}
      role="navigation"
    >
      <button
        onClick={() => navigateToPrevious({ animate: true })}
        disabled={isTransitioning}
        className={`${styles.navButton} ${styles.prev}`}
        aria-label="Previous Screen"
      >
        ←
      </button>

      <div className={styles.screenButtons}>
        {Object.values(ScreenType).map(screen => (
          <button
            key={screen}
            onClick={() => navigateTo(screen, { animate: true })}
            disabled={isTransitioning || !accessibleScreens.includes(screen)}
            className={`${styles.screenButton} ${currentScreen === screen ? styles.active : ''}`}
            aria-label={`Go to ${screen}`}
            aria-current={currentScreen === screen}
          >
            {screen.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <button
        onClick={() => navigateToNext({ animate: true })}
        disabled={isTransitioning}
        className={`${styles.navButton} ${styles.next}`}
        aria-label="Next Screen"
      >
        →
      </button>
    </nav>
  );
};
