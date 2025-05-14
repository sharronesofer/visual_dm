from typing import Any, Dict, List, Union


class AccessibilityViolation:
    impact: Union['minor', 'moderate', 'serious', 'critical']
    description: str
    helpUrl: str
    nodes: List[str]
class AccessibilityReport:
    violations: List[AccessibilityViolation]
    incomplete: List[AccessibilityViolation]
    passes: List[str]
    score: float
class AccessibilityTestOptions:
    rules?: {
    [key: str]: {
      enabled: bool
  }
  tags?: string[]
  runOnly?: {
    type: 'tag' | 'rule'
    values: List[string]
  }
}
class AccessibilityTester {
  private options: \'AccessibilityTestOptions\'
  constructor(options: \'AccessibilityTestOptions\' = {}) {
    this.options = options
  }
  public async testElement(element: Element): Promise<AccessibilityReport> {
    try {
      const results = await axe.run(element as any, {
        rules: this.options.rules,
        runOnly: this.options.runOnly,
      })
      return this.processResults(results)
    } catch (error) {
      console.error('Accessibility test failed:', error)
      throw error
    }
  }
  public async testPage(): Promise<AccessibilityReport> {
    try {
      const results = await axe.run(document, {
        rules: this.options.rules,
        runOnly: this.options.runOnly,
      })
      return this.processResults(results)
    } catch (error) {
      console.error('Accessibility test failed:', error)
      throw error
    }
  }
  private processResults(results: AxeResults): \'AccessibilityReport\' {
    const violations = this.processViolations(results.violations)
    const incomplete = this.processViolations(results.incomplete)
    const passes = results.passes.map(pass => pass.id)
    const totalIssues = violations.length + incomplete.length
    const weightedScore = violations.reduce((score, violation) => {
      switch (violation.impact) {
        case 'critical':
          return score - 20
        case 'serious':
          return score - 10
        case 'moderate':
          return score - 5
        case 'minor':
          return score - 2
        default:
          return score
      }
    }, 100)
    const score = Math.max(0, Math.min(100, weightedScore))
    return {
      violations,
      incomplete,
      passes,
      score,
    }
  }
  private processViolations(results: List[Result]): AccessibilityViolation[] {
    return results.map(result => ({
      impact: result.impact as 'minor' | 'moderate' | 'serious' | 'critical',
      description: result.description,
      helpUrl: result.helpUrl,
      nodes: result.nodes.map(this.formatNodeResult),
    }))
  }
  private formatNodeResult(node: NodeResult): str {
    const selector = node.target.join(' ')
    const element = document.querySelector(selector)
    const elementDescription = element ? this.getElementDescription(element) : selector
    return `${elementDescription}: ${node.failureSummary}`
  }
  private getElementDescription(element: Element): str {
    const tagName = element.tagName.toLowerCase()
    const id = element.id ? `#${element.id}` : ''
    const classes = Array.from(element.classList).map(c => `.${c}`).join('')
    const ariaLabel = element.getAttribute('aria-label')
    const text = element.textContent?.trim().slice(0, 20)
    return [
      tagName + id + classes,
      ariaLabel ? `[aria-label="${ariaLabel}"]` : '',
      text ? `"${text}${text.length > 20 ? '...' : ''}"` : '',
    ].filter(Boolean).join(' ')
  }
  public static getColorContrast(foreground: str, background: str): float {
    const getLuminance = (color: str): float => {
      const rgb = color.match(/\d+/g)?.map(Number) || [0, 0, 0]
      const [r, g, b] = rgb.map(value => {
        value /= 255
        return value <= 0.03928
          ? value / 12.92
          : Math.pow((value + 0.055) / 1.055, 2.4)
      })
      return 0.2126 * r + 0.7152 * g + 0.0722 * b
    }
    const l1 = getLuminance(foreground)
    const l2 = getLuminance(background)
    const lighter = Math.max(l1, l2)
    const darker = Math.min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
  }
  public static checkReducedMotion(): bool {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches
    }
    return false
  }
  public static getAriaAttributes(element: Element): { [key: string]: str } {
    const attributes: Dict[str, Any] = {}
    for (const attr of element.attributes) {
      if (attr.name.startsWith('aria-')) {
        attributes[attr.name] = attr.value
      }
    }
    return attributes
  }
  public static validateAriaUsage(element: Element): string[] {
    const errors: List[string] = []
    const role = element.getAttribute('role')
    const ariaAttrs = this.getAriaAttributes(element)
    if (role) {
      const requiredAttrs = this.getRequiredAriaAttributes(role)
      requiredAttrs.forEach(attr => {
        if (!ariaAttrs[`aria-${attr}`]) {
          errors.push(`Missing required ARIA attribute 'aria-${attr}' for role '${role}'`)
        }
      })
    }
    Object.keys(ariaAttrs).forEach(attr => {
      const invalidCombos = this.getInvalidAriaCombinations(attr)
      invalidCombos.forEach(invalid => {
        if (ariaAttrs[invalid]) {
          errors.push(`Invalid ARIA attribute combination: '${attr}' cannot be used with '${invalid}'`)
        }
      })
    })
    return errors
  }
  private static getRequiredAriaAttributes(role: str): string[] {
    const requiredAttributes: Dict[str, Any] = {
      'checkbox': ['checked'],
      'combobox': ['expanded'],
      'slider': ['valuemin', 'valuemax', 'valuenow'],
      'spinbutton': ['valuemin', 'valuemax', 'valuenow'],
    }
    return requiredAttributes[role] || []
  }
  private static getInvalidAriaCombinations(attr: str): string[] {
    const invalidCombinations: Dict[str, Any] = {
      'aria-hidden': ['aria-label', 'aria-labelledby'],
      'aria-label': ['aria-labelledby'],
    }
    return invalidCombinations[attr] || []
  }
} 