from typing import Any, List


describe('QuestTemplate JSON Schema Validation', () => {
  const ajv = new Ajv({ allErrors: true })
  const schemaPath = path.join(__dirname, '../schemas/quest_template.schema.json')
  const templatesPath = path.join(__dirname, '../templates/sample_quest_templates.json')
  let schema: Any
  let templates: List[any]
  beforeAll(() => {
    schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'))
    templates = JSON.parse(fs.readFileSync(templatesPath, 'utf-8'))
  })
  it('should validate all sample quest templates against the schema', () => {
    const validate = ajv.compile(schema)
    for (const template of templates) {
      const valid = validate(template)
      if (!valid) {
        console.error(validate.errors)
      }
      expect(valid).toBe(true)
    }
  })
})
describe('QuestTemplate Loader', () => {
  it('should return only valid quest templates', () => {
    const validTemplates = getQuestTemplates()
    expect(Array.isArray(validTemplates)).toBe(true)
    expect(validTemplates.length).toBeGreaterThan(0)
    for (const tpl of validTemplates) {
      expect(typeof tpl.id).toBe('string')
      expect(typeof tpl.title).toBe('string')
    }
  })
}) 