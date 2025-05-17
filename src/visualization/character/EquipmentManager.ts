import { Character, Equipment, InventoryItem, ItemType, CharacterUIEvent, EquipmentState } from './types';

export class EquipmentManager {
  private container: HTMLElement;
  private previewContainer: HTMLElement;
  private equipmentContainer: HTMLElement;
  private tooltipElement: HTMLElement;
  private currentCharacter: Character | null = null;
  private listeners: ((event: CharacterUIEvent) => void)[] = [];
  private switchCooldown: boolean = false;
  private cooldownDuration: number = 1000; // ms, can be made configurable
  private lastSwitchTime: number = 0;
  private switchingSlot: keyof Equipment | null = null;
  private stateValidators: Array<(item: InventoryItem, character: Character) => boolean> = [];

  constructor(containerId: string) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.tooltipElement = this.createTooltip();
    this.previewContainer = document.createElement('div');
    this.equipmentContainer = document.createElement('div');
    this.initializeManager();
  }

  private createTooltip(): HTMLElement {
    const tooltip = document.createElement('div');
    tooltip.className = 'equipment-tooltip';
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

  private initializeManager(): void {
    this.container.innerHTML = '';
    this.container.className = 'equipment-manager';

    // Create character preview
    this.previewContainer.className = 'character-preview';
    this.previewContainer.innerHTML = `
      <div class="preview-placeholder">
        <div class="preview-silhouette"></div>
      </div>
    `;

    // Create equipment slots
    this.equipmentContainer.className = 'equipment-slots';
    const slots = ['weapon', 'armor', 'accessory1', 'accessory2'];
    slots.forEach(slot => {
      const slotElement = document.createElement('div');
      slotElement.className = `equipment-slot ${slot}-slot`;
      slotElement.dataset.slot = slot;

      const label = document.createElement('div');
      label.className = 'slot-label';
      label.textContent = this.formatSlotName(slot);

      const itemContainer = document.createElement('div');
      itemContainer.className = 'slot-item';

      slotElement.appendChild(label);
      slotElement.appendChild(itemContainer);

      // Add drop zone functionality
      this.setupDropZone(slotElement);

      this.equipmentContainer.appendChild(slotElement);
    });

    // Add components to container
    this.container.appendChild(this.previewContainer);
    this.container.appendChild(this.equipmentContainer);

    // Add CSS styles
    const style = document.createElement('style');
    style.textContent = `
      .equipment-manager {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        padding: 15px;
        background: rgba(0, 0, 0, 0.1);
        border-radius: 8px;
      }

      .character-preview {
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
        aspect-ratio: 3/4;
      }

      .preview-placeholder {
        width: 80%;
        height: 80%;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .preview-silhouette {
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.1);
        mask: url('/assets/character-silhouette.svg') center/contain no-repeat;
        -webkit-mask: url('/assets/character-silhouette.svg') center/contain no-repeat;
      }

      .equipment-slots {
        display: grid;
        grid-template-rows: repeat(4, 1fr);
        gap: 10px;
      }

      .equipment-slot {
        display: grid;
        grid-template-columns: 100px 1fr;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
        transition: background-color 0.2s;
      }

      .equipment-slot.drag-over {
        background: rgba(255, 255, 255, 0.15);
      }

      .slot-label {
        font-size: 14px;
        color: #ccc;
        text-transform: uppercase;
      }

      .slot-item {
        position: relative;
        width: 60px;
        height: 60px;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        display: flex;
        justify-content: center;
        align-items: center;
      }

      .slot-item.equipped {
        border-color: rgba(255, 255, 255, 0.3);
      }

      .slot-item img {
        max-width: 80%;
        max-height: 80%;
        object-fit: contain;
      }

      .equipment-tooltip {
        pointer-events: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
      }

      .equipment-slot.switch-anim {
        animation: switchFade 0.6s cubic-bezier(0.4,0,0.2,1);
        box-shadow: 0 0 8px 2px #8f8;
      }
      @keyframes switchFade {
        0% { background: #222; }
        50% { background: #8f8; }
        100% { background: rgba(255,255,255,0.05); }
      }
      .equipment-slot.cooldown-flash {
        animation: cooldownFlash 0.4s;
        border: 2px solid #f88;
      }
      @keyframes cooldownFlash {
        0% { border-color: #f88; }
        50% { border-color: #fff; }
        100% { border-color: #f88; }
      }
      .state-overlay {
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 18px;
        color: #f88;
        pointer-events: none;
        z-index: 2;
        text-shadow: 0 0 4px #000;
      }
      .state-overlay.empowered { color: #8ff; }
      .state-overlay.damaged { color: #ff8; }
      .state-overlay.repaired { color: #8f8; }
      .durability-bar {
        position: absolute;
        bottom: 2px;
        left: 2px;
        width: 90%;
        height: 6px;
        background: #222;
        border-radius: 3px;
        overflow: hidden;
        z-index: 1;
      }
      .durability-fill {
        height: 100%;
        background: linear-gradient(90deg, #8f8, #ff8, #f88);
        border-radius: 3px;
        transition: width 0.2s;
      }
      .slot-item.broken { filter: grayscale(1) brightness(0.7); }
      .slot-item.disabled { filter: grayscale(1) opacity(0.5); }
      .slot-item.empowered { box-shadow: 0 0 8px 2px #8ff; }
      .slot-item.damaged { box-shadow: 0 0 8px 2px #ff8; }
      .slot-item.repaired { box-shadow: 0 0 8px 2px #8f8; }
    `;
    document.head.appendChild(style);
  }

  private formatSlotName(slot: string): string {
    return slot
      .replace(/([A-Z])/g, ' $1')
      .replace(/\d+/g, ' $&')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private setupDropZone(element: HTMLElement): void {
    element.addEventListener('dragover', (e) => {
      e.preventDefault();
      element.classList.add('drag-over');
    });

    element.addEventListener('dragleave', () => {
      element.classList.remove('drag-over');
    });

    element.addEventListener('drop', (e) => {
      e.preventDefault();
      element.classList.remove('drag-over');

      const itemData = e.dataTransfer?.getData('text/plain');
      if (itemData && this.currentCharacter) {
        try {
          const item = JSON.parse(itemData) as InventoryItem;
          const slot = element.dataset.slot as keyof Equipment;
          this.equipItem(item, slot);
        } catch (error) {
          console.error('Failed to parse dropped item:', error);
        }
      }
    });
  }

  private equipItem(item: InventoryItem, slot: keyof Equipment): void {
    if (!this.currentCharacter) return;
    if (this.switchCooldown) {
      this.flashCooldown(slot);
      return;
    }
    // Pre-switch event hook
    this.notifyListeners({
      type: 'preSwitch',
      character: this.currentCharacter,
      data: { item, slot }
    });
    this.switchingSlot = slot;
    this.switchCooldown = true;
    this.lastSwitchTime = Date.now();
    this.animateSwitch(slot);
    setTimeout(() => {
      this.performEquip(item, slot);
      this.switchCooldown = false;
      this.switchingSlot = null;
      // Post-switch event hook
      this.notifyListeners({
        type: 'postSwitch',
        character: this.currentCharacter,
        data: { item, slot }
      });
    }, this.cooldownDuration);
  }

  private performEquip(item: InventoryItem, slot: keyof Equipment): void {
    // Validate item type for slot
    const validTypes: Record<keyof Equipment, ItemType[]> = {
      weapon: [ItemType.WEAPON],
      armor: [ItemType.ARMOR],
      accessory1: [ItemType.ACCESSORY],
      accessory2: [ItemType.ACCESSORY]
    };
    if (!validTypes[slot].includes(item.type)) {
      console.warn(`Invalid item type ${item.type} for slot ${slot}`);
      return;
    }
    // Unequip current item if any
    const currentItem = this.currentCharacter!.equipment[slot];
    if (currentItem) {
      this.notifyListeners({
        type: 'unequip',
        character: this.currentCharacter!,
        data: { item: currentItem, slot }
      });
    }
    // Equip new item
    this.notifyListeners({
      type: 'equip',
      character: this.currentCharacter!,
      data: { item, slot }
    });
    // Update display
    this.updateEquipmentDisplay();
  }

  private animateSwitch(slot: keyof Equipment): void {
    // Add a CSS class to the slot for animation
    const slotElement = this.equipmentContainer.querySelector(`.equipment-slot[data-slot="${slot}"]`);
    if (slotElement) {
      slotElement.classList.add('switch-anim');
      setTimeout(() => {
        slotElement.classList.remove('switch-anim');
      }, 600); // Animation duration in ms
    }
  }

  private flashCooldown(slot: keyof Equipment): void {
    // Visual feedback for cooldown (e.g., shake or red border)
    const slotElement = this.equipmentContainer.querySelector(`.equipment-slot[data-slot="${slot}"]`);
    if (slotElement) {
      slotElement.classList.add('cooldown-flash');
      setTimeout(() => {
        slotElement.classList.remove('cooldown-flash');
      }, 400);
    }
  }

  private updateEquipmentDisplay(): void {
    if (!this.currentCharacter) return;
    const slots = this.equipmentContainer.getElementsByClassName('equipment-slot');
    Array.from(slots).forEach(slot => {
      const slotElement = slot as HTMLElement;
      const slotName = slotElement.dataset.slot as keyof Equipment;
      const itemContainer = slotElement.querySelector('.slot-item') as HTMLElement;
      const item = this.currentCharacter!.equipment[slotName];
      itemContainer.innerHTML = '';
      itemContainer.classList.remove('equipped', 'broken', 'disabled', 'empowered', 'damaged', 'repaired');
      if (item) {
        // Main icon
        itemContainer.innerHTML = `<img src="${item.icon}" alt="${item.name}">`;
        itemContainer.classList.add('equipped');
        // State overlay
        if (item.state) {
          itemContainer.classList.add(item.state);
          if (item.state === EquipmentState.BROKEN) {
            itemContainer.innerHTML += '<span class="state-overlay" title="Broken">&#9888;</span>';
          } else if (item.state === EquipmentState.DISABLED) {
            itemContainer.innerHTML += '<span class="state-overlay" title="Disabled">&#9940;</span>';
          } else if (item.state === EquipmentState.EMPOWERED) {
            itemContainer.innerHTML += '<span class="state-overlay empowered" title="Empowered">&#9889;</span>';
          } else if (item.state === EquipmentState.DAMAGED) {
            itemContainer.innerHTML += '<span class="state-overlay damaged" title="Damaged">&#128165;</span>';
          } else if (item.state === EquipmentState.REPAIRED) {
            itemContainer.innerHTML += '<span class="state-overlay repaired" title="Repaired">&#128295;</span>';
          }
        }
        // Durability bar
        if (typeof item.durability === 'number' && typeof item.maxDurability === 'number') {
          const percent = Math.round((item.durability / item.maxDurability) * 100);
          itemContainer.innerHTML += `<div class="durability-bar" title="Durability: ${item.durability}/${item.maxDurability}"><div class="durability-fill" style="width:${percent}%"></div></div>`;
        }
        // Tooltip and unequip
        itemContainer.addEventListener('mouseenter', (e) => this.showItemTooltip(e, item));
        itemContainer.addEventListener('mouseleave', () => this.hideTooltip());
        itemContainer.addEventListener('click', () => this.unequipItem(slotName));
      }
    });
    this.updateCharacterPreview();
  }

  private showItemTooltip(event: MouseEvent, item: InventoryItem): void {
    const tooltipContent = `
      <div style="margin-bottom: 10px;">
        <strong>${item.name}</strong>
      </div>
      <div style="color: #aaa; font-size: 12px;">
        ${item.type.charAt(0).toUpperCase() + item.type.slice(1)}
      </div>
      <div style="margin: 10px 0;">
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
      <div style="margin-top: 10px; color: #aaa; font-style: italic;">
        Click to unequip
      </div>
    `;

    this.tooltipElement.innerHTML = tooltipContent;
    this.tooltipElement.style.display = 'block';

    const rect = (event.target as HTMLElement).getBoundingClientRect();
    this.tooltipElement.style.left = `${rect.right + 10}px`;
    this.tooltipElement.style.top = `${rect.top}px`;
  }

  private hideTooltip(): void {
    this.tooltipElement.style.display = 'none';
  }

  private unequipItem(slot: keyof Equipment): void {
    if (!this.currentCharacter) return;

    const item = this.currentCharacter.equipment[slot];
    if (item) {
      this.notifyListeners({
        type: 'unequip',
        character: this.currentCharacter,
        data: { item, slot }
      });
      this.updateEquipmentDisplay();
    }
  }

  private updateCharacterPreview(): void {
    // This is a placeholder for character preview rendering
    // In a real implementation, this would update the character's appearance
    // based on equipped items, possibly using layered images or a 3D model
  }

  public updateEquipment(character: Character): void {
    this.currentCharacter = character;
    this.updateEquipmentDisplay();
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
    const slots = this.equipmentContainer.getElementsByClassName('slot-item');
    Array.from(slots).forEach(slot => {
      slot.innerHTML = '';
      slot.classList.remove('equipped');
    });
  }

  public dispose(): void {
    this.tooltipElement.remove();
    this.container.innerHTML = '';
    this.listeners = [];
  }

  public setEquipmentState(item: InventoryItem, state: EquipmentState): void {
    item.state = state;
    this.updateEquipmentDisplay();
    if (this.currentCharacter) {
      this.notifyListeners({
        type: 'equipmentStateChange',
        character: this.currentCharacter!,
        data: { item, state }
      });
    }
  }

  public updateDurability(item: InventoryItem, delta: number): void {
    if (typeof item.durability !== 'number' || typeof item.maxDurability !== 'number') return;
    item.durability = Math.max(0, Math.min(item.maxDurability, item.durability + delta));
    if (item.durability === 0) {
      this.setEquipmentState(item, EquipmentState.BROKEN);
    } else if (item.state === EquipmentState.BROKEN && item.durability > 0) {
      this.setEquipmentState(item, EquipmentState.REPAIRED);
    }
    this.updateEquipmentDisplay();
  }

  public addStateValidator(validator: (item: InventoryItem, character: Character) => boolean): void {
    this.stateValidators.push(validator);
  }

  private validateEquipmentState(item: InventoryItem, character: Character): boolean {
    return this.stateValidators.every(validator => validator(item, character));
  }
} 