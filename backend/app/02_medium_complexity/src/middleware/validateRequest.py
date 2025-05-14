from typing import Any, List



const logger = new Logger({ prefix: 'Validation' })
/**
 * Interface for validation targets in the request
 */
class ValidationTarget:
    body?: bool
    query?: bool
    params?: bool
/**
 * Creates a middleware function that validates request data against a Zod schema
 * @param schema The Zod schema to validate against
 * @param targets Which parts of the request to validate (default: body only)
 */
const validateRequest = (
  schema: AnyZodObject,
  targets: \'ValidationTarget\' = { body: true }
) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const dataToValidate: Record<string, unknown> = {}
      if (targets.body) dataToValidate.body = req.body
      if (targets.query) dataToValidate.query = req.query
      if (targets.params) dataToValidate.params = req.params
      const validatedData = await schema.parseAsync(dataToValidate)
      if (targets.body) req.body = validatedData.body
      if (targets.query) req.query = validatedData.query
      if (targets.params) req.params = validatedData.params
      next()
    } catch (error) {
      if (error instanceof ZodError) {
        const formattedErrors: List[FormattedValidationError] = error.errors.map(err => ({
          path: err.path.join('.'),
          message: err.message,
        }))
        logger.warn('Validation failed:', error.errors)
        next(new ValidationError('Validation failed', formattedErrors))
      } else {
        next(error)
      }
    }
  }
}