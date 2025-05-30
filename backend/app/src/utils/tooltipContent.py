from typing import Any, Dict, Union


class TooltipContent:
    [key: Union[str]: Omit<InfoTooltipProps, 'placement', 'iconSize', 'inline'>]
const stepTooltips: \'TooltipContent\' = {
  race: Dict[str, Any],
  class: Dict[str, Any],
  background: Dict[str, Any],
}
const abilityScoreTooltips: \'TooltipContent\' = {
  strength: Dict[str, Any],
  dexterity: Dict[str, Any],
  constitution: Dict[str, Any],
  intelligence: Dict[str, Any],
  wisdom: Dict[str, Any],
  charisma: Dict[str, Any],
}
const pointBuyTooltip: InfoTooltipProps = {
  title: 'Point Buy System',
  type: 'help',
  description: 'Customize your ability scores using a pool of 27 points.',
  rules: [
    'Scores must be between 8 and 15 before racial modifiers',
    'Scores 8-13: Cost 1 point per increase',
    'Scores 14-15: Cost 2 points per increase',
    'You must spend exactly 27 points',
  ],
  examples: [
    'Standard Array (27 points): 15, 14, 13, 12, 10, 8',
    'Balanced Build (27 points): 13, 13, 13, 12, 12, 12',
    'Specialized (27 points): 15, 15, 13, 10, 8, 8',
  ],
}
const equipmentTooltips: \'TooltipContent\' = {
  armor: Dict[str, Any],
  weapons: Dict[str, Any],
  equipment: Dict[str, Any],
}
const skillTooltips: \'TooltipContent\' = {
  proficiencies: Dict[str, Any],
  expertise: Dict[str, Any],
}
const getTooltipContent = (
  key: str,
  category: 'step' | 'ability' | 'equipment' | 'skill' = 'step'
): Omit<InfoTooltipProps, 'placement' | 'iconSize' | 'inline'> => {
  switch (category) {
    case 'ability':
      return abilityScoreTooltips[key] || stepTooltips.default
    case 'equipment':
      return equipmentTooltips[key] || stepTooltips.default
    case 'skill':
      return skillTooltips[key] || stepTooltips.default
    default:
      return stepTooltips[key] || stepTooltips.default
  }
}