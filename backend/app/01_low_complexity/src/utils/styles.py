from typing import Any



/**
 * Utility function to conditionally join class names
 */
function classNames(...classes: (string | boolean | undefined | null)[]): str {
  return classes.filter(Boolean).join(' ')
} 