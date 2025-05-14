from typing import Any, Dict, List


class InventoryPanel {
  private container: HTMLElement
  private itemsContainer: HTMLElement
  private filterContainer: HTMLElement
  private sortContainer: HTMLElement
  private tooltipElement: HTMLElement
  private items: List[InventoryItem] = []
  private currentFilter: ItemType | null = null
  private currentSort: 'name' | 'type' | 'rarity' = 'name'
  private listeners: ((event: CharacterUIEvent) => void)[] = []
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.tooltipElement = this.createTooltip()
    this.itemsContainer = document.createElement('div')
    this.filterContainer = document.createElement('div')
    this.sortContainer = document.createElement('div')
    this.initializePanel()
  }
  private createTooltip(): HTMLElement {
    const tooltip = document.createElement('div')
    tooltip.className = 'inventory-tooltip'
    tooltip.style.position = 'absolute'
    tooltip.style.display = 'none'
    tooltip.style.zIndex = '1000'
    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.9)'
    tooltip.style.color = 'white'
    tooltip.style.padding = '10px'
    tooltip.style.borderRadius = '5px'
    tooltip.style.maxWidth = '300px'
    document.body.appendChild(tooltip)
    return tooltip
  }
  private initializePanel(): void {
    this.container.innerHTML = ''
    this.container.className = 'inventory-panel'
    this.filterContainer.className = 'inventory-filters'
    const filterTypes = Object.values(ItemType)
    filterTypes.forEach(type => {
      const button = document.createElement('button')
      button.className = 'filter-button'
      button.textContent = type.charAt(0).toUpperCase() + type.slice(1)
      button.addEventListener('click', () => this.setFilter(type))
      this.filterContainer.appendChild(button)
    })
    this.sortContainer.className = 'inventory-sort'
    const sortSelect = document.createElement('select')
    sortSelect.className = 'sort-select'
    const sortOptions = [
      { value: 'name', label: 'Name' },
      { value: 'type', label: 'Type' },
      { value: 'rarity', label: 'Rarity' }
    ]
    sortOptions.forEach(option => {
      const optElement = document.createElement('option')
      optElement.value = option.value
      optElement.textContent = `Sort by ${option.label}`
      sortSelect.appendChild(optElement)
    })
    sortSelect.addEventListener('change', (e) => {
      this.setSort((e.target as HTMLSelectElement).value as 'name' | 'type' | 'rarity')
    })
    this.sortContainer.appendChild(sortSelect)
    this.itemsContainer.className = 'inventory-items'
    this.container.appendChild(this.filterContainer)
    this.container.appendChild(this.sortContainer)
    this.container.appendChild(this.itemsContainer)
    const style = document.createElement('style')
    style.textContent = `
      .inventory-panel {
        display: flex
        flex-direction: column
        gap: 10px
        padding: 15px
        background: rgba(0, 0, 0, 0.1)
        border-radius: 8px
      }
      .inventory-filters {
        display: flex
        gap: 5px
        flex-wrap: wrap
      }
      .filter-button {
        padding: 5px 10px
        border: none
        border-radius: 3px
        background: rgba(255, 255, 255, 0.1)
        color: white
        cursor: pointer
        transition: background-color 0.2s
      }
      .filter-button:hover {
        background: rgba(255, 255, 255, 0.2)
      }
      .filter-button.active {
        background: rgba(255, 255, 255, 0.3)
      }
      .inventory-sort {
        padding: 5px 0
      }
      .sort-select {
        padding: 5px
        border-radius: 3px
        background: rgba(255, 255, 255, 0.1)
        color: white
        border: 1px solid rgba(255, 255, 255, 0.2)
      }
      .inventory-items {
        display: grid
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr))
        gap: 10px
        padding: 10px
        max-height: 400px
        overflow-y: auto
      }
      .item-slot {
        position: relative
        aspect-ratio: 1
        background: rgba(255, 255, 255, 0.1)
        border-radius: 5px
        display: flex
        flex-direction: column
        align-items: center
        justify-content: center
        cursor: pointer
        transition: background-color 0.2s
      }
      .item-slot:hover {
        background: rgba(255, 255, 255, 0.2)
      }
      .item-icon {
        width: 60
        height: 60
        object-fit: contain
      }
      .item-quantity {
        position: absolute
        bottom: 5px
        right: 5px
        background: rgba(0, 0, 0, 0.7)
        padding: 2px 5px
        border-radius: 3px
        font-size: 12px
      }
      .item-rarity-common { border: 1px solid #aaa; }
      .item-rarity-uncommon { border: 1px solid #2ecc71; }
      .item-rarity-rare { border: 1px solid #3498db; }
      .item-rarity-epic { border: 1px solid #9b59b6; }
      .item-rarity-legendary { border: 1px solid #f1c40f; }
      .inventory-tooltip {
        pointer-events: none
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5)
      }
    `
    document.head.appendChild(style)
  }
  private createItemElement(item: InventoryItem): HTMLElement {
    const itemElement = document.createElement('div')
    itemElement.className = `item-slot item-rarity-${item.rarity}`
    const icon = document.createElement('img')
    icon.className = 'item-icon'
    icon.src = item.icon
    icon.alt = item.name
    if (item.stackable && item.quantity > 1) {
      const quantity = document.createElement('div')
      quantity.className = 'item-quantity'
      quantity.textContent = item.quantity.toString()
      itemElement.appendChild(quantity)
    }
    itemElement.appendChild(icon)
    itemElement.addEventListener('mouseenter', (e) => this.showItemTooltip(e, item))
    itemElement.addEventListener('mouseleave', () => this.hideTooltip())
    itemElement.addEventListener('click', () => this.handleItemClick(item))
    return itemElement
  }
  private showItemTooltip(event: MouseEvent, item: InventoryItem): void {
    const tooltipContent = this.createTooltipContent(item)
    this.tooltipElement.innerHTML = tooltipContent
    this.tooltipElement.style.display = 'block'
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    this.tooltipElement.style.left = `${rect.right + 10}px`
    this.tooltipElement.style.top = `${rect.top}px`
  }
  private hideTooltip(): void {
    this.tooltipElement.style.display = 'none'
  }
  private createTooltipContent(item: InventoryItem): str {
    return `
      <div style="margin-bottom: 10px;">
        <strong style="color: ${this.getRarityColor(item.rarity)}">${item.name}</strong>
      </div>
      <div style="color: #aaa; font-size: 12px; margin-bottom: 5px;">
        ${item.type.charAt(0).toUpperCase() + item.type.slice(1)}
      </div>
      <div style="margin-bottom: 10px;">
        ${item.description}
      </div>
      ${Object.entries(item.stats).map(([stat, value]) => `
        <div style="display: flex; justify-content: space-between; margin: 5px 0;">
          <span>${stat.charAt(0).toUpperCase() + stat.slice(1)}</span>
          <span style="color: ${value >= 0 ? '#8f8' : '#f88'}">
            ${value >= 0 ? '+' : ''}${value}
          </span>
        </div>
      `).join('')}
      ${item.effects.map(effect => `
        <div style="margin-top: 5px; color: #aaa; font-size: 12px;">
          ${effect.type}: ${effect.value}
          ${effect.duration ? ` for ${effect.duration}s` : ''}
          ${effect.trigger ? ` (${effect.trigger})` : ''}
        </div>
      `).join('')}
    `
  }
  private getRarityColor(rarity: ItemRarity): str {
    const colors = {
      [ItemRarity.COMMON]: '#aaa',
      [ItemRarity.UNCOMMON]: '#2ecc71',
      [ItemRarity.RARE]: '#3498db',
      [ItemRarity.EPIC]: '#9b59b6',
      [ItemRarity.LEGENDARY]: '#f1c40f'
    }
    return colors[rarity]
  }
  private handleItemClick(item: InventoryItem): void {
    this.notifyListeners({
      type: 'select',
      character: this.currentCharacter!,
      data: Dict[str, Any]
    })
  }
  private setFilter(type: ItemType): void {
    this.currentFilter = this.currentFilter === type ? null : type
    this.updateFilterButtons()
    this.renderItems()
  }
  private updateFilterButtons(): void {
    const buttons = this.filterContainer.getElementsByClassName('filter-button')
    Array.from(buttons).forEach(button => {
      const type = button.textContent?.toLowerCase()
      button.classList.toggle('active', type === this.currentFilter)
    })
  }
  private setSort(sort: 'name' | 'type' | 'rarity'): void {
    this.currentSort = sort
    this.renderItems()
  }
  private sortItems(items: List[InventoryItem]): InventoryItem[] {
    return [...items].sort((a, b) => {
      switch (this.currentSort) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'type':
          return a.type.localeCompare(b.type)
        case 'rarity':
          return Object.values(ItemRarity).indexOf(b.rarity) - 
                 Object.values(ItemRarity).indexOf(a.rarity)
        default:
          return 0
      }
    })
  }
  private currentCharacter: Character | null = null
  public updateInventory(character: Character): void {
    this.currentCharacter = character
    this.items = character.inventory
    this.renderItems()
  }
  private renderItems(): void {
    this.itemsContainer.innerHTML = ''
    let items = this.items
    if (this.currentFilter) {
      items = items.filter(item => item.type === this.currentFilter)
    }
    items = this.sortItems(items)
    items.forEach(item => {
      const itemElement = this.createItemElement(item)
      this.itemsContainer.appendChild(itemElement)
    })
  }
  public addListener(listener: (event: CharacterUIEvent) => void): void {
    this.listeners.push(listener)
  }
  public removeListener(listener: (event: CharacterUIEvent) => void): void {
    const index = this.listeners.indexOf(listener)
    if (index !== -1) {
      this.listeners.splice(index, 1)
    }
  }
  private notifyListeners(event: CharacterUIEvent): void {
    this.listeners.forEach(listener => listener(event))
  }
  public clear(): void {
    this.currentCharacter = null
    this.items = []
    this.itemsContainer.innerHTML = ''
  }
  public dispose(): void {
    this.tooltipElement.remove()
    this.container.innerHTML = ''
    this.listeners = []
  }
} 