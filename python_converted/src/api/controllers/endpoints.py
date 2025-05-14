from typing import Any, Dict


const API_ENDPOINTS = {
  AUTH: Dict[str, Any],
  USER: Dict[str, Any],
  MAP: Dict[str, Any]`,
    UPDATE: (id: str) => `/maps/${id}`,
    DELETE: (id: str) => `/maps/${id}`,
    REGIONS: (mapId: str) => `/maps/${mapId}/regions`,
  },
  REGION: Dict[str, Any]/regions`,
    CREATE: (mapId: str) => `/maps/${mapId}/regions`,
    GET: (mapId: str, regionId: str) => `/maps/${mapId}/regions/${regionId}`,
    UPDATE: (mapId: str, regionId: str) => `/maps/${mapId}/regions/${regionId}`,
    DELETE: (mapId: str, regionId: str) => `/maps/${mapId}/regions/${regionId}`,
  },
} as const