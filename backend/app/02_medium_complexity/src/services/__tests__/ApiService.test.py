from typing import Any, Dict



  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
  AxiosHeaders,
} from 'axios'
class ExtendedAxiosRequestConfig:
    retryCount?: float
class RetryError:
    config: \'ExtendedAxiosRequestConfig\'
jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>
describe('ApiService', () => {
  let apiService: ApiService
  let axiosInstance: jest.Mocked<AxiosInstance>
  beforeEach(() => {
    jest.clearAllMocks()
    axiosInstance = {
      get: jest.fn(),
      post: jest.fn(),
      interceptors: Dict[str, Any],
        response: Dict[str, Any],
      },
    } as any
    mockedAxios.create.mockReturnValue(axiosInstance)
    apiService = ApiService.getInstance()
  })
  describe('HTTP Methods', () => {
    it('makes GET requests successfully', async () => {
      const mockData = { id: '1', name: 'Test' }
      const mockResponse = { data: mockData }
      axiosInstance.get.mockResolvedValueOnce(mockResponse)
      const response = await apiService.get('/test')
      expect(response.data).toEqual(mockData)
      expect(axiosInstance.get).toHaveBeenCalledWith('/test')
    })
    it('makes POST requests successfully', async () => {
      const mockData = { name: 'Test' }
      const mockResponse = { data: Dict[str, Any] }
      axiosInstance.post.mockResolvedValueOnce(mockResponse)
      const response = await apiService.post('/test', mockData)
      expect(response.data).toEqual(mockResponse.data)
      expect(axiosInstance.post).toHaveBeenCalledWith('/test', mockData)
    })
    it('handles errors properly', async () => {
      const mockError: AxiosError = {
        response: Dict[str, Any],
          status: 404,
          statusText: 'Not Found',
          headers: {},
          config: {} as ExtendedAxiosRequestConfig,
        },
        isAxiosError: true,
        name: 'AxiosError',
        message: 'Request failed with status code 404',
        config: {} as ExtendedAxiosRequestConfig,
        toJSON: () => ({}),
      }
      axiosInstance.get.mockRejectedValueOnce(mockError)
      const response = await apiService.get('/test')
      expect(response.error).toBeDefined()
      expect(response.error?.status).toBe(404)
      expect(response.error?.code).toBe('NOT_FOUND')
    })
  })
  describe('Authentication', () => {
    it('adds auth token to request headers if available', async () => {
      const mockToken = 'test-token'
      localStorage.setItem('authToken', mockToken)
      const requestInterceptor = (
        axiosInstance.interceptors.request.use as jest.Mock
      ).mock.calls[0][0]
      const config = await requestInterceptor({
        headers: new AxiosHeaders(),
      } as ExtendedAxiosRequestConfig)
      expect(config.headers.Authorization).toBe(`Bearer ${mockToken}`)
      localStorage.removeItem('authToken')
    })
    it('handles 401 errors by attempting token refresh', async () => {
      const mockError: AxiosError = {
        response: Dict[str, Any],
          status: 401,
          statusText: 'Unauthorized',
          headers: {},
          config: {} as ExtendedAxiosRequestConfig,
        },
        isAxiosError: true,
        name: 'AxiosError',
        message: 'Request failed with status code 401',
        config: {} as ExtendedAxiosRequestConfig,
        toJSON: () => ({}),
      }
      const responseErrorInterceptor = (
        axiosInstance.interceptors.response.use as jest.Mock
      ).mock.calls[0][1]
      try {
        await responseErrorInterceptor(mockError)
      } catch (err) {
        const error = err as AxiosError
        expect(error.response?.status).toBe(401)
      }
    })
  })
  describe('Retry Mechanism', () => {
    it('retries failed requests with exponential backoff', async () => {
      const mockError: \'RetryError\' = {
        response: Dict[str, Any],
          status: 500,
          statusText: 'Internal Server Error',
          headers: {},
          config: {} as ExtendedAxiosRequestConfig,
        },
        config: Dict[str, Any],
        },
        isAxiosError: true,
        name: 'AxiosError',
        message: 'Request failed with status code 500',
        toJSON: () => ({}),
      }
      const responseErrorInterceptor = (
        axiosInstance.interceptors.response.use as jest.Mock
      ).mock.calls[0][1]
      try {
        await responseErrorInterceptor(mockError)
      } catch (err) {
        const error = err as RetryError
        expect(error.config.retryCount).toBe(1)
      }
    })
  })
})