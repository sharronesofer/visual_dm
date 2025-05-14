from typing import Any



describe('HTTP Utilities Integration Tests', () => {
  let mock: MockAdapter
  beforeEach(() => {
    mock = new MockAdapter(axios)
    localStorage.clear()
    jest.useFakeTimers()
  })
  afterEach(() => {
    mock.restore()
    jest.useRealTimers()
  })
  describe('Authentication', () => {
    it('should add auth token to requests when available', async () => {
      const token = 'test-token'
      localStorage.setItem('authToken', token)
      mock.onGet('/test').reply(config => {
        expect(config.headers?.Authorization).toBe(`Bearer ${token}`)
        return [200, { data: 'success' }]
      })
      await httpClient.get('/test')
    })
    it('should handle 401 unauthorized responses', async () => {
      mock.onGet('/test').reply(401, { message: 'Unauthorized' })
      await expect(httpClient.get('/test')).rejects.toThrow(ApiError)
    })
  })
  describe('Request Cancellation', () => {
    it('should cancel requests using cancellation token', async () => {
      const cancelToken = createCancellationToken()
      mock.onGet('/test').reply(() => {
        return new Promise(() => {}) 
      })
      const promise = httpClient.get('/test', {
        cancelToken: cancelToken.token,
      })
      cancelToken.cancel('Request cancelled by user')
      await expect(promise).rejects.toThrow('Request cancelled by user')
    })
    it('should cancel multiple requests with same token', async () => {
      const cancelToken = createCancellationToken()
      mock.onGet('/test1').reply(() => new Promise(() => {}))
      mock.onGet('/test2').reply(() => new Promise(() => {}))
      const promise1 = httpClient.get('/test1', {
        cancelToken: cancelToken.token,
      })
      const promise2 = httpClient.get('/test2', {
        cancelToken: cancelToken.token,
      })
      cancelToken.cancel('Cancelled all requests')
      await expect(promise1).rejects.toThrow('Cancelled all requests')
      await expect(promise2).rejects.toThrow('Cancelled all requests')
    })
  })
  describe('Timeout Handling', () => {
    it('should timeout requests after specified duration', async () => {
      const client = createHttpClient({ timeout: 1000 })
      mock.onGet('/test').reply(() => {
        return new Promise(() => {}) 
      })
      const promise = client.get('/test')
      jest.advanceTimersByTime(2000)
      await expect(promise).rejects.toThrow(TimeoutError)
    })
    it('should override default timeout in request config', async () => {
      mock.onGet('/test').reply(() => {
        return new Promise(() => {}) 
      })
      const promise = httpClient.get('/test', { timeout: 500 })
      jest.advanceTimersByTime(1000)
      await expect(promise).rejects.toThrow(TimeoutError)
    })
  })
  describe('Retry Logic', () => {
    it('should retry failed requests with exponential backoff', async () => {
      const attempts = jest.fn()
      mock
        .onGet('/test')
        .replyOnce(
          503,
          { message: 'Service Unavailable' },
          { 'Retry-After': '1' }
        )
        .replyOnce(
          503,
          { message: 'Service Unavailable' },
          { 'Retry-After': '1' }
        )
        .reply(200, { data: 'success' })
      const promise = httpClient.get('/test')
      jest.advanceTimersByTime(1000)
      jest.advanceTimersByTime(2000)
      jest.advanceTimersByTime(4000)
      const result = await promise
      expect(result).toEqual({ data: 'success' })
      expect(mock.history.get.length).toBe(3)
    })
    it('should stop retrying after max attempts', async () => {
      mock.onGet('/test').reply(503, { message: 'Service Unavailable' })
      const promise = httpClient.get('/test')
      for (let i = 0; i < 4; i++) {
        jest.advanceTimersByTime(Math.pow(2, i) * 1000)
      }
      await expect(promise).rejects.toThrow(ApiError)
      expect(mock.history.get.length).toBe(4) 
    })
    it('should not retry on non-retryable status codes', async () => {
      mock.onGet('/test').reply(400, { message: 'Bad Request' })
      await expect(httpClient.get('/test')).rejects.toThrow(ApiError)
      expect(mock.history.get.length).toBe(1) 
    })
  })
  describe('Concurrent Requests', () => {
    it('should handle multiple concurrent requests', async () => {
      mock.onGet('/test1').reply(200, { data: 'test1' })
      mock.onGet('/test2').reply(200, { data: 'test2' })
      mock.onGet('/test3').reply(200, { data: 'test3' })
      const results = await Promise.all([
        httpClient.get('/test1'),
        httpClient.get('/test2'),
        httpClient.get('/test3'),
      ])
      expect(results).toEqual([
        { data: 'test1' },
        { data: 'test2' },
        { data: 'test3' },
      ])
    })
    it('should handle mixed success/failure concurrent requests', async () => {
      mock.onGet('/success').reply(200, { data: 'success' })
      mock.onGet('/error').reply(500, { message: 'Server Error' })
      mock.onGet('/timeout').reply(() => new Promise(() => {}))
      const successPromise = httpClient.get('/success')
      const errorPromise = httpClient.get('/error')
      const timeoutPromise = httpClient.get('/timeout', { timeout: 1000 })
      jest.advanceTimersByTime(2000)
      const results = await Promise.allSettled([
        successPromise,
        errorPromise,
        timeoutPromise,
      ])
      expect(results[0].status).toBe('fulfilled')
      expect(results[1].status).toBe('rejected')
      expect(results[2].status).toBe('rejected')
    })
  })
  describe('Request/Response Metadata', () => {
    it('should include request ID in headers', async () => {
      mock.onGet('/test').reply(config => {
        expect(config.headers?.['X-Request-ID']).toMatch(/^req_\d+_[a-z0-9]+$/)
        return [200, { data: 'success' }]
      })
      await httpClient.get('/test')
    })
    it('should include metadata in response', async () => {
      const requestId = 'test-request-id'
      mock.onGet('/test').reply(config => {
        return [200, { data: 'success' }, { 'X-Request-ID': requestId }]
      })
      const response = await httpClient.get('/test')
      expect(response._metadata).toBeDefined()
      expect(response._metadata.statusCode).toBe(200)
      expect(response._metadata.timestamp).toBeDefined()
      expect(
        new Date(response._metadata.timestamp).getTime()
      ).toBeLessThanOrEqual(Date.now())
    })
  })
  describe('Network Errors', () => {
    it('should handle network errors', async () => {
      mock.onGet('/test').networkError()
      await expect(httpClient.get('/test')).rejects.toThrow(NetworkError)
    })
    it('should handle timeout errors', async () => {
      mock.onGet('/test').timeout()
      await expect(httpClient.get('/test')).rejects.toThrow(TimeoutError)
    })
    it('should handle connection errors', async () => {
      mock.onGet('/test').networkError()
      await expect(httpClient.get('/test')).rejects.toThrow(NetworkError)
    })
  })
  describe('HTTP Methods', () => {
    const testData = { test: true }
    const successResponse = { data: 'success' }
    it('should make POST request with data', async () => {
      mock.onPost('/test', testData).reply(201, successResponse)
      const result = await httpClient.post('/test', testData)
      expect(result).toEqual(successResponse)
      expect(mock.history.post[0].data).toBe(JSON.stringify(testData))
    })
    it('should make PUT request with data', async () => {
      mock.onPut('/test', testData).reply(200, successResponse)
      const result = await httpClient.put('/test', testData)
      expect(result).toEqual(successResponse)
      expect(mock.history.put[0].data).toBe(JSON.stringify(testData))
    })
    it('should make PATCH request with data', async () => {
      mock.onPatch('/test', testData).reply(200, successResponse)
      const result = await httpClient.patch('/test', testData)
      expect(result).toEqual(successResponse)
      expect(mock.history.patch[0].data).toBe(JSON.stringify(testData))
    })
    it('should make DELETE request', async () => {
      mock.onDelete('/test').reply(204)
      await httpClient.delete('/test')
      expect(mock.history.delete.length).toBe(1)
    })
    it('should make HEAD request', async () => {
      mock.onHead('/test').reply(200)
      await httpClient.head('/test')
      expect(mock.history.head.length).toBe(1)
    })
    it('should make OPTIONS request', async () => {
      mock.onOptions('/test').reply(200, {
        allow: ['GET', 'POST', 'PUT', 'DELETE'],
      })
      const result = await httpClient.options('/test')
      expect(result.allow).toEqual(['GET', 'POST', 'PUT', 'DELETE'])
    })
  })
})