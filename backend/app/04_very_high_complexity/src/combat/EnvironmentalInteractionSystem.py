from typing import Any, Dict, List, Union



class PhysicsProperties:
    mass: float
    friction: float
    restitution: float
    isMovable: bool
    isRotatable: bool
class ForceVector:
    magnitude: float
    direction: Dict[str, Any]
class PhysicsObject:
    physics: \'PhysicsProperties\'
    velocity: \'ForceVector\'
    angularVelocity: float
class InteractiveObject:
    id: str
    type: Union['destructible', 'lever', 'trap', 'resource', 'physics']
    position: Dict[str, Any]>
}
class EnvironmentalHazard:
    type: HazardType
    position: Dict[str, Any]>
}
class EnvironmentalInteractionSystem {
  private grid: TacticalHexGrid
  private interactiveObjects: Map<string, InteractiveObject>
  private hazards: Map<string, EnvironmentalHazard>
  private weatherEffects: Map<string, number>
  private physicsObjects: Map<string, PhysicsObject>
  constructor(grid: TacticalHexGrid) {
    this.grid = grid
    this.interactiveObjects = new Map()
    this.hazards = new Map()
    this.weatherEffects = new Map()
    this.physicsObjects = new Map()
  }
  addInteractiveObject(object: InteractiveObject): void {
    this.interactiveObjects.set(object.id, object)
  }
  updateHazard(hazard: EnvironmentalHazard): void {
    this.hazards.set(`${hazard.type}_${hazard.position.q}_${hazard.position.r}`, hazard)
  }
  interactWithObject(objectId: str, participant: CombatParticipant): bool {
    const object = this.interactiveObjects.get(objectId)
    if (!object) return false
    switch (object.type) {
      case 'destructible':
        return this.handleDestructibleInteraction(object, participant)
      case 'lever':
        return this.handleLeverInteraction(object)
      case 'trap':
        return this.handleTrapInteraction(object, participant)
      case 'resource':
        return this.handleResourceInteraction(object, participant)
      default:
        return false
    }
  }
  private handleDestructibleInteraction(object: \'InteractiveObject\', participant: CombatParticipant): bool {
    if (object.health && object.health > 0) {
      object.health -= participant.calculateDamage()
      if (object.health <= 0) {
        object.state = 'destroyed'
        const physicsObject = this.physicsObjects.get(object.id)
        if (physicsObject) {
          this.handlePhysicsObjectDestruction(physicsObject)
        } else {
          this.applyDestructionEffects(object)
        }
        return true
      }
    }
    return false
  }
  private handleLeverInteraction(object: InteractiveObject): bool {
    object.state = object.state === 'active' ? 'inactive' : 'active'
    this.applyLeverEffects(object)
    return true
  }
  private handleTrapInteraction(object: \'InteractiveObject\', participant: CombatParticipant): bool {
    if (object.state === 'active') {
      object.state = 'inactive'
      this.applyTrapEffects(object, participant)
      return true
    }
    return false
  }
  private handleResourceInteraction(object: \'InteractiveObject\', participant: CombatParticipant): bool {
    if (object.state !== 'destroyed') {
      object.state = 'destroyed'
      this.applyResourceEffects(object, participant)
      return true
    }
    return false
  }
  private applyDestructionEffects(object: InteractiveObject): void {
    for (const effect of object.effects) {
      if (effect.radius) {
        this.applyAreaEffect(object.position, effect)
      }
    }
  }
  private applyLeverEffects(object: InteractiveObject): void {
    for (const effect of object.effects) {
      if (object.state === 'active') {
        this.applyAreaEffect(object.position, effect)
      }
    }
  }
  private applyTrapEffects(object: \'InteractiveObject\', participant: CombatParticipant): void {
    for (const effect of object.effects) {
      participant.applyEffect(effect.type, effect.magnitude)
    }
  }
  private applyResourceEffects(object: \'InteractiveObject\', participant: CombatParticipant): void {
    for (const effect of object.effects) {
      participant.applyBuff(effect.type, effect.magnitude)
    }
  }
  private applyAreaEffect(center: Dict[str, Any], effect: Dict[str, Any]): void {
    if (!effect.radius) return
    const affectedCells = this.grid.getNeighborsInRange(center.q, center.r, effect.radius)
    for (const cell of affectedCells) {
      this.applyCellEffect(cell, effect)
    }
  }
  private applyCellEffect(cell: TacticalHexCell, effect: Dict[str, Any]): void {
    switch (effect.type) {
      case 'fire':
        cell.terrainEffect = 'burning'
        cell.cover = Math.max(0, cell.cover - effect.magnitude)
        break
      case 'water':
        cell.terrainEffect = 'flooded'
        cell.movementCost += effect.magnitude
        break
      case 'collapse':
        cell.terrainEffect = 'rubble'
        cell.cover = Math.min(1, cell.cover + effect.magnitude)
        cell.movementCost += effect.magnitude
        break
    }
  }
  addPhysicsObject(object: PhysicsObject): void {
    this.physicsObjects.set(object.id, object)
    this.interactiveObjects.set(object.id, object)
  }
  applyForce(objectId: str, force: ForceVector): bool {
    const object = this.physicsObjects.get(objectId)
    if (!object || !object.physics.isMovable) return false
    const acceleration = {
      q: force.direction.q * (force.magnitude / object.physics.mass),
      r: force.direction.r * (force.magnitude / object.physics.mass)
    }
    object.velocity = {
      magnitude: Math.sqrt(
        Math.pow(object.velocity.magnitude * object.velocity.direction.q + acceleration.q, 2) +
        Math.pow(object.velocity.magnitude * object.velocity.direction.r + acceleration.r, 2)
      ),
      direction: Dict[str, Any]
    }
    return true
  }
  private updatePhysicsObjects(): void {
    for (const object of this.physicsObjects.values()) {
      if (object.velocity.magnitude > 0) {
        const newPosition = {
          q: object.position.q + object.velocity.direction.q * object.velocity.magnitude,
          r: object.position.r + object.velocity.direction.r * object.velocity.magnitude
        }
        const collisions = this.checkCollisions(object, newPosition)
        if (collisions.length === 0) {
          object.position = newPosition
        } else {
          this.handleCollisions(object, collisions)
        }
        object.velocity.magnitude *= (1 - object.physics.friction)
        if (object.velocity.magnitude < 0.01) {
          object.velocity.magnitude = 0
        }
      }
      if (object.physics.isRotatable && object.angularVelocity !== 0) {
        object.angularVelocity *= (1 - object.physics.friction)
        if (Math.abs(object.angularVelocity) < 0.01) {
          object.angularVelocity = 0
        }
      }
    }
  }
  private checkCollisions(object: \'PhysicsObject\', newPosition: Dict[str, Any]): PhysicsObject[] {
    const collisions: List[PhysicsObject] = []
    const radius = 1 
    for (const other of this.physicsObjects.values()) {
      if (other.id !== object.id) {
        const distance = this.grid.getDistance(
          newPosition.q,
          newPosition.r,
          other.position.q,
          other.position.r
        )
        if (distance < radius) {
          collisions.push(other)
        }
      }
    }
    return collisions
  }
  private handleCollisions(object: \'PhysicsObject\', collisions: List[PhysicsObject]): void {
    for (const other of collisions) {
      const relativeVelocity = {
        q: object.velocity.direction.q * object.velocity.magnitude - 
           (other.velocity?.direction.q || 0) * (other.velocity?.magnitude || 0),
        r: object.velocity.direction.r * object.velocity.magnitude - 
           (other.velocity?.direction.r || 0) * (other.velocity?.magnitude || 0)
      }
      const restitution = Math.min(object.physics.restitution, other.physics.restitution || 0)
      if (other.physics.isMovable) {
        const totalMass = object.physics.mass + other.physics.mass
        const impulse = {
          q: (-(1 + restitution) * relativeVelocity.q * object.physics.mass) / totalMass,
          r: (-(1 + restitution) * relativeVelocity.r * object.physics.mass) / totalMass
        }
        object.velocity = {
          magnitude: Math.sqrt(Math.pow(impulse.q, 2) + Math.pow(impulse.r, 2)),
          direction: Dict[str, Any]
        }
        if (other.velocity) {
          const otherImpulse = {
            q: -impulse.q * (object.physics.mass / other.physics.mass),
            r: -impulse.r * (object.physics.mass / other.physics.mass)
          }
          other.velocity = {
            magnitude: Math.sqrt(Math.pow(otherImpulse.q, 2) + Math.pow(otherImpulse.r, 2)),
            direction: Dict[str, Any]
          }
        }
      } else {
        object.velocity = {
          magnitude: object.velocity.magnitude * restitution,
          direction: Dict[str, Any]
        }
      }
    }
  }
  applyPhysicsAttack(source: CombatParticipant, target: \'PhysicsObject\', force: float): bool {
    const direction = {
      q: target.position.q - source.position.q,
      r: target.position.r - source.position.r
    }
    const magnitude = Math.sqrt(direction.q * direction.q + direction.r * direction.r)
    if (magnitude === 0) return false
    const normalizedDirection = {
      q: direction.q / magnitude,
      r: direction.r / magnitude
    }
    const attackForce: \'ForceVector\' = {
      magnitude: force * source.calculateDamage(),
      direction: normalizedDirection
    }
    return this.applyForce(target.id, attackForce)
  }
  applyTorque(objectId: str, torque: float): bool {
    const object = this.physicsObjects.get(objectId)
    if (!object || !object.physics.isRotatable) return false
    const angularAcceleration = torque / (object.physics.mass * 0.5) 
    object.angularVelocity += angularAcceleration
    return true
  }
  private applyEnvironmentalPhysics(): void {
    for (const object of this.physicsObjects.values()) {
      const effects = this.getEnvironmentalEffectsAtPosition(object.position)
      for (const effect of effects) {
        switch (effect.type) {
          case 'wind':
            const windForce: \'ForceVector\' = {
              magnitude: effect.magnitude * 2, 
              direction: Dict[str, Any] 
            }
            this.applyForce(object.id, windForce)
            break
          case 'burning':
            if (object.physics.mass > 0.1) { 
              object.physics.mass *= (1 - effect.magnitude * 0.1)
            }
            break
          case 'flooded':
            object.physics.friction = Math.min(1, object.physics.friction + effect.magnitude * 0.2)
            break
        }
      }
    }
  }
  processTurn(): void {
    this.applyEnvironmentalPhysics()
    this.updatePhysicsObjects()
    for (const [id, hazard] of this.hazards) {
      if (hazard.ticksRemaining > 0) {
        this.processHazardEffects(hazard)
        hazard.ticksRemaining--
      } else {
        this.hazards.delete(id)
      }
    }
    for (const [effect, intensity] of this.weatherEffects) {
      this.processWeatherEffects(effect, intensity)
    }
  }
  private processHazardEffects(hazard: EnvironmentalHazard): void {
    const affectedCells = this.grid.getNeighborsInRange(
      hazard.position.q,
      hazard.position.r,
      hazard.radius
    )
    for (const cell of affectedCells) {
      for (const effect of hazard.effects) {
        this.applyCellEffect(cell, effect)
      }
    }
  }
  private processWeatherEffects(effect: str, intensity: float): void {
    for (let q = 0; q < this.grid.width; q++) {
      for (let r = 0; r < this.grid.height; r++) {
        const cell = this.grid.get(q, r)
        if (cell) {
          switch (effect) {
            case 'rain':
              if (cell.terrainEffect === 'burning') {
                cell.terrainEffect = ''
              }
              cell.movementCost = Math.min(99, cell.movementCost + intensity * 0.5)
              break
            case 'wind':
              if (cell.cover > 0) {
                cell.cover = Math.max(0, cell.cover - intensity * 0.1)
              }
              break
            case 'fog':
              cell.visibility = Math.max(0, 1 - intensity)
              break
          }
        }
      }
    }
  }
  getInteractiveObjectsInRange(position: Dict[str, Any], range: float): InteractiveObject[] {
    const objects: List[InteractiveObject] = []
    for (const object of this.interactiveObjects.values()) {
      const distance = this.grid.getDistance(position.q, position.r, object.position.q, object.position.r)
      if (distance <= range) {
        objects.push(object)
      }
    }
    return objects
  }
  getEnvironmentalEffectsAtPosition(position: Dict[str, Any]): Array<{ type: str; magnitude: float }> {
    const effects: Array<{ type: str; magnitude: float }> = []
    const cell = this.grid.get(position.q, position.r)
    if (cell) {
      if (cell.terrainEffect) {
        effects.push({
          type: cell.terrainEffect,
          magnitude: this.getTerrainEffectMagnitude(cell.terrainEffect)
        })
      }
      for (const hazard of this.hazards.values()) {
        const distance = this.grid.getDistance(position.q, position.r, hazard.position.q, hazard.position.r)
        if (distance <= hazard.radius) {
          effects.push(...hazard.effects)
        }
      }
      for (const [effect, intensity] of this.weatherEffects) {
        effects.push({ type: effect, magnitude: intensity })
      }
    }
    return effects
  }
  private getTerrainEffectMagnitude(effect: str): float {
    switch (effect) {
      case 'burning': return 0.3
      case 'flooded': return 0.4
      case 'rubble': return 0.2
      default: return 0.1
    }
  }
  private handlePhysicsObjectDestruction(object: PhysicsObject): void {
    const explosionRadius = 2
    const explosionForce = 10
    for (const other of this.physicsObjects.values()) {
      if (other.id !== object.id) {
        const distance = this.grid.getDistance(
          object.position.q,
          object.position.r,
          other.position.q,
          other.position.r
        )
        if (distance <= explosionRadius) {
          const forceMagnitude = explosionForce * (1 - distance / explosionRadius)
          const direction = {
            q: other.position.q - object.position.q,
            r: other.position.r - object.position.r
          }
          const mag = Math.sqrt(direction.q * direction.q + direction.r * direction.r)
          if (mag > 0) {
            const force: \'ForceVector\' = {
              magnitude: forceMagnitude,
              direction: Dict[str, Any]
            }
            this.applyForce(other.id, force)
          }
        }
      }
    }
    this.physicsObjects.delete(object.id)
    this.interactiveObjects.delete(object.id)
  }
} 