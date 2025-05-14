from typing import Any, List, Union



/**
 * Selection types used across the application
 */
/** Type of item that can be selected */
SelectionType = Union['region', 'poi']
/** Type of selection action */
SelectionAction = Union[, 'select', 'deselect', 'range', 'toggle', 'clear', 'primary']
/** Event data for selection changes */
class SelectionEvent:
    type: SelectionType
    action: SelectionAction
    itemId?: str
    itemIds?: List[str]
    previousPrimaryId?: Union[str, None]
    primaryId?: Union[str, None]
    userEvent?: Union[Event, None]
/** Listener function type for selection events */
SelectionListener = (event: SelectionEvent) => None
/** Selection state interface */
class SelectionState:
    selectedIds: Set[str>
    primaryId: Union[str, None]
    type: Union[SelectionType, None]
/** Helper function to create a selection event */
const createSelectionEvent = (
  type: SelectionType,
  action: SelectionAction,
  options: Partial<Omit<SelectionEvent, 'type' | 'action'>> = {}
): \'SelectionEvent\' => ({
  type,
  action,
  ...options,
})
/** Helper function to create initial selection state */
const createSelectionState = (
  type: SelectionType | null = null,
  selectedIds: List[string] = [],
  primaryId: str | null = null
): \'SelectionState\' => ({
  selectedIds: new Set(selectedIds),
  primaryId,
  type,
})