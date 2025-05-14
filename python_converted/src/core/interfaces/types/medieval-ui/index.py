from typing import Any, Dict, Union


class MedievalThemeConfig:
    colors: Dict[str, Any]
  animations: Dict[str, Any]
  decorations: Dict[str, Any]
}
class MedievalComponentBaseProps:
    className?: str
    style?: React.CSSProperties
    children?: ReactNode
    themeVariant?: Union['default', 'aged', 'pristine', 'weathered']
class PageContainerProps:
    title?: str
    pageNumber?: float
    hasHeader?: bool
    hasFooter?: bool
    decorationLevel?: Union['minimal', 'standard', 'elaborate']
class NavigationProps:
    type: Union['bookmark', 'tab', 'ribbon']
    isActive?: bool
    onClick?: () => None
    label: str
    icon?: str
class TextInputProps:
    value: str
    onChange: (value: str) => None
    placeholder?: str
    isScrollType?: bool
    maxLength?: float
    hasInkEffects?: bool
class ButtonProps:
    onClick: () => None
    variant: Union['waxSeal', 'inkStamp', 'parchmentRoll']
    size?: Union['small', 'medium', 'large']
    disabled?: bool
    loading?: bool
    icon?: str
    label: str
class ScrollContainerProps:
    maxHeight?: str
    scrollbarStyle?: Union['parchment', 'ink', 'minimal']
    showScrollShadow?: bool
    decorationLevel?: Union['minimal', 'standard', 'ornate']
class PageTransitionState:
    isFlipping: bool
    direction: Union['forward', 'backward']
    progress: float
    currentPage: float
    nextPage: float
class MedievalThemeContextValue:
    theme: \'MedievalThemeConfig\'
    updateTheme: (updates: Partial<MedievalThemeConfig>) => None
    resetTheme: () => None 