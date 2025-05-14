from typing import Any, Dict


const mockInstance = {
  getBackgrounds: jest.fn().mockResolvedValue([
    {
      name: 'Acolyte',
      feature: Dict[str, Any],
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
    attributes: Dict[str, Any],
    selectedSkills: [],
    skillPoints: 4,
    background: '',
    toolProficiencies: [],
    languagesKnown: 0,
  }),
}
default mockInstance