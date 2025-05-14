from typing import Any


describe('StorageError', () => {
  it('should create error with code and message', () => {
    const error = new StorageError(
      StorageErrorCode.NOT_FOUND,
      'File not found'
    )
    expect(error).toBeInstanceOf(Error)
    expect(error).toBeInstanceOf(StorageError)
    expect(error.name).toBe('StorageError')
    expect(error.code).toBe(StorageErrorCode.NOT_FOUND)
    expect(error.message).toBe('File not found')
    expect(error.details).toBeUndefined()
  })
  it('should create error with optional details', () => {
    const details = { path: '/test/file.txt', attempt: 3 }
    const error = new StorageError(
      StorageErrorCode.NETWORK_ERROR,
      'Failed to upload file',
      details
    )
    expect(error.code).toBe(StorageErrorCode.NETWORK_ERROR)
    expect(error.message).toBe('Failed to upload file')
    expect(error.details).toEqual(details)
  })
  it('should preserve stack trace', () => {
    const error = new StorageError(
      StorageErrorCode.PERMISSION_DENIED,
      'Access denied'
    )
    expect(error.stack).toBeDefined()
    expect(error.stack).toContain('StorageError')
  })
  it('should work with all error codes', () => {
    Object.values(StorageErrorCode).forEach(code => {
      const error = new StorageError(code, `Error with code ${code}`)
      expect(error.code).toBe(code)
    })
  })
}) 