from typing import Any, Dict


describe('Region type validation', () => {
  it('should validate a correct region object', () => {
    expect(isRegion(sampleRegion)).toBe(true)
  })
  it('should reject an invalid region object', () => {
    const invalidRegion = {
      id: 123, 
      name: 'Test Region',
      boundaries: 'not-an-array', 
      properties: Dict[str, Any],
    }
    expect(isRegion(invalidRegion)).toBe(false)
  })
})