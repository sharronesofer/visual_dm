from typing import Any



class DatabaseError extends Error {
  constructor(message: str) {
    super(message)
    this.name = 'DatabaseError'
  }
}