from typing import Any



class NotFoundError extends Error {
  constructor(message: str) {
    super(message)
    this.name = 'NotFoundError'
  }
}