from typing import Any, Dict



class CharacterUIController {
  private container: HTMLElement
  private statDisplay!: StatDisplay
  private inventoryPanel!: InventoryPanel
  private equipmentManager!: EquipmentManager
  private skillTreeRenderer!: SkillTreeRenderer
  private currentCharacter: Character | null = null
  private state: CharacterUIState = {
    selectedCharacter: null,
    selectedInventoryItem: null,
    selectedSkill: null,
    comparisonItem: null,
    inventoryFilter: null,
    inventorySort: 'name',
    showTooltip: false,
    tooltipPosition: Dict[str, Any]
  }
  private options: CharacterUIOptions = {
    showComparison: true,
    showStatChanges: true,
    showSkillTree: true,
    showInventory: true,
    showEquipment: true,
    showTraits: true,
    showProgression: true
  }
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.initializeController()
  }
  private initializeController(): void {
    this.container.innerHTML = ''
    this.container.className = 'character-ui'
    const statsContainer = document.createElement('div')
    statsContainer.id = 'character-stats'
    statsContainer.className = 'character-stats-container'
    const equipmentContainer = document.createElement('div')
    equipmentContainer.id = 'character-equipment'
    equipmentContainer.className = 'character-equipment-container'
    const inventoryContainer = document.createElement('div')
    inventoryContainer.id = 'character-inventory'
    inventoryContainer.className = 'character-inventory-container'
    const skillTreeContainer = document.createElement('div')
    skillTreeContainer.id = 'character-skills'
    skillTreeContainer.className = 'character-skills-container'
    this.statDisplay = new StatDisplay('character-stats')
    this.equipmentManager = new EquipmentManager('character-equipment')
    this.inventoryPanel = new InventoryPanel('character-inventory')
    this.skillTreeRenderer = new SkillTreeRenderer('character-skills')
    this.setupEventListeners()
    this.container.appendChild(statsContainer)
    this.container.appendChild(equipmentContainer)
    this.container.appendChild(inventoryContainer)
    this.container.appendChild(skillTreeContainer)
    const style = document.createElement('style')
    style.textContent = `
      .character-ui {
        display: grid
        grid-template-columns: 300px 1fr
        grid-template-rows: auto 1fr
        gap: 20px
        padding: 20px
        height: 100
        min-height: 600px
        background: rgba(0, 0, 0, 0.2)
        border-radius: 10px
      }
      .character-stats-container {
        grid-column: 1
        grid-row: 1
      }
      .character-equipment-container {
        grid-column: 1
        grid-row: 2
      }
      .character-inventory-container {
        grid-column: 2
        grid-row: 1
      }
      .character-skills-container {
        grid-column: 2
        grid-row: 2
      }
      @media (max-width: 1200px) {
        .character-ui {
          grid-template-columns: 1fr
          grid-template-rows: auto auto 1fr 1fr
        }
        .character-stats-container {
          grid-column: 1
          grid-row: 1
        }
        .character-equipment-container {
          grid-column: 1
          grid-row: 2
        }
        .character-inventory-container {
          grid-column: 1
          grid-row: 3
        }
        .character-skills-container {
          grid-column: 1
          grid-row: 4
        }
      }
    `
    document.head.appendChild(style)
  }
  private setupEventListeners(): void {
    this.equipmentManager.addListener((event: CharacterUIEvent) => {
      if (!this.currentCharacter) return
      switch (event.type) {
        case 'equip': {
          const { item, slot } = event.data
          if (this.isValidEquipmentSlot(slot)) {
            const validTypes = this.getValidItemTypesForSlot(slot)
            if (validTypes.includes(item.type)) {
              this.currentCharacter.equipment[slot] = item
              this.updateUI()
            } else {
              console.warn(`Invalid item type ${item.type} for slot ${slot}`)
            }
          }
          break
        }
        case 'unequip': {
          const { slot } = event.data
          if (this.isValidEquipmentSlot(slot)) {
            this.currentCharacter.equipment[slot] = null
            this.updateUI()
          }
          break
        }
      }
    })
    this.inventoryPanel.addListener((event: CharacterUIEvent) => {
      if (!this.currentCharacter) return
      switch (event.type) {
        case 'select':
          const { item } = event.data
          this.state.selectedInventoryItem = item
          if (this.options.showComparison) {
            this.state.comparisonItem = item
          }
          this.updateUI()
          break
        case 'useItem':
          const { item: usedItem } = event.data
          this.updateUI()
          break
      }
    })
    this.skillTreeRenderer.addListener((event: CharacterUIEvent) => {
      if (!this.currentCharacter) return
      switch (event.type) {
        case 'select':
          const { skill } = event.data
          this.state.selectedSkill = skill
          this.updateUI()
          break
        case 'learnSkill':
          const { skill: learnedSkill } = event.data
          this.updateUI()
          break
      }
    })
  }
  private isValidEquipmentSlot(slot: str): slot is keyof Equipment {
    const validSlots: Array<keyof Equipment> = ['weapon', 'armor', 'accessory1', 'accessory2']
    return validSlots.includes(slot as keyof Equipment)
  }
  private getValidItemTypesForSlot(slot: keyof Equipment): ItemType[] {
    const validTypes: Record<keyof Equipment, ItemType[]> = {
      weapon: [ItemType.WEAPON],
      armor: [ItemType.ARMOR],
      accessory1: [ItemType.ACCESSORY],
      accessory2: [ItemType.ACCESSORY]
    }
    return validTypes[slot]
  }
  private calculateStatModifiers(): Record<keyof CharacterStats, StatModifier[]> {
    if (!this.currentCharacter) {
      return this.getDefaultStats()
    }
    const modifiers: Record<keyof CharacterStats, StatModifier[]> = this.getDefaultStats()
    Object.entries(this.currentCharacter.equipment).forEach(([slot, item]) => {
      if (item && this.isValidEquipmentSlot(slot)) {
        Object.entries(item.stats).forEach(([stat, value]) => {
          if (this.isValidStat(stat) && typeof value === 'number') {
            modifiers[stat].push({
              source: `${item.name} (${slot})`,
              value: value,
              type: 'equipment'
            })
          }
        })
      }
    })
    this.currentCharacter.skills.forEach(skill => {
      if (skill.level > 0) {
        skill.effects.forEach(effect => {
          if (this.isValidStat(effect.type)) {
            modifiers[effect.type].push({
              source: `${skill.name} (Level ${skill.level})`,
              value: effect.value,
              type: 'skill'
            })
          }
        })
      }
    })
    this.currentCharacter.traits.forEach(trait => {
      trait.effects.forEach(effect => {
        if (this.isValidStat(effect.type)) {
          modifiers[effect.type].push({
            source: trait.name,
            value: effect.value,
            type: 'trait'
          })
        }
      })
    })
    return modifiers
  }
  private getDefaultStats(): Record<keyof CharacterStats, StatModifier[]> {
    return {
      strength: [],
      dexterity: [],
      constitution: [],
      intelligence: [],
      wisdom: [],
      charisma: []
    }
  }
  private isValidStat(stat: str): stat is keyof CharacterStats {
    const validStats: Array<keyof CharacterStats> = [
      'strength',
      'dexterity',
      'constitution',
      'intelligence',
      'wisdom',
      'charisma'
    ]
    return validStats.includes(stat as keyof CharacterStats)
  }
  private updateUI(): void {
    if (!this.currentCharacter) return
    this.statDisplay.updateStats({
      ...this.currentCharacter.stats,
      modifiers: this.calculateStatModifiers()
    })
    this.equipmentManager.updateEquipment(this.currentCharacter)
    this.inventoryPanel.updateInventory(this.currentCharacter)
    this.skillTreeRenderer.updateSkillTree(this.currentCharacter)
  }
  public setCharacter(character: Character): void {
    this.currentCharacter = character
    this.state.selectedCharacter = character
    this.updateUI()
  }
  public setOptions(options: Partial<CharacterUIOptions>): void {
    this.options = { ...this.options, ...options }
    this.updateUI()
  }
  public getState(): CharacterUIState {
    return { ...this.state }
  }
  public clear(): void {
    this.currentCharacter = null
    this.state = {
      selectedCharacter: null,
      selectedInventoryItem: null,
      selectedSkill: null,
      comparisonItem: null,
      inventoryFilter: null,
      inventorySort: 'name',
      showTooltip: false,
      tooltipPosition: Dict[str, Any]
    }
    this.statDisplay.clear()
    this.equipmentManager.clear()
    this.inventoryPanel.clear()
    this.skillTreeRenderer.clear()
  }
  public dispose(): void {
    this.statDisplay.dispose()
    this.equipmentManager.dispose()
    this.inventoryPanel.dispose()
    this.skillTreeRenderer.dispose()
    this.container.innerHTML = ''
  }
} 