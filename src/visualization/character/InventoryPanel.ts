import { InventoryItem, ItemType, ItemRarity, Character, CharacterUIEvent } from './types';

export class InventoryPanel {
  private container: HTMLElement;
  private itemsContainer: HTMLElement;
  private filterContainer: HTMLElement;
  private sortContainer: HTMLElement;
  private tooltipElement: HTMLElement;
  private items: InventoryItem[] = [];
  private currentFilter: ItemType | null = null;
  private currentSort: 'name' | 'type' | 'rarity' = 'name';
  private listeners: ((event: CharacterUIEvent) => void)[] = [];

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.tooltipElement = this.createTooltip();
    this.itemsContainer = document.createElement('div');
    this.filterContainer = document.createElement('div');
    this.sortContainer = document.createElement('div');
    this.initializePanel();
  }

  private createTooltip(): HTMLElement {
    const tooltip = document.createElement('div');
    tooltip.className = 'inventory-tooltip';
    tooltip.style.position = 'absolute';
    tooltip.style.display = 'none';
    tooltip.style.zIndex = '1000';
    tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
    tooltip.style.color = 'white';
    tooltip.style.padding = '10px';
    tooltip.style.borderRadius = '5px';
    tooltip.style.maxWidth = '300px';
    document.body.appendChild(tooltip);
    return tooltip;
  }

  private initializePanel(): void {
    this.container.innerHTML = '';
    this.container.className = 'inventory-panel';

    // Create filter buttons
    this.filterContainer.className = 'inventory-filters';
    const filterTypes = Object.values(ItemType);
    filterTypes.forEach(type => {
      const button = document.createElement('button');
      button.className = 'filter-button';
      button.textContent = type.charAt(0).toUpperCase() + type.slice(1);
      button.addEventListener('click', () => this.setFilter(type));
      this.filterContainer.appendChild(button);
    });

    // Create sort options
    this.sortContainer.className = 'inventory-sort';
    const sortSelect = document.createElement('select');
    sortSelect.className = 'sort-select';
    const sortOptions = [
      { value: 'name', label: 'Name' },
      { value: 'type', label: 'Type' },
      { value: 'rarity', label: 'Rarity' }
    ];
    sortOptions.forEach(option => {
      const optElement = document.createElement('option');
      optElement.value = option.value;
      optElement.textContent = `Sort by ${option.label}`;
      sortSelect.appendChild(optElement);
    });
    sortSelect.addEventListener('change', (e) => {
      this.setSort((e.target as HTMLSelectElement).value as 'name' | 'type' | 'rarity');
    });
    this.sortContainer.appendChild(sortSelect);

    // Create items container
    this.itemsContainer.className = 'inventory-items';

    // Add components to container
    this.container.appendChild(this.filterContainer);
    this.container.appendChild(this.sortContainer);
    this.container.appendChild(this.itemsContainer);

    // Add CSS styles
    const style = document.createElement('style');
    style.textContent = `
      .inventory-panel {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 15px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 8px;
      }

      .inventory-filters {
        display: flex;
        gap: 5px;
        flex-wrap: wrap;
      }

      .filter-button {
        padding: 5px 10px;
        border: none;
        border-radius: 3px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        cursor: pointer;
        transition: background-color 0.2s;
      }

      .filter-button:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      .filter-button.active {
        background: rgba(255, 255, 255, 0.3);
      }

      .inventory-sort {
        padding: 5px 0;
      }

      .sort-select {
        padding: 5px;
        border-radius: 3px;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }

      .inventory-items {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 10px;
        padding: 10px;
        max-height: 400px;
        overflow-y: auto;
      }

      .item-slot {
        position: relative;
        aspect-ratio: 1;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.2s;
      }

      .item-slot:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      .item-icon {
        width: 60%;
        height: 60%;
        object-fit: contain;
      }

      .item-quantity {
        position: absolute;
        bottom: 5px;
        right: 5px;
        background: rgba(0, 0, 0, 0.7);
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 12px;
      }

      .item-rarity-common { border: 1px solid #aaa; }
      .item-rarity-uncommon { border: 1px solid #2ecc71; }
      .item-rarity-rare { border: 1px solid #3498db; }
      .item-rarity-epic { border: 1px solid #9b59b6; }
      .item-rarity-legendary { border: 1px solid #f1c40f; }

      .inventory-tooltip {
        pointer-events: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
      }
    `;
    document.head.appendChild(style);
  }

  private createItemElement(item: InventoryItem): HTMLElement {
    const itemElement = document.createElement('div');
    itemElement.className = `item-slot item-rarity-${item.rarity}`;

    const icon = document.createElement('img');
    icon.className = 'item-icon';
    icon.src = item.icon;
    icon.alt = item.name;

    if (item.stackable && item.quantity > 1) {
      const quantity = document.createElement('div');
      quantity.className = 'item-quantity';
      quantity.textContent = item.quantity.toString();
      itemElement.appendChild(quantity);
    }

    itemElement.appendChild(icon);

    // Add event listeners
    itemElement.addEventListener('mouseenter', (e) => this.showItemTooltip(e, item));
    itemElement.addEventListener('mouseleave', () => this.hideTooltip());
    itemElement.addEventListener('click', () => this.handleItemClick(item));

    return itemElement;
  }

  private showItemTooltip(event: MouseEvent, item: InventoryItem): void {
    const tooltipContent = this.createTooltipContent(item);
    this.tooltipElement.innerHTML = tooltipContent;
    this.tooltipElement.style.display = 'block';

    const rect = (event.target as HTMLElement).getBoundingClientRect();
    this.tooltipElement.style.left = `${rect.right + 10}px`;
    this.tooltipElement.style.top = `${rect.top}px`;
  }

  private hideTooltip(): void {
    this.tooltipElement.style.display = 'none';
  }

  private createTooltipContent(item: InventoryItem): string {
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
    `;
  }

  private getRarityColor(rarity: ItemRarity): string {
    const colors = {
      [ItemRarity.COMMON]: '#aaa',
      [ItemRarity.UNCOMMON]: '#2ecc71',
      [ItemRarity.RARE]: '#3498db',
      [ItemRarity.EPIC]: '#9b59b6',
      [ItemRarity.LEGENDARY]: '#f1c40f'
    };
    return colors[rarity];
  }

  private handleItemClick(item: InventoryItem): void {
    this.notifyListeners({
      type: 'select',
      character: this.currentCharacter!,
      data: { item }
    });
  }

  private setFilter(type: ItemType): void {
    this.currentFilter = this.currentFilter === type ? null : type;
    this.updateFilterButtons();
    this.renderItems();
  }

  private updateFilterButtons(): void {
    const buttons = this.filterContainer.getElementsByClassName('filter-button');
    Array.from(buttons).forEach(button => {
      const type = button.textContent?.toLowerCase();
      button.classList.toggle('active', type === this.currentFilter);
    });
  }

  private setSort(sort: 'name' | 'type' | 'rarity'): void {
    this.currentSort = sort;
    this.renderItems();
  }

  private sortItems(items: InventoryItem[]): InventoryItem[] {
    return [...items].sort((a, b) => {
      switch (this.currentSort) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'type':
          return a.type.localeCompare(b.type);
        case 'rarity':
          return Object.values(ItemRarity).indexOf(b.rarity) -
            Object.values(ItemRarity).indexOf(a.rarity);
        default:
          return 0;
      }
    });
  }

  private currentCharacter: Character | null = null;

  public updateInventory(character: Character): void {
    this.currentCharacter = character;
    this.items = character.inventory;
    this.renderItems();
  }

  private renderItems(): void {
    this.itemsContainer.innerHTML = '';
    let items = this.items;

    // Apply filter
    if (this.currentFilter) {
      items = items.filter(item => item.type === this.currentFilter);
    }

    // Apply sort
    items = this.sortItems(items);

    // Create and append item elements
    items.forEach(item => {
      const itemElement = this.createItemElement(item);
      this.itemsContainer.appendChild(itemElement);
    });
  }

  public addListener(listener: (event: CharacterUIEvent) => void): void {
    this.listeners.push(listener);
  }

  public removeListener(listener: (event: CharacterUIEvent) => void): void {
    const index = this.listeners.indexOf(listener);
    if (index !== -1) {
      this.listeners.splice(index, 1);
    }
  }

  private notifyListeners(event: CharacterUIEvent): void {
    this.listeners.forEach(listener => listener(event));
  }

  public clear(): void {
    this.currentCharacter = null;
    this.items = [];
    this.itemsContainer.innerHTML = '';
  }

  public dispose(): void {
    this.tooltipElement.remove();
    this.container.innerHTML = '';
    this.listeners = [];
  }
}

/**
 * LODConfigPanel: Artist-facing UI for editing LOD configuration.
 * (Stub implementation for future UI/UX work)
 */
export class LODConfigPanel {
  private container: HTMLElement;
  private config: any; // Should be WeatherLODConfig
  private effectTypes: string[] = [];
  private listeners: Array<() => void> = [];

  constructor(containerId: string, effectTypes: string[] = []) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.effectTypes = effectTypes;
    this.initializePanel();
  }

  /**
   * Initialize the LOD config editor panel UI.
   * (Stub: Add controls for each effect type and LOD level)
   */
  private initializePanel(): void {
    this.container.innerHTML = '';
    this.container.className = 'lod-config-panel';
    // TODO: Add controls for editing thresholds, quality params, transition distances
    // TODO: Add real-time preview button
    // TODO: Add load/save JSON config buttons
    // TODO: Add presets dropdown
    // TODO: Add validation feedback
  }

  /**
   * Load LOD config from JSON.
   */
  public loadConfig(json: string) {
    try {
      this.config = JSON.parse(json);
      this.notifyListeners();
      this.render();
    } catch (e) {
      // TODO: Show error to user
    }
  }

  /**
   * Save current config to JSON.
   */
  public saveConfig(): string {
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * Apply a preset configuration.
   */
  public applyPreset(preset: any) {
    // TODO: Implement preset logic
    this.config = { ...preset };
    this.notifyListeners();
    this.render();
  }

  /**
   * Validate current config and show feedback.
   */
  public validateConfig(): boolean {
    // TODO: Implement validation logic
    return true;
  }

  /**
   * Add a listener for config changes.
   */
  public addListener(listener: () => void) {
    this.listeners.push(listener);
  }

  /**
   * Remove a listener.
   */
  public removeListener(listener: () => void) {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  private notifyListeners() {
    for (const l of this.listeners) l();
  }

  /**
   * Render the panel UI (stub).
   */
  public render() {
    // TODO: Render controls for each effect type and LOD level
  }

  /**
   * Show real-time preview of LOD changes (stub).
   */
  public showPreview() {
    // TODO: Integrate with WeatherLODManager for live preview
  }
}

/**
 * NPCLODConfigPanel: Developer UI for visualizing and configuring NPC LOD system.
 * - Adjust LOD thresholds, update priorities, simulation params
 * - Real-time preview, load/save config, presets, validation
 * - Visualize current LOD state and CPU heatmap
 */
export class NPCLODConfigPanel {
  private container: HTMLElement;
  private config: any = {};
  private listeners: Array<() => void> = [];
  private previewCallback: (() => void) | null = null;
  private lodState: Record<string, string> = {};
  private heatmapData: number[][] = [];

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) throw new Error(`Container element with id '${containerId}' not found`);
    this.container = element;
    this.initializePanel();
  }

  private initializePanel(): void {
    this.container.innerHTML = '';
    this.container.className = 'npc-lod-config-panel';
    // --- Controls ---
    const controls = document.createElement('div');
    controls.className = 'npc-lod-controls';
    // LOD thresholds
    controls.innerHTML += `
      <label>To Statistical: <input type="number" id="lod-to-statistical" value="300" min="50" max="2000" step="10"></label>
      <label>To Individual: <input type="number" id="lod-to-individual" value="150" min="10" max="1000" step="10"></label>
      <label>Pooling Aggressiveness: <input type="range" id="lod-pooling" min="0" max="1" step="0.01" value="0.5"></label>
      <label>Transition Delay (ms): <input type="number" id="lod-transition-delay" value="500" min="0" max="5000" step="50"></label>
      <button id="npc-lod-preview">Preview</button>
      <button id="npc-lod-load">Load Config</button>
      <button id="npc-lod-save">Save Config</button>
      <select id="npc-lod-presets">
        <option value="default">Default</option>
        <option value="performance">Performance</option>
        <option value="quality">Quality</option>
      </select>
      <span id="npc-lod-validation"></span>
    `;
    this.container.appendChild(controls);
    // --- LOD State Visualization ---
    const lodStateDiv = document.createElement('div');
    lodStateDiv.className = 'npc-lod-state';
    lodStateDiv.innerHTML = '<h4>Current NPC LOD State</h4><div id="npc-lod-state-list"></div>';
    this.container.appendChild(lodStateDiv);
    // --- Heatmap Visualization ---
    const heatmapDiv = document.createElement('div');
    heatmapDiv.className = 'npc-lod-heatmap';
    heatmapDiv.innerHTML = '<h4>CPU Usage Heatmap</h4><canvas id="npc-lod-heatmap-canvas" width="200" height="100"></canvas>';
    this.container.appendChild(heatmapDiv);
    // --- Event Listeners ---
    controls.querySelector('#npc-lod-preview')?.addEventListener('click', () => this.previewCallback?.());
    controls.querySelector('#npc-lod-load')?.addEventListener('click', () => this.loadConfigFromPrompt());
    controls.querySelector('#npc-lod-save')?.addEventListener('click', () => this.saveConfigToFile());
    controls.querySelector('#npc-lod-presets')?.addEventListener('change', (e) => this.applyPreset((e.target as HTMLSelectElement).value));
    // Input change listeners
    ['lod-to-statistical', 'lod-to-individual', 'lod-pooling', 'lod-transition-delay'].forEach(id => {
      controls.querySelector(`#${id}`)?.addEventListener('input', () => this.handleConfigChange());
    });
    this.renderLODState();
    this.renderHeatmap();
    this.addCSS();
  }

  private handleConfigChange() {
    // Read values from inputs and update config
    const toStat = +(this.container.querySelector('#lod-to-statistical') as HTMLInputElement).value;
    const toInd = +(this.container.querySelector('#lod-to-individual') as HTMLInputElement).value;
    const pooling = +(this.container.querySelector('#lod-pooling') as HTMLInputElement).value;
    const delay = +(this.container.querySelector('#lod-transition-delay') as HTMLInputElement).value;
    this.config = { toStatistical: toStat, toIndividual: toInd, poolingAggressiveness: pooling, transitionDelay: delay };
    this.validateConfig();
    this.notifyListeners();
  }

  private validateConfig(): boolean {
    const valid = this.config.toStatistical > this.config.toIndividual && this.config.toIndividual > 0;
    const validation = this.container.querySelector('#npc-lod-validation') as HTMLElement;
    validation.textContent = valid ? '✔️' : '❌ LOD thresholds invalid';
    return valid;
  }

  public addListener(listener: () => void) { this.listeners.push(listener); }
  public removeListener(listener: () => void) { this.listeners = this.listeners.filter(l => l !== listener); }
  private notifyListeners() { for (const l of this.listeners) l(); }

  public setPreviewCallback(cb: () => void) { this.previewCallback = cb; }

  public loadConfig(json: string) {
    try { this.config = JSON.parse(json); this.updateInputsFromConfig(); this.notifyListeners(); } catch { }
  }
  public saveConfig(): string { return JSON.stringify(this.config, null, 2); }
  private loadConfigFromPrompt() {
    const json = prompt('Paste NPC LOD config JSON:');
    if (json) this.loadConfig(json);
  }
  private saveConfigToFile() {
    const blob = new Blob([this.saveConfig()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'npc_lod_config.json'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  public applyPreset(preset: string) {
    if (preset === 'performance') this.config = { toStatistical: 600, toIndividual: 300, poolingAggressiveness: 0.9, transitionDelay: 200 };
    else if (preset === 'quality') this.config = { toStatistical: 200, toIndividual: 80, poolingAggressiveness: 0.2, transitionDelay: 800 };
    else this.config = { toStatistical: 300, toIndividual: 150, poolingAggressiveness: 0.5, transitionDelay: 500 };
    this.updateInputsFromConfig(); this.notifyListeners();
  }
  private updateInputsFromConfig() {
    (this.container.querySelector('#lod-to-statistical') as HTMLInputElement).value = this.config.toStatistical;
    (this.container.querySelector('#lod-to-individual') as HTMLInputElement).value = this.config.toIndividual;
    (this.container.querySelector('#lod-pooling') as HTMLInputElement).value = this.config.poolingAggressiveness;
    (this.container.querySelector('#lod-transition-delay') as HTMLInputElement).value = this.config.transitionDelay;
    this.validateConfig();
  }
  public setLODState(state: Record<string, string>) { this.lodState = state; this.renderLODState(); }
  private renderLODState() {
    const list = this.container.querySelector('#npc-lod-state-list');
    if (!list) return;
    list.innerHTML = Object.entries(this.lodState).map(([id, lod]) => `<div>${id}: <span class="lod-level lod-${lod}">${lod}</span></div>`).join('');
  }
  public setHeatmapData(data: number[][]) { this.heatmapData = data; this.renderHeatmap(); }
  private renderHeatmap() {
    const canvas = this.container.querySelector('#npc-lod-heatmap-canvas') as HTMLCanvasElement;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const rows = this.heatmapData.length, cols = this.heatmapData[0]?.length || 0;
    const w = canvas.width / (cols || 1), h = canvas.height / (rows || 1);
    for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
      const v = this.heatmapData[y][x];
      ctx.fillStyle = `rgba(255,0,0,${Math.min(1, v)})`;
      ctx.fillRect(x * w, y * h, w, h);
    }
  }
  private addCSS() {
    const style = document.createElement('style');
    style.textContent = `
      .npc-lod-config-panel { background: #181c24; color: #fff; padding: 18px; border-radius: 10px; width: 420px; font-family: sans-serif; }
      .npc-lod-controls label { display: block; margin: 8px 0; }
      .npc-lod-controls input[type=number], .npc-lod-controls input[type=range] { margin-left: 8px; }
      .npc-lod-controls button, .npc-lod-controls select { margin: 8px 4px 8px 0; }
      .npc-lod-state { margin-top: 18px; }
      .npc-lod-state .lod-level { font-weight: bold; margin-left: 8px; }
      .npc-lod-state .lod-ultra { color: #00eaff; }
      .npc-lod-state .lod-high { color: #00ff00; }
      .npc-lod-state .lod-medium { color: #ffff00; }
      .npc-lod-state .lod-low { color: #ff9900; }
      .npc-lod-state .lod-verylow { color: #ff0000; }
      .npc-lod-heatmap { margin-top: 18px; }
    `;
    document.head.appendChild(style);
  }
} 