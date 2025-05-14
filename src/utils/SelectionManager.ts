// SelectionManager.ts

/**
 * SelectionManager API
 *
 * - Manages selection state for regions and POIs (multi-selection, primary selection)
 * - Emits detailed events:
 *   - onSelect: when an item is selected
 *   - onDeselect: when an item is deselected
 *   - onSelectionChange: when the selection set changes (debounced)
 *   - onPrimarySelectionChange: when the primary selection changes
 * - Event payloads include: item ID(s), selection type, user action ("select", "deselect", "range", "toggle", etc.)
 * - Subscribe/unsubscribe methods for each event type
 * - Event throttling for onSelectionChange (default 50ms debounce)
 *
 * Example usage:
 *   const mgr = new SelectionManager();
 *   mgr.onSelect((e) => { ... });
 *   mgr.onSelectionChange((e) => { ... });
 *   mgr.selectRegion('r1');
 */

export type SelectionType = 'region' | 'poi';
export type SelectionAction = 'select' | 'deselect' | 'range' | 'toggle' | 'clear' | 'primary';

export interface SelectionEvent {
  type: SelectionType;
  action: SelectionAction;
  itemId?: string;
  itemIds?: string[];
  previousPrimaryId?: string | null;
  primaryId?: string | null;
  userEvent?: Event | null;
}

export type SelectionListener = (event: SelectionEvent) => void;

function debounce<T extends (...args: any[]) => void>(fn: T, ms: number): T {
  let timeout: any;
  return function (this: any, ...args: any[]) {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), ms);
  } as T;
}

export class SelectionManager {
  private selectedRegions: Set<string> = new Set();
  private selectedPOIs: Set<string> = new Set();
  private primaryRegion: string | null = null;
  private primaryPOI: string | null = null;
  private listeners: {
    select: Set<SelectionListener>;
    deselect: Set<SelectionListener>;
    selectionChange: Set<SelectionListener>;
    primaryChange: Set<SelectionListener>;
  } = {
    select: new Set(),
    deselect: new Set(),
    selectionChange: new Set(),
    primaryChange: new Set(),
  };
  private debouncedNotifySelectionChange: () => void;

  constructor(debounceMs = 50) {
    this.debouncedNotifySelectionChange = debounce(() => {
      this.listeners.selectionChange.forEach(fn =>
        fn({
          type: 'region', // Could be region or poi; for batch, use both or split events
          action: 'clear',
          itemIds: [...this.selectedRegions, ...this.selectedPOIs],
          primaryId: this.primaryRegion || this.primaryPOI,
        })
      );
    }, debounceMs);
  }

  // --- Event subscription API ---
  onSelect(fn: SelectionListener) {
    this.listeners.select.add(fn);
    return () => this.listeners.select.delete(fn);
  }
  onDeselect(fn: SelectionListener) {
    this.listeners.deselect.add(fn);
    return () => this.listeners.deselect.delete(fn);
  }
  onSelectionChange(fn: SelectionListener) {
    this.listeners.selectionChange.add(fn);
    return () => this.listeners.selectionChange.delete(fn);
  }
  onPrimarySelectionChange(fn: SelectionListener) {
    this.listeners.primaryChange.add(fn);
    return () => this.listeners.primaryChange.delete(fn);
  }

  // --- Selection logic ---
  selectRegion(id: string, primary = false, userEvent?: Event) {
    const wasSelected = this.selectedRegions.has(id);
    this.selectedRegions.add(id);
    if (primary || !this.primaryRegion) {
      const prev = this.primaryRegion;
      this.primaryRegion = id;
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'region',
          action: 'primary',
          itemId: id,
          previousPrimaryId: prev ?? undefined,
          primaryId: id,
          userEvent,
        })
      );
    }
    if (!wasSelected)
      this.listeners.select.forEach(fn =>
        fn({ type: 'region', action: 'select', itemId: id, userEvent })
      );
    this.debouncedNotifySelectionChange();
  }

  deselectRegion(id: string, userEvent?: Event) {
    const wasSelected = this.selectedRegions.delete(id);
    if (wasSelected)
      this.listeners.deselect.forEach(fn =>
        fn({ type: 'region', action: 'deselect', itemId: id, userEvent })
      );
    if (this.primaryRegion === id) {
      const prev = this.primaryRegion;
      this.primaryRegion = this.selectedRegions.values().next().value || null;
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'region',
          action: 'primary',
          itemId: this.primaryRegion ?? undefined,
          previousPrimaryId: prev ?? undefined,
          primaryId: this.primaryRegion ?? undefined,
          userEvent,
        })
      );
    }
    this.debouncedNotifySelectionChange();
  }

  selectPOI(id: string, primary = false, userEvent?: Event) {
    const wasSelected = this.selectedPOIs.has(id);
    this.selectedPOIs.add(id);
    if (primary || !this.primaryPOI) {
      const prev = this.primaryPOI;
      this.primaryPOI = id;
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'poi',
          action: 'primary',
          itemId: id,
          previousPrimaryId: prev ?? undefined,
          primaryId: id,
          userEvent,
        })
      );
    }
    if (!wasSelected)
      this.listeners.select.forEach(fn =>
        fn({ type: 'poi', action: 'select', itemId: id, userEvent })
      );
    this.debouncedNotifySelectionChange();
  }

  deselectPOI(id: string, userEvent?: Event) {
    const wasSelected = this.selectedPOIs.delete(id);
    if (wasSelected)
      this.listeners.deselect.forEach(fn =>
        fn({ type: 'poi', action: 'deselect', itemId: id, userEvent })
      );
    if (this.primaryPOI === id) {
      const prev = this.primaryPOI;
      this.primaryPOI = this.selectedPOIs.values().next().value || null;
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'poi',
          action: 'primary',
          itemId: this.primaryPOI ?? undefined,
          previousPrimaryId: prev ?? undefined,
          primaryId: this.primaryPOI ?? undefined,
          userEvent,
        })
      );
    }
    this.debouncedNotifySelectionChange();
  }

  clearSelection(userEvent?: Event) {
    const regionIds = [...this.selectedRegions];
    const poiIds = [...this.selectedPOIs];
    this.selectedRegions.clear();
    this.selectedPOIs.clear();
    const prevRegion = this.primaryRegion;
    const prevPOI = this.primaryPOI;
    this.primaryRegion = null;
    this.primaryPOI = null;
    this.listeners.selectionChange.forEach(fn =>
      fn({
        type: 'region',
        action: 'clear',
        itemIds: regionIds,
        previousPrimaryId: prevRegion,
        userEvent,
      })
    );
    this.listeners.selectionChange.forEach(fn =>
      fn({
        type: 'poi',
        action: 'clear',
        itemIds: poiIds,
        previousPrimaryId: prevPOI,
        userEvent,
      })
    );
  }

  // --- Multi-selection and range selection logic would go here (see previous implementation) ---

  isRegionSelected(id: string) {
    return this.selectedRegions.has(id);
  }
  isPOISelected(id: string) {
    return this.selectedPOIs.has(id);
  }
  getSelectedRegions(): string[] {
    return Array.from(this.selectedRegions);
  }
  getSelectedPOIs(): string[] {
    return Array.from(this.selectedPOIs);
  }
  getPrimaryRegion(): string | null {
    return this.primaryRegion;
  }
  getPrimaryPOI(): string | null {
    return this.primaryPOI;
  }
}
