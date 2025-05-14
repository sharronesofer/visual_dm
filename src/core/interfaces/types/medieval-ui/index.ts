import { ReactNode } from 'react';

// Theme configuration for medieval UI elements
export interface MedievalThemeConfig {
  // Base colors for the theme
  colors: {
    parchment: string;
    ink: string;
    accent: string;
    shadow: string;
    highlight: string;
  };
  // Font settings
  typography: {
    primaryFont: string;
    secondaryFont: string;
    headerScaling: number;
    baseSize: number;
  };
  // Animation timings
  animations: {
    pageFlipDuration: number;
    fadeInDuration: number;
    scrollDuration: number;
  };
  // Texture and border settings
  decorations: {
    borderStyle: 'simple' | 'ornate' | 'illuminated';
    cornerStyle: 'rounded' | 'torn' | 'folded';
    textureIntensity: 'light' | 'medium' | 'heavy';
  };
}

// Base props for all medieval components
export interface MedievalComponentBaseProps {
  className?: string;
  style?: React.CSSProperties;
  children?: ReactNode;
  themeVariant?: 'default' | 'aged' | 'pristine' | 'weathered';
}

// Props for the page container component
export interface PageContainerProps extends MedievalComponentBaseProps {
  title?: string;
  pageNumber?: number;
  hasHeader?: boolean;
  hasFooter?: boolean;
  decorationLevel?: 'minimal' | 'standard' | 'elaborate';
}

// Props for navigation elements
export interface NavigationProps extends MedievalComponentBaseProps {
  type: 'bookmark' | 'tab' | 'ribbon';
  isActive?: boolean;
  onClick?: () => void;
  label: string;
  icon?: string;
}

// Props for medieval text input
export interface TextInputProps extends MedievalComponentBaseProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  isScrollType?: boolean;
  maxLength?: number;
  hasInkEffects?: boolean;
}

// Props for medieval button
export interface ButtonProps extends MedievalComponentBaseProps {
  onClick: () => void;
  variant: 'waxSeal' | 'inkStamp' | 'parchmentRoll';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
  label: string;
}

// Props for scrollable content area
export interface ScrollContainerProps extends MedievalComponentBaseProps {
  maxHeight?: string;
  scrollbarStyle?: 'parchment' | 'ink' | 'minimal';
  showScrollShadow?: boolean;
  decorationLevel?: 'minimal' | 'standard' | 'ornate';
}

// Animation state for page transitions
export interface PageTransitionState {
  isFlipping: boolean;
  direction: 'forward' | 'backward';
  progress: number;
  currentPage: number;
  nextPage: number;
}

// Context interface for medieval theme provider
export interface MedievalThemeContextValue {
  theme: MedievalThemeConfig;
  updateTheme: (updates: Partial<MedievalThemeConfig>) => void;
  resetTheme: () => void;
} 