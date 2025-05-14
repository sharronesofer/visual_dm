from typing import Any, Dict


  SchemaValidator,
  NarrativeConsistencyValidator,
  DifficultyScalingValidator,
  ComprehensivePOIValidator,
  ValidationResult,
} from '../poiValidation'
describe('POI Validation Framework', () => {
  const basePOI: POI = {
    id: '1',
    name: 'Test POI',
    type: 'dungeon',
    size: 'small',
    theme: 'medieval',
    description: 'A test POI',
    layout: Dict[str, Any],
          width: 2,
          height: 2,
          properties: {},
        },
      ],
      connections: [],
    },
    position: Dict[str, Any],
    chunks: {},
    activeChunks: [],
    isActive: true,
    properties: Dict[str, Any],
  }
  it('SchemaValidator detects missing fields', () => {
    const poi = {
      ...basePOI,
      id: '',
      layout: Dict[str, Any],
    }
    const result = new SchemaValidator().validate(poi as POI)
    expect(result.errors.some(e => e.code === 'missing_id')).toBe(true)
    expect(result.errors.some(e => e.code === 'missing_layout')).toBe(true)
    expect(result.isValid()).toBe(false)
  })
  it('NarrativeConsistencyValidator detects empty and duplicate descriptions', () => {
    const validator = new NarrativeConsistencyValidator()
    const emptyPOI = { ...basePOI, description: '' }
    let result = validator.validate(emptyPOI)
    expect(result.warnings.some(w => w.code === 'empty_description')).toBe(
      true
    )
    const descPOI = { ...basePOI, description: 'desc1' }
    validator.validate(descPOI)
    result = validator.validate({ ...basePOI, description: 'desc1' })
    expect(result.warnings.some(w => w.code === 'duplicate_description')).toBe(
      true
    )
  })
  it('DifficultyScalingValidator detects difficulty out of range', () => {
    const validator = new DifficultyScalingValidator()
    const hardStarter = {
      ...basePOI,
      properties: Dict[str, Any],
    }
    let result = validator.validate(hardStarter)
    expect(result.errors.some(e => e.code === 'difficulty_too_high')).toBe(
      true
    )
    const easyEndgame = {
      ...basePOI,
      properties: Dict[str, Any],
    }
    result = validator.validate(easyEndgame)
    expect(result.warnings.some(w => w.code === 'difficulty_too_low')).toBe(
      true
    )
  })
  it('ComprehensivePOIValidator accumulates all errors and warnings', () => {
    const validator = new ComprehensivePOIValidator()
    const poi = {
      ...basePOI,
      id: '',
      description: '',
      layout: Dict[str, Any],
      properties: Dict[str, Any],
    }
    const result = validator.validate(poi as POI)
    expect(result.errors.length).toBeGreaterThan(0)
    expect(result.warnings.length).toBeGreaterThan(0)
    expect(result.isValid()).toBe(false)
  })
  it('Valid POI passes all validators', () => {
    const validator = new ComprehensivePOIValidator()
    const result = validator.validate(basePOI)
    expect(result.isValid()).toBe(true)
    expect(result.errors.length).toBe(0)
  })
})