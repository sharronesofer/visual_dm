from typing import Any, Dict


describe('Character Store', () => {
  beforeEach(() => {
    const { result } = renderHook(() => useCharacterStore())
    act(() => {
      result.current.resetCharacter()
    })
  })
  describe('Character Management', () => {
    it('should initialize a character with default values', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
      })
      expect(result.current.character).toEqual({
        id: expect.any(String),
        name: 'Test Character',
        selectedBackgrounds: [],
        maxBackgrounds: 2,
        skills: {},
        totalSkillPoints: 20,
      })
    })
    it('should update character name', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.setCharacterName('New Name')
      })
      expect(result.current.character?.name).toBe('New Name')
    })
    it('should update character description', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.setCharacterDescription('Test description')
      })
      expect(result.current.character?.description).toBe('Test description')
    })
  })
  describe('Background Management', () => {
    const testBackground: IBackground = {
      id: 'test-bg',
      name: 'Test Background',
      description: 'A test background',
      skillModifiers: Dict[str, Any],
    }
    it('should register a background', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.registerBackground(testBackground)
      })
      expect(result.current.backgrounds['test-bg']).toEqual(testBackground)
    })
    it('should add and remove backgrounds', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.registerBackground(testBackground)
        result.current.addBackground('test-bg')
      })
      expect(result.current.character?.selectedBackgrounds).toContain(
        'test-bg'
      )
      act(() => {
        result.current.removeBackground('test-bg')
      })
      expect(result.current.character?.selectedBackgrounds).not.toContain(
        'test-bg'
      )
    })
    it('should validate background limits', () => {
      const { result } = renderHook(() => useCharacterStore())
      const secondBackground: IBackground = {
        id: 'test-bg-2',
        name: 'Second Background',
        description: 'Another test background',
        skillModifiers: {},
      }
      const thirdBackground: IBackground = {
        id: 'test-bg-3',
        name: 'Third Background',
        description: 'One too many',
        skillModifiers: {},
      }
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.registerBackground(testBackground)
        result.current.registerBackground(secondBackground)
        result.current.registerBackground(thirdBackground)
        result.current.addBackground('test-bg')
        result.current.addBackground('test-bg-2')
      })
      expect(result.current.character?.selectedBackgrounds.length).toBe(2)
      expect(result.current.validationErrors).toHaveLength(0)
      act(() => {
        result.current.addBackground('test-bg-3')
      })
      expect(result.current.character?.selectedBackgrounds.length).toBe(2)
      expect(result.current.validationErrors[0]?.type).toBe('BACKGROUND_LIMIT')
    })
  })
  describe('Skill Management', () => {
    const testSkill: ISkill = {
      id: 'test-skill',
      name: 'Test Skill',
      description: 'A test skill',
      points: 0,
      modifier: 0,
      maxPoints: 5,
      category: 'Test',
    }
    it('should register a skill', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.registerSkill(testSkill)
      })
      expect(result.current.skills['test-skill']).toEqual(testSkill)
    })
    it('should allocate skill points within limits', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.registerSkill(testSkill)
        result.current.allocateSkillPoints('test-skill', 3)
      })
      expect(result.current.character?.skills['test-skill']).toBe(3)
      expect(result.current.validationErrors).toHaveLength(0)
      act(() => {
        result.current.allocateSkillPoints('test-skill', 6)
      })
      expect(result.current.character?.skills['test-skill']).toBe(3)
      expect(result.current.validationErrors[0]?.type).toBe('SKILL_POINTS')
    })
  })
  describe('Skill Calculations', () => {
    const testSkill: ISkill = {
      id: 'test-skill',
      name: 'Test Skill',
      description: 'A test skill',
      points: 0,
      modifier: 0,
      maxPoints: 5,
      category: 'Test',
    }
    const testBackground: IBackground = {
      id: 'test-bg',
      name: 'Test Background',
      description: 'A test background',
      skillModifiers: Dict[str, Any],
    }
    it('should calculate final skill values with modifiers', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.registerSkill(testSkill)
        result.current.registerBackground(testBackground)
        result.current.allocateSkillPoints('test-skill', 3)
        result.current.addBackground('test-bg')
      })
      const calculatedSkills = result.current.calculatedSkills
      expect(calculatedSkills?.finalValues['test-skill']).toBe(5) 
      expect(calculatedSkills?.totalModifiers['test-skill']).toBe(2)
      expect(calculatedSkills?.remainingPoints).toBe(17) 
    })
  })
  describe('Validation', () => {
    it('should validate total skill points', () => {
      const { result } = renderHook(() => useCharacterStore())
      const skill1: ISkill = {
        id: 'skill-1',
        name: 'Skill 1',
        description: 'First test skill',
        points: 0,
        modifier: 0,
        maxPoints: 10,
        category: 'Test',
      }
      const skill2: ISkill = {
        id: 'skill-2',
        name: 'Skill 2',
        description: 'Second test skill',
        points: 0,
        modifier: 0,
        maxPoints: 10,
        category: 'Test',
      }
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.registerSkill(skill1)
        result.current.registerSkill(skill2)
        result.current.allocateSkillPoints('skill-1', 15)
      })
      expect(result.current.validationErrors[0]?.type).toBe('SKILL_POINTS')
      act(() => {
        result.current.allocateSkillPoints('skill-1', 10)
        result.current.allocateSkillPoints('skill-2', 9)
      })
      expect(result.current.validationErrors).toHaveLength(0)
    })
    it('should validate skill existence', () => {
      const { result } = renderHook(() => useCharacterStore())
      act(() => {
        result.current.initializeCharacter('Test Character')
        result.current.allocateSkillPoints('nonexistent-skill', 5)
      })
      expect(result.current.validationErrors[0]?.type).toBe('INVALID_SKILL')
    })
  })
})