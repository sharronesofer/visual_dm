from typing import Any, List


/**
 * Loads and validates quest templates from the templates directory.
 * Only templates that pass schema validation are exported.
 */
const SCHEMA_PATH = path.join(__dirname, 'schemas/quest_template.schema.json')
const TEMPLATES_PATH = path.join(__dirname, 'templates/sample_quest_templates.json')
const ajv = new Ajv({ allErrors: true })
const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf-8'))
const validate = ajv.compile(schema)
const templatesRaw = JSON.parse(fs.readFileSync(TEMPLATES_PATH, 'utf-8'))
const questTemplates: List[QuestTemplate] = templatesRaw.filter((template: Any) => {
  const valid = validate(template)
  if (!valid) {
    console.error(`Invalid quest template: ${template.id}`, validate.errors)
    return false
  }
  return true
})
/**
 * Get all valid quest templates.
 */
function getQuestTemplates(): QuestTemplate[] {
  return questTemplates
} 