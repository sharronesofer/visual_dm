/**
 * Selection types used across the application
 */

/** Type of item that can be selected */
export type SelectionType = 'region' | 'poi';

/** Type of selection action */
export type SelectionAction =
  | 'select'
  | 'deselect'
  | 'range'
  | 'toggle'
  | 'clear'
  | 'primary';

/** Event data for selection changes */
export interface SelectionEvent {
  type: SelectionType;
  action: SelectionAction;
  itemId?: string;
  itemIds?: string[];
  previousPrimaryId?: string | null;
  primaryId?: string | null;
  userEvent?: Event | null;
}

/** Listener function type for selection events */
export type SelectionListener = (event: SelectionEvent) => void;

/** Selection state interface */
export interface SelectionState {
  selectedIds: Set<string>;
  primaryId: string | null;
  type: SelectionType | null;
}

/** Helper function to create a selection event */
export const createSelectionEvent = (
  type: SelectionType,
  action: SelectionAction,
  options: Partial<Omit<SelectionEvent, 'type' | 'action'>> = {}
): SelectionEvent => ({
  type,
  action,
  ...options,
});

/** Helper function to create initial selection state */
export const createSelectionState = (
  type: SelectionType | null = null,
  selectedIds: string[] = [],
  primaryId: string | null = null
): SelectionState => ({
  selectedIds: new Set(selectedIds),
  primaryId,
  type,
});
