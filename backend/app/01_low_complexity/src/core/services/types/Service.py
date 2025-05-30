from typing import Any



interface ServiceResponse<T> {
  success: bool
  data?: T
  error?: str
  metadata?: Record<string, unknown>
} 