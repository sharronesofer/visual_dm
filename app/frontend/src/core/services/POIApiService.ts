import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { POI } from '../types/poi';
import { Region } from '../types/regionMap';
import { Viewport } from '../types/common';

// Define ApiResponse if not found elsewhere
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
}

export class POIApiService {
  private client: AxiosInstance;
  private readonly DEFAULT_TIMEOUT = 10000; // 10 seconds

  constructor(baseURL: string = process.env.REACT_APP_API_BASE_URL || '') {
    this.client = axios.create({
      baseURL,
      timeout: this.DEFAULT_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    // Add request interceptor for auth tokens
    this.client.interceptors.request.use(config => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  async fetchPOIsByRegion(regionId: string): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>(`/regions/${regionId}/pois`);
      return response.data.data;
    });
  }

  async fetchPOIsByCoordinates(lat: number, lng: number, radius: number = 1000): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>('/regions/by-coords', {
        params: { lat, lng, radius },
      });
      return response.data.data;
    });
  }

  async fetchPOIsByViewport(viewport: Viewport): Promise<POI[]> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI[]>>('/regions/by-viewport', {
        params: viewport,
      });
      return response.data.data;
    });
  }

  async fetchPOIDetails(poiId: string): Promise<POI | null> {
    return this.withRetry(async () => {
      const response = await this.client.get<ApiResponse<POI>>(`/pois/${poiId}`);
      return response.data.data;
    });
  }

  private async withRetry<T>(operation: () => Promise<T>, retries: number = 3): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (retries > 0 && this.isRetryableError(error)) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.withRetry(operation, retries - 1);
      }
      this.handleApiError(error, 'API request failed');
      throw error;
    }
  }

  private isRetryableError(error: any): boolean {
    return (
      axios.isAxiosError(error) &&
      (!error.response || [408, 429, 500, 502, 503, 504].includes(error.response.status))
    );
  }

  private handleApiError(error: any, defaultMessage: string): void {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        console.error(
          `API Error (${error.response.status}): ${error.response.data.message || defaultMessage}`
        );
      } else if (error.request) {
        // Request made but no response received
        console.error(`Network Error: ${defaultMessage} - No response received`);
      } else {
        // Error in request configuration
        console.error(`Request Error: ${error.message}`);
      }
    } else {
      console.error(`Unexpected Error: ${error.message || defaultMessage}`);
    }
  }
}
