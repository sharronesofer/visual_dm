from typing import Any, Dict, List, Union



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
 *   const mgr = new SelectionManager()
 *   mgr.onSelect((e) => { ... })
 *   mgr.onSelectionChange((e) => { ... })
 *   mgr.selectRegion('r1')
 */
SelectionType = Union['region', 'poi']
SelectionAction = Union['select', 'deselect', 'range', 'toggle', 'clear', 'primary']
class SelectionEvent:
    type: SelectionType
    action: SelectionAction
    itemId?: str
    itemIds?: List[str]
    previousPrimaryId?: Union[str, None]
    primaryId?: Union[str, None]
    userEvent?: Union[Event, None]
SelectionListener = (event: SelectionEvent) => None
function debounce<T extends (...args: List[any]) => void>(fn: T, ms: float): T {
  let timeout: Any
  return function (this: Any, ...args: List[any]) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), ms)
  } as T
}
class SelectionManager {
  private selectedRegions: Set<string> = new Set()
  private selectedPOIs: Set<string> = new Set()
  private primaryRegion: str | null = null
  private primaryPOI: str | null = null
  private listeners: Dict[str, Any] = {
    select: new Set(),
    deselect: new Set(),
    selectionChange: new Set(),
    primaryChange: new Set(),
  }
  private debouncedNotifySelectionChange: () => void
  constructor(debounceMs = 50) {
    this.debouncedNotifySelectionChange = debounce(() => {
      this.listeners.selectionChange.forEach(fn =>
        fn({
          type: 'region', 
          action: 'clear',
          itemIds: [...this.selectedRegions, ...this.selectedPOIs],
          primaryId: this.primaryRegion || this.primaryPOI,
        })
      )
    }, debounceMs)
  }
  onSelect(fn: SelectionListener) {
    this.listeners.select.add(fn)
    return () => this.listeners.select.delete(fn)
  }
  onDeselect(fn: SelectionListener) {
    this.listeners.deselect.add(fn)
    return () => this.listeners.deselect.delete(fn)
  }
  onSelectionChange(fn: SelectionListener) {
    this.listeners.selectionChange.add(fn)
    return () => this.listeners.selectionChange.delete(fn)
  }
  onPrimarySelectionChange(fn: SelectionListener) {
    this.listeners.primaryChange.add(fn)
    return () => this.listeners.primaryChange.delete(fn)
  }
  selectRegion(id: str, primary = false, userEvent?: Event) {
    const wasSelected = this.selectedRegions.has(id)
    this.selectedRegions.add(id)
    if (primary || !this.primaryRegion) {
      const prev = this.primaryRegion
      this.primaryRegion = id
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'region',
          action: 'primary',
          itemId: id,
          previousPrimaryId: prev ?? undefined,
          primaryId: id,
          userEvent,
        })
      )
    }
    if (!wasSelected)
      this.listeners.select.forEach(fn =>
        fn({ type: 'region', action: 'select', itemId: id, userEvent })
      )
    this.debouncedNotifySelectionChange()
  }
  deselectRegion(id: str, userEvent?: Event) {
    const wasSelected = this.selectedRegions.delete(id)
    if (wasSelected)
      this.listeners.deselect.forEach(fn =>
        fn({ type: 'region', action: 'deselect', itemId: id, userEvent })
      )
    if (this.primaryRegion === id) {
      const prev = this.primaryRegion
      this.primaryRegion = this.selectedRegions.values().next().value || null
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'region',
          action: 'primary',
          itemId: this.primaryRegion ?? undefined,
          previousPrimaryId: prev ?? undefined,
          primaryId: this.primaryRegion ?? undefined,
          userEvent,
        })
      )
    }
    this.debouncedNotifySelectionChange()
  }
  selectPOI(id: str, primary = false, userEvent?: Event) {
    const wasSelected = this.selectedPOIs.has(id)
    this.selectedPOIs.add(id)
    if (primary || !this.primaryPOI) {
      const prev = this.primaryPOI
      this.primaryPOI = id
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'poi',
          action: 'primary',
          itemId: id,
          previousPrimaryId: prev ?? undefined,
          primaryId: id,
          userEvent,
        })
      )
    }
    if (!wasSelected)
      this.listeners.select.forEach(fn =>
        fn({ type: 'poi', action: 'select', itemId: id, userEvent })
      )
    this.debouncedNotifySelectionChange()
  }
  deselectPOI(id: str, userEvent?: Event) {
    const wasSelected = this.selectedPOIs.delete(id)
    if (wasSelected)
      this.listeners.deselect.forEach(fn =>
        fn({ type: 'poi', action: 'deselect', itemId: id, userEvent })
      )
    if (this.primaryPOI === id) {
      const prev = this.primaryPOI
      this.primaryPOI = this.selectedPOIs.values().next().value || null
      this.listeners.primaryChange.forEach(fn =>
        fn({
          type: 'poi',
          action: 'primary',
          itemId: this.primaryPOI ?? undefined,
          previousPrimaryId: prev ?? undefined,
          primaryId: this.primaryPOI ?? undefined,
          userEvent,
        })
      )
    }
    this.debouncedNotifySelectionChange()
  }
  clearSelection(userEvent?: Event) {
    const regionIds = [...this.selectedRegions]
    const poiIds = [...this.selectedPOIs]
    this.selectedRegions.clear()
    this.selectedPOIs.clear()
    const prevRegion = this.primaryRegion
    const prevPOI = this.primaryPOI
    this.primaryRegion = null
    this.primaryPOI = null
    this.listeners.selectionChange.forEach(fn =>
      fn({
        type: 'region',
        action: 'clear',
        itemIds: regionIds,
        previousPrimaryId: prevRegion,
        userEvent,
      })
    )
    this.listeners.selectionChange.forEach(fn =>
      fn({
        type: 'poi',
        action: 'clear',
        itemIds: poiIds,
        previousPrimaryId: prevPOI,
        userEvent,
      })
    )
  }
  isRegionSelected(id: str) {
    return this.selectedRegions.has(id)
  }
  isPOISelected(id: str) {
    return this.selectedPOIs.has(id)
  }
  getSelectedRegions(): string[] {
    return Array.from(this.selectedRegions)
  }
  getSelectedPOIs(): string[] {
    return Array.from(this.selectedPOIs)
  }
  getPrimaryRegion(): str | null {
    return this.primaryRegion
  }
  getPrimaryPOI(): str | null {
    return this.primaryPOI
  }
}