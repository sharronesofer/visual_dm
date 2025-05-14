from typing import Any, List


class StatDisplay {
  private container: HTMLElement
  private statElements: Map<keyof CharacterStats, HTMLElement> = new Map()
  private modifierElements: Map<keyof CharacterStats, HTMLElement> = new Map()
  private tooltipElement: HTMLElement
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.tooltipElement = this.createTooltip()
    this.initializeDisplay()
  }
  private createTooltip(): HTMLElement {
    const tooltip = document.createElement('div')
    tooltip.className = 'stat-tooltip'
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
  private initializeDisplay(): void {
    this.container.innerHTML = ''
    this.container.className = 'stat-display'
    const stats: (keyof CharacterStats)[] = [
      'strength',
      'dexterity',
      'constitution',
      'intelligence',
      'wisdom',
      'charisma'
    ]
    stats.forEach(stat => {
      const statContainer = document.createElement('div')
      statContainer.className = 'stat-container'
      const label = document.createElement('div')
      label.className = 'stat-label'
      label.textContent = this.formatStatName(stat)
      const value = document.createElement('div')
      value.className = 'stat-value'
      this.statElements.set(stat, value)
      const modifier = document.createElement('div')
      modifier.className = 'stat-modifier'
      this.modifierElements.set(stat, modifier)
      statContainer.appendChild(label)
      statContainer.appendChild(value)
      statContainer.appendChild(modifier)
      statContainer.addEventListener('mouseenter', (e) => this.showStatTooltip(e, stat))
      statContainer.addEventListener('mouseleave', () => this.hideTooltip())
      this.container.appendChild(statContainer)
    })
    const style = document.createElement('style')
    style.textContent = `
      .stat-display {
        display: grid
        grid-template-columns: repeat(2, 1fr)
        gap: 10px
        padding: 15px
        background: rgba(0, 0, 0, 0.1)
        border-radius: 8px
      }
      .stat-container {
        display: flex
        flex-direction: column
        align-items: center
        padding: 10px
        background: rgba(255, 255, 255, 0.1)
        border-radius: 5px
        transition: background-color 0.2s
      }
      .stat-container:hover {
        background: rgba(255, 255, 255, 0.2)
      }
      .stat-label {
        font-size: 14px
        color: #ccc
        text-transform: uppercase
      }
      .stat-value {
        font-size: 24px
        font-weight: bold
        color: white
        margin: 5px 0
      }
      .stat-modifier {
        font-size: 12px
        color: #8f8
      }
      .stat-modifier.negative {
        color: #f88
      }
      .stat-tooltip {
        pointer-events: none
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5)
      }
    `
    document.head.appendChild(style)
  }
  private formatStatName(stat: keyof CharacterStats): str {
    return stat.charAt(0).toUpperCase() + stat.slice(1)
  }
  private formatModifier(value: float): str {
    return value >= 0 ? `+${value}` : `${value}`
  }
  private showStatTooltip(event: MouseEvent, stat: keyof CharacterStats): void {
    const modifiers = this.currentStats?.modifiers[stat] || []
    if (modifiers.length === 0) {
      return
    }
    const tooltipContent = this.createTooltipContent(stat, modifiers)
    this.tooltipElement.innerHTML = tooltipContent
    this.tooltipElement.style.display = 'block'
    const rect = (event.target as HTMLElement).getBoundingClientRect()
    this.tooltipElement.style.left = `${rect.right + 10}px`
    this.tooltipElement.style.top = `${rect.top}px`
  }
  private hideTooltip(): void {
    this.tooltipElement.style.display = 'none'
  }
  private createTooltipContent(stat: keyof CharacterStats, modifiers: List[StatModifier]): str {
    const total = modifiers.reduce((sum, mod) => sum + mod.value, 0)
    return `
      <div style="margin-bottom: 10px;">
        <strong>${this.formatStatName(stat)} Modifiers</strong>
      </div>
      ${modifiers.map(mod => `
        <div style="display: flex; justify-content: space-between; margin: 5px 0;">
          <span>${mod.source}</span>
          <span style="color: ${mod.value >= 0 ? '#8f8' : '#f88'}">
            ${this.formatModifier(mod.value)}
          </span>
        </div>
      `).join('')}
      <div style="border-top: 1px solid rgba(255, 255, 255, 0.2); margin-top: 10px; padding-top: 5px;">
        <strong>Total:</strong>
        <span style="float: right; color: ${total >= 0 ? '#8f8' : '#f88'}">
          ${this.formatModifier(total)}
        </span>
      </div>
    `
  }
  private currentStats: CalculatedStats | null = null
  public updateStats(stats: CalculatedStats): void {
    this.currentStats = stats
    Object.entries(stats).forEach(([stat, value]) => {
      if (stat !== 'modifiers') {
        const statElement = this.statElements.get(stat as keyof CharacterStats)
        const modifierElement = this.modifierElements.get(stat as keyof CharacterStats)
        if (statElement && modifierElement) {
          statElement.textContent = value.toString()
          const modifiers = stats.modifiers[stat as keyof CharacterStats]
          const totalModifier = modifiers.reduce((sum, mod) => sum + mod.value, 0)
          if (totalModifier !== 0) {
            modifierElement.textContent = this.formatModifier(totalModifier)
            modifierElement.className = `stat-modifier ${totalModifier < 0 ? 'negative' : ''}`
          } else {
            modifierElement.textContent = ''
          }
        }
      }
    })
  }
  public clear(): void {
    this.currentStats = null
    this.statElements.forEach(element => {
      element.textContent = '0'
    })
    this.modifierElements.forEach(element => {
      element.textContent = ''
    })
  }
  public dispose(): void {
    this.tooltipElement.remove()
    this.container.innerHTML = ''
  }
} 