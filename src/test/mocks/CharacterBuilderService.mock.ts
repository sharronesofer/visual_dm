import { Background, Skill } from '../../types/character';

const mockInstance = {
  getBackgrounds: jest.fn().mockResolvedValue([
    {
      name: 'Acolyte',
      feature: {
        name: 'Shelter of the Faithful',
        description:
          'As an acolyte, you command the respect of those who share your faith.',
      },
      toolProficiencies: ['Incense burner', 'Prayer book'],
      languages: 2,
      skillProficiencies: ['Religion', 'Insight'],
    },
  ]),
  setBackground: jest.fn().mockResolvedValue(undefined),
  getSkills: jest.fn().mockResolvedValue([
    {
      name: 'Acrobatics',
      ability: 'Dexterity',
      trained: false,
      modifier: 0,
    },
    {
      name: 'Athletics',
      ability: 'Strength',
      trained: false,
      modifier: 0,
    },
  ]),
  setSkillProficiencies: jest.fn().mockResolvedValue(undefined),
  calculateAvailableSkillPoints: jest.fn().mockReturnValue(4),
  getState: jest.fn().mockReturnValue({
    class: '',
    attributes: {
      strength: 10,
      dexterity: 10,
      constitution: 10,
      intelligence: 10,
      wisdom: 10,
      charisma: 10,
    },
    selectedSkills: [],
    skillPoints: 4,
    background: '',
    toolProficiencies: [],
    languagesKnown: 0,
  }),
};

export default mockInstance;
