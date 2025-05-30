from typing import Any, Dict, List


class POITemplate:
    id: str
    name: str
    type: str
    rarity: float
    allowedTerrains: List[str]
    minDistance: float
    maxDistance?: float
    effects?: Dict[str, Any>
class POIInstance:
    id: str
    templateId: str
    q: float
    r: float
    discovered: bool
class POIGeneratorOptions:
    seed?: float
    maxPOIs?: float
function generatePOIs(
  grid: HexGrid,
  templates: List[POITemplate],
  options: \'POIGeneratorOptions\' = {}
): POIInstance[] {
  const {
    seed = 42,
    maxPOIs = 10
  } = options
  const pois: List[POIInstance] = []
  let poiCount = 0
  let attempt = 0
  const maxAttempts = maxPOIs * 20
  while (poiCount < maxPOIs && attempt < maxAttempts) {
    attempt++
    const totalWeight = templates.reduce((sum, t) => sum + (1 - t.rarity), 0)
    let pick = (pseudoRandom(attempt, seed, 1) * totalWeight)
    let template: \'POITemplate\' | undefined
    for (const t of templates) {
      pick -= (1 - t.rarity)
      if (pick <= 0) {
        template = t
        break
      }
    }
    if (!template) template = templates[0]
    const q = Math.floor(pseudoRandom(attempt, seed, 2) * grid.width)
    const r = Math.floor(pseudoRandom(attempt, seed, 3) * grid.height)
    const cell = grid.get(q, r)
    if (!cell) continue
    if (!template.allowedTerrains.includes(cell.terrain)) continue
    let tooClose = false
    for (const poi of pois) {
      const dist = grid.distance(q, r, poi.q, poi.r)
      if (dist < template.minDistance) tooClose = true
      if (template.maxDistance && dist > template.maxDistance) tooClose = true
    }
    if (tooClose) continue
    pois.push({
      id: `poi-${poiCount}`,
      templateId: template.id,
      q,
      r,
      discovered: false
    })
    poiCount++
  }
  return pois
}
function pseudoRandom(a: float, b: float, c: float): float {
  let x = a * 374761393 + b * 668265263 + c * 982451653
  x = (x ^ (x >> 13)) * 1274126177
  return ((x ^ (x >> 16)) >>> 0) / 0xffffffff
}
class ResourceTemplate:
    id: str
    name: str
    type: str
    rarity: float
    allowedTerrains: List[str]
    clusterChance?: float
    clusterSize?: float
class ResourceInstance:
    id: str
    templateId: str
    q: float
    r: float
    amount: float
    depleted: bool
class ResourceGeneratorOptions:
    seed?: float
    maxResources?: float
function generateResources(
  grid: HexGrid,
  resourceTemplates: List[ResourceTemplate],
  pois: List[POIInstance],
  options: \'ResourceGeneratorOptions\' = {}
): ResourceInstance[] {
  const {
    seed = 99,
    maxResources = 30
  } = options
  const resources: List[ResourceInstance] = []
  let resourceCount = 0
  let attempt = 0
  const maxAttempts = maxResources * 20
  while (resourceCount < maxResources && attempt < maxAttempts) {
    attempt++
    const totalWeight = resourceTemplates.reduce((sum, t) => sum + (1 - t.rarity), 0)
    let pick = (pseudoRandom(attempt, seed, 1) * totalWeight)
    let template: \'ResourceTemplate\' | undefined
    for (const t of resourceTemplates) {
      pick -= (1 - t.rarity)
      if (pick <= 0) {
        template = t
        break
      }
    }
    if (!template) template = resourceTemplates[0]
    const q = Math.floor(pseudoRandom(attempt, seed, 2) * grid.width)
    const r = Math.floor(pseudoRandom(attempt, seed, 3) * grid.height)
    const cell = grid.get(q, r)
    if (!cell) continue
    if (!template.allowedTerrains.includes(cell.terrain)) continue
    let nearPOI = false
    for (const poi of pois) {
      const dist = grid.distance(q, r, poi.q, poi.r)
      if (dist <= 2) nearPOI = true
    }
    let clustered = false
    if (template.clusterChance && pseudoRandom(attempt, seed, 4) < template.clusterChance) {
      clustered = true
      const clusterSize = template.clusterSize || 2
      for (let i = 0; i < clusterSize; i++) {
        const dq = Math.floor(pseudoRandom(attempt, seed, 5 + i) * 3) - 1
        const dr = Math.floor(pseudoRandom(attempt, seed, 6 + i) * 3) - 1
        const cq = q + dq
        const cr = r + dr
        const ccell = grid.get(cq, cr)
        if (!ccell || !template.allowedTerrains.includes(ccell.terrain)) continue
        resources.push({
          id: `res-${resourceCount}`,
          templateId: template.id,
          q: cq,
          r: cr,
          amount: 100,
          depleted: false
        })
        resourceCount++
        if (resourceCount >= maxResources) break
      }
      continue
    }
    resources.push({
      id: `res-${resourceCount}`,
      templateId: template.id,
      q,
      r,
      amount: 100,
      depleted: false
    })
    resourceCount++
  }
  return resources
}
function discoverPOI(pois: List[POIInstance], q: float, r: float, radius: float): void {
  for (const poi of pois) {
    const dist = Math.abs(poi.q - q) + Math.abs(poi.r - r)
    if (dist <= radius) poi.discovered = true
  }
}
function discoverResource(resources: List[ResourceInstance], q: float, r: float, radius: float): void {
  for (const res of resources) {
    const dist = Math.abs(res.q - q) + Math.abs(res.r - r)
    if (dist <= radius) res.depleted = false 
  }
}
function queryNearbyPOIs(pois: List[POIInstance], q: float, r: float, radius: float): POIInstance[] {
  return pois.filter(poi => poi.discovered && (Math.abs(poi.q - q) + Math.abs(poi.r - r) <= radius))
}
function queryNearbyResources(resources: List[ResourceInstance], q: float, r: float, radius: float): ResourceInstance[] {
  return resources.filter(res => !res.depleted && (Math.abs(res.q - q) + Math.abs(res.r - r) <= radius))
} 