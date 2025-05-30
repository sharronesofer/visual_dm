from typing import Any, Dict, List


class SkillTreeRenderer {
  private container: HTMLElement
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private tooltipElement: HTMLElement
  private nodes: List[SkillTreeNode] = []
  private currentCharacter: Character | null = null
  private listeners: ((event: CharacterUIEvent) => void)[] = []
  private isDragging: bool = false
  private dragStart: Dict[str, Any] | null = null
  private viewOffset: Dict[str, Any] = { x: 0, y: 0 }
  private zoom: float = 1
  private selectedNode: SkillTreeNode | null = null
  private hoveredNode: SkillTreeNode | null = null
  private readonly nodeRadius: float = 30
  private readonly nodeSpacing: float = 100
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.canvas = document.createElement('canvas')
    this.ctx = this.canvas.getContext('2d')!
    this.tooltipElement = this.createTooltip()
    this.initializeRenderer()
  }
  private createTooltip(): HTMLElement {
    const tooltip = document.createElement('div')
    tooltip.className = 'skill-tooltip'
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
  private initializeRenderer(): void {
    this.container.innerHTML = ''
    this.container.className = 'skill-tree-renderer'
    this.canvas.className = 'skill-tree-canvas'
    this.container.appendChild(this.canvas)
    this.setupEventListeners()
    const style = document.createElement('style')
    style.textContent = `
      .skill-tree-renderer {
        width: 100
        height: 100
        min-height: 500px
        background: rgba(0, 0, 0, 0.1)
        border-radius: 8px
        overflow: hidden
        position: relative
      }
      .skill-tree-canvas {
        width: 100
        height: 100
        cursor: grab
      }
      .skill-tree-canvas:active {
        cursor: grabbing
      }
      .skill-tooltip {
        pointer-events: none
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5)
      }
    `
    document.head.appendChild(style)
    this.handleResize()
  }
  private setupEventListeners(): void {
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this))
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this))
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this))
    this.canvas.addEventListener('wheel', this.handleWheel.bind(this))
    window.addEventListener('resize', this.handleResize.bind(this))
  }
  private handleResize(): void {
    const rect = this.container.getBoundingClientRect()
    this.canvas.width = rect.width
    this.canvas.height = rect.height
    this.render()
  }
  private handleMouseDown(event: MouseEvent): void {
    const rect = this.canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    const node = this.findNodeAtPosition(x, y)
    if (node) {
      this.selectedNode = node
      this.render()
      this.notifyListeners({
        type: 'select',
        character: this.currentCharacter!,
        data: Dict[str, Any]
      })
    } else {
      this.isDragging = true
      this.dragStart = { x, y }
    }
  }
  private handleMouseMove(event: MouseEvent): void {
    const rect = this.canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    if (this.isDragging && this.dragStart) {
      const dx = x - this.dragStart.x
      const dy = y - this.dragStart.y
      this.viewOffset.x += dx
      this.viewOffset.y += dy
      this.dragStart = { x, y }
      this.render()
    } else {
      const node = this.findNodeAtPosition(x, y)
      if (node !== this.hoveredNode) {
        this.hoveredNode = node
        this.render()
        if (node) {
          this.showSkillTooltip(event, node.skill)
        } else {
          this.hideTooltip()
        }
      }
    }
  }
  private handleMouseUp(): void {
    this.isDragging = false
    this.dragStart = null
  }
  private handleWheel(event: WheelEvent): void {
    event.preventDefault()
    const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
    this.zoom = Math.max(0.5, Math.min(2, this.zoom * zoomFactor))
    this.render()
  }
  private findNodeAtPosition(x: float, y: float): SkillTreeNode | null {
    const transformedX = (x - this.viewOffset.x) / this.zoom
    const transformedY = (y - this.viewOffset.y) / this.zoom
    return this.nodes.find(node => {
      const dx = node.position.x - transformedX
      const dy = node.position.y - transformedY
      return Math.sqrt(dx * dx + dy * dy) <= this.nodeRadius
    }) || null
  }
  private showSkillTooltip(event: MouseEvent, skill: CharacterSkill): void {
    const tooltipContent = `
      <div style="margin-bottom: 10px;">
        <strong>${skill.name}</strong>
        <span style="float: right;">Level ${skill.level}/${skill.maxLevel}</span>
      </div>
      <div style="margin-bottom: 10px;">
        ${skill.description}
      </div>
      ${skill.effects.map(effect => `
        <div style="color: #8f8; margin: 5px 0;">
          ${effect.type}: ${effect.value}
          ${effect.duration ? ` for ${effect.duration}s` : ''}
          (${effect.target})
        </div>
      `).join('')}
      ${skill.prerequisites.length > 0 ? `
        <div style="margin-top: 10px; color: #aaa;">
          Prerequisites: ${skill.prerequisites.join(', ')}
        </div>
      ` : ''}
    `
    this.tooltipElement.innerHTML = tooltipContent
    this.tooltipElement.style.display = 'block'
    const rect = this.canvas.getBoundingClientRect()
    this.tooltipElement.style.left = `${event.clientX - rect.left + 20}px`
    this.tooltipElement.style.top = `${event.clientY - rect.top + 20}px`
  }
  private hideTooltip(): void {
    this.tooltipElement.style.display = 'none'
  }
  private render(): void {
    if (!this.ctx) return
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    this.ctx.save()
    this.ctx.translate(this.viewOffset.x, this.viewOffset.y)
    this.ctx.scale(this.zoom, this.zoom)
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
    this.ctx.lineWidth = 2
    this.nodes.forEach(node => {
      node.connections.forEach(targetId => {
        const targetNode = this.nodes.find(n => n.skill.id === targetId)
        if (targetNode) {
          this.ctx.beginPath()
          this.ctx.moveTo(node.position.x, node.position.y)
          this.ctx.lineTo(targetNode.position.x, targetNode.position.y)
          this.ctx.stroke()
        }
      })
    })
    this.nodes.forEach(node => {
      this.ctx.beginPath()
      this.ctx.arc(node.position.x, node.position.y, this.nodeRadius, 0, Math.PI * 2)
      if (node === this.selectedNode) {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
      } else if (node === this.hoveredNode) {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
      } else {
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
      }
      this.ctx.fill()
      this.ctx.strokeStyle = node.unlocked ? '#8f8' : '#888'
      this.ctx.lineWidth = 2
      this.ctx.stroke()
      if (node.skill.icon) {
        const img = new Image()
        img.src = node.skill.icon
        const iconSize = this.nodeRadius * 1.2
        this.ctx.drawImage(
          img,
          node.position.x - iconSize / 2,
          node.position.y - iconSize / 2,
          iconSize,
          iconSize
        )
      }
      if (node.skill.level > 0) {
        this.ctx.fillStyle = '#fff'
        this.ctx.font = '12px Arial'
        this.ctx.textAlign = 'center'
        this.ctx.textBaseline = 'bottom'
        this.ctx.fillText(
          `${node.skill.level}/${node.skill.maxLevel}`,
          node.position.x,
          node.position.y + this.nodeRadius + 15
        )
      }
    })
    this.ctx.restore()
  }
  public updateSkillTree(character: Character): void {
    this.currentCharacter = character
    this.nodes = this.layoutSkillTree(character.skills)
    this.render()
  }
  private layoutSkillTree(skills: List[CharacterSkill]): SkillTreeNode[] {
    const nodes: List[SkillTreeNode] = []
    const gridSize = Math.ceil(Math.sqrt(skills.length))
    const startX = this.canvas.width / (2 * this.zoom) - (gridSize * this.nodeSpacing) / 2
    const startY = this.canvas.height / (2 * this.zoom) - (gridSize * this.nodeSpacing) / 2
    skills.forEach((skill, index) => {
      const row = Math.floor(index / gridSize)
      const col = index % gridSize
      nodes.push({
        skill,
        position: Dict[str, Any],
        connections: skill.prerequisites,
        unlocked: skill.level > 0
      })
    })
    return nodes
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
    this.nodes = []
    this.selectedNode = null
    this.hoveredNode = null
    this.viewOffset = { x: 0, y: 0 }
    this.zoom = 1
    this.render()
  }
  public dispose(): void {
    this.tooltipElement.remove()
    this.container.innerHTML = ''
    this.listeners = []
    window.removeEventListener('resize', this.handleResize.bind(this))
  }
} 