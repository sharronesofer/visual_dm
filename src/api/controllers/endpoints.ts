// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh-token',
  },

  // User endpoints
  USER: {
    PROFILE: '/user/profile',
    UPDATE_PROFILE: '/user/profile/update',
    CHANGE_PASSWORD: '/user/password/change',
  },

  // Map endpoints
  MAP: {
    LIST: '/maps',
    CREATE: '/maps',
    GET: (id: string) => `/maps/${id}`,
    UPDATE: (id: string) => `/maps/${id}`,
    DELETE: (id: string) => `/maps/${id}`,
    REGIONS: (mapId: string) => `/maps/${mapId}/regions`,
  },

  // Region endpoints
  REGION: {
    LIST: (mapId: string) => `/maps/${mapId}/regions`,
    CREATE: (mapId: string) => `/maps/${mapId}/regions`,
    GET: (mapId: string, regionId: string) => `/maps/${mapId}/regions/${regionId}`,
    UPDATE: (mapId: string, regionId: string) => `/maps/${mapId}/regions/${regionId}`,
    DELETE: (mapId: string, regionId: string) => `/maps/${mapId}/regions/${regionId}`,
  },
} as const;
