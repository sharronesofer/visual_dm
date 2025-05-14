import { InfoTooltipProps } from '../components/InfoTooltip';

interface TooltipContent {
  [key: string]: Omit<InfoTooltipProps, 'placement' | 'iconSize' | 'inline'>;
}

// Character Creation Step Tooltips
export const stepTooltips: TooltipContent = {
  race: {
    title: 'Race Selection',
    type: 'help',
    description:
      "Choose your character's race, which determines various racial traits and bonuses.",
    rules: [
      'Each race provides specific ability score increases',
      'Races have unique features like darkvision or resistances',
      'Your race choice may affect your size and movement speed',
    ],
  },
  class: {
    title: 'Class Selection',
    type: 'help',
    description: "Select your character's class, which defines their primary abilities and role.",
    rules: [
      'Classes determine hit points, proficiencies, and special abilities',
      'Some classes have specific ability score requirements',
      'Your class affects available equipment options',
    ],
  },
  background: {
    title: 'Background Selection',
    type: 'help',
    description: "Choose your character's background, representing their life before adventuring.",
    rules: [
      'Backgrounds provide skill proficiencies',
      'Each background grants specific tool proficiencies or languages',
      'Backgrounds include personality traits, ideals, bonds, and flaws',
    ],
  },
};

// Ability Score Tooltips
export const abilityScoreTooltips: TooltipContent = {
  strength: {
    title: 'Strength',
    type: 'info',
    description: 'Measures physical power and carrying capacity.',
    rules: [
      'Affects melee attack and damage rolls',
      'Determines carrying capacity and lift/push/drag limits',
      'Used for Athletics skill checks',
    ],
    examples: ['Breaking down doors', 'Lifting heavy objects', 'Wrestling and climbing'],
  },
  dexterity: {
    title: 'Dexterity',
    type: 'info',
    description: 'Represents agility, reflexes, and balance.',
    rules: [
      'Affects Armor Class for light armor',
      'Used for ranged attack rolls',
      'Determines Initiative bonus',
    ],
    examples: ['Dodging attacks', 'Walking on narrow ledges', 'Picking locks'],
  },
  constitution: {
    title: 'Constitution',
    type: 'info',
    description: 'Represents health, stamina, and vital force.',
    rules: [
      'Affects hit points gained at each level',
      'Used for concentration checks when spellcasting',
      'Determines resistance to disease and poison',
    ],
    examples: ['Resisting poison', 'Running long distances', 'Surviving harsh conditions'],
  },
  intelligence: {
    title: 'Intelligence',
    type: 'info',
    description: 'Measures reasoning and memory.',
    rules: [
      'Primary ability for Wizards',
      'Affects number of languages known',
      'Used for Investigation and knowledge skills',
    ],
    examples: ['Solving puzzles', 'Recalling lore', 'Understanding ancient writings'],
  },
  wisdom: {
    title: 'Wisdom',
    type: 'info',
    description: 'Represents perception and insight.',
    rules: [
      'Primary ability for Clerics and Druids',
      'Used for Perception checks',
      'Affects survival and insight abilities',
    ],
    examples: [
      'Spotting hidden objects',
      "Reading someone's intentions",
      'Tracking in the wilderness',
    ],
  },
  charisma: {
    title: 'Charisma',
    type: 'info',
    description: 'Measures force of personality.',
    rules: [
      'Primary ability for Sorcerers, Warlocks, and Bards',
      'Used for social interaction skills',
      'Affects ability to influence others',
    ],
    examples: ['Negotiating with NPCs', 'Performing for an audience', 'Leading a group'],
  },
};

// Point Buy System Tooltip
export const pointBuyTooltip: InfoTooltipProps = {
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
};

// Equipment Tooltips
export const equipmentTooltips: TooltipContent = {
  armor: {
    title: 'Armor',
    type: 'info',
    description: 'Protective gear that improves your Armor Class (AC).',
    rules: [
      'Light Armor: Adds Dexterity modifier to AC',
      'Medium Armor: Adds limited Dexterity bonus',
      'Heavy Armor: Fixed AC value, no Dexterity bonus',
    ],
  },
  weapons: {
    title: 'Weapons',
    type: 'info',
    description: 'Tools for combat, each with unique properties.',
    rules: [
      'Simple weapons are available to all classes',
      'Martial weapons require specific proficiencies',
      'Ranged weapons use Dexterity for attack rolls',
    ],
  },
  equipment: {
    title: 'Adventuring Gear',
    type: 'info',
    description: 'Essential items for exploration and survival.',
    rules: [
      'Some items are required for class abilities',
      'Consider weight limits when selecting gear',
      'Pack contents can be customized',
    ],
  },
};

// Skill Selection Tooltips
export const skillTooltips: TooltipContent = {
  proficiencies: {
    title: 'Skill Proficiencies',
    type: 'help',
    description: "Skills you're trained in, granting a bonus to related ability checks.",
    rules: [
      'Proficiency bonus is added to skill checks',
      'Number of proficiencies based on class and background',
      'Some classes grant expertise (double proficiency)',
    ],
  },
  expertise: {
    title: 'Expertise',
    type: 'info',
    description: 'Double your proficiency bonus for selected skills.',
    rules: [
      'Must be proficient in the skill first',
      'Limited to certain classes (like Rogue and Bard)',
      'Represents exceptional training or natural talent',
    ],
  },
};

// Helper function to get tooltip content
export const getTooltipContent = (
  key: string,
  category: 'step' | 'ability' | 'equipment' | 'skill' = 'step'
): Omit<InfoTooltipProps, 'placement' | 'iconSize' | 'inline'> => {
  switch (category) {
    case 'ability':
      return abilityScoreTooltips[key] || stepTooltips.default;
    case 'equipment':
      return equipmentTooltips[key] || stepTooltips.default;
    case 'skill':
      return skillTooltips[key] || stepTooltips.default;
    default:
      return stepTooltips[key] || stepTooltips.default;
  }
};
