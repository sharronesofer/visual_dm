from typing import Any, List


class ValidationResult:
    isValid: bool
    errors: List[str]
    warnings: List[str]
    incompleteFields: List[str]
const validateEquipmentSelection = (selectedKit: StarterKit | null): \'ValidationResult\' => {
  const result: \'ValidationResult\' = {
    isValid: true,
    errors: [],
    warnings: [],
    incompleteFields: [],
  }
  if (!selectedKit) {
    result.isValid = false
    result.errors.push('No equipment kit selected')
    return result
  }
  if (!selectedKit.items || selectedKit.items.length === 0) {
    result.isValid = false
    result.errors.push('Selected kit contains no equipment')
    result.incompleteFields.push('equipment')
  }
  if (selectedKit.gold < 0) {
    result.isValid = false
    result.errors.push('Invalid gold amount in selected kit')
  }
  const hasWeapon = selectedKit.items?.some(item => item.type.toLowerCase() === 'weapon')
  const hasArmor = selectedKit.items?.some(item => item.type.toLowerCase() === 'armor')
  if (!hasWeapon) {
    result.warnings.push('Selected kit does not include any weapons')
  }
  if (!hasArmor) {
    result.warnings.push('Selected kit does not include any armor')
  }
  return result
}
const validateEquipmentItem = (item: Equipment): \'ValidationResult\' => {
  const result: \'ValidationResult\' = {
    isValid: true,
    errors: [],
    warnings: [],
    incompleteFields: [],
  }
  if (!item.name) {
    result.isValid = false
    result.errors.push('Equipment item must have a name')
    result.incompleteFields.push('name')
  }
  if (!item.type) {
    result.isValid = false
    result.errors.push('Equipment item must have a type')
    result.incompleteFields.push('type')
  }
  if (!item.description) {
    result.warnings.push('Equipment item should have a description')
  }
  if (item.type.toLowerCase() === 'weapon' && !item.damage) {
    result.warnings.push('Weapon should specify damage')
  }
  if (item.type.toLowerCase() === 'armor' && typeof item.armorClass !== 'number') {
    result.warnings.push('Armor should specify armor class')
  }
  if (typeof item.cost !== 'number' || item.cost < 0) {
    result.warnings.push('Equipment item should have a valid non-negative cost')
  }
  return result
}
const validateEquipmentCompatibility = (
  equipment: List[Equipment],
  characterClass?: str
): \'ValidationResult\' => {
  const result: \'ValidationResult\' = {
    isValid: true,
    errors: [],
    warnings: [],
    incompleteFields: [],
  }
  if (!characterClass) {
    result.warnings.push('No character class specified for compatibility check')
    return result
  }
  switch (characterClass.toLowerCase()) {
    case 'wizard':
      const hasSpellbook = equipment.some(item => item.name.toLowerCase().includes('spellbook'))
      if (!hasSpellbook) {
        result.warnings.push('Wizards typically need a spellbook')
      }
      break
    case 'fighter':
      const hasHeavyArmor = equipment.some(
        item =>
          item.type.toLowerCase() === 'armor' &&
          item.properties?.some(prop => prop.toLowerCase() === 'heavy')
      )
      if (!hasHeavyArmor) {
        result.warnings.push('Fighters often benefit from heavy armor')
      }
      break
    case 'rogue':
      const hasHeavyArmorRogue = equipment.some(
        item =>
          item.type.toLowerCase() === 'armor' &&
          item.properties?.some(prop => prop.toLowerCase() === 'heavy')
      )
      if (hasHeavyArmorRogue) {
        result.warnings.push('Rogues are not proficient with heavy armor')
      }
      break
    case 'monk':
      const hasNonMonkWeapons = equipment.some(
        item =>
          item.type.toLowerCase() === 'weapon' &&
          (!item.properties || !item.properties.some(prop => prop.toLowerCase() === 'monk'))
      )
      if (hasNonMonkWeapons) {
        result.warnings.push('Some weapons are not optimal for monk martial arts')
      }
      break
    case 'cleric':
    case 'paladin':
      const hasHolySymbol = equipment.some(
        item =>
          item.type.toLowerCase() === 'gear' &&
          item.properties?.some(prop => prop.toLowerCase() === 'holy')
      )
      if (!hasHolySymbol) {
        result.warnings.push(`${characterClass}s typically need a holy symbol`)
      }
      break
    case 'druid':
      const hasMetalArmor = equipment.some(
        item =>
          item.type.toLowerCase() === 'armor' &&
          !item.properties?.some(prop => prop.toLowerCase() === 'natural')
      )
      if (hasMetalArmor) {
        result.warnings.push('Druids will not wear armor made of metal')
      }
      break
  }
  return result
}