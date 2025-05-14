from typing import Any



class ApiError:
    message: str
    code?: str
    status?: float
    details?: Any
interface ApiResponse<T = any> {
  data?: T
  error?: \'ApiError\'
  status: float
  headers?: Record<string, string>
} 