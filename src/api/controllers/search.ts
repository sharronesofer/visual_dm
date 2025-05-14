import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { EntityType } from '../types/entities';
import { useAuth } from '../hooks/useAuth';

export type FilterOperator = 
  | 'eq'
  | 'ne'
  | 'gt'
  | 'gte'
  | 'lt'
  | 'lte'
  | 'in'
  | 'nin'
  | 'contains'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'
  | 'between';

export type FilterDataType = 
  | 'string'
  | 'number'
  | 'boolean'
  | 'date'
  | 'list';

export interface FilterValue {
  value: string | number | boolean | Date | Array<any>;
  operator?: FilterOperator;
}

export interface SearchFilters {
  [field: string]: FilterValue | 'and' | 'or';
}

export interface SearchParams {
  query: string;
  entityType?: EntityType;
  filters?: SearchFilters;
  page?: number;
  perPage?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  pagination?: {
    page: number;
    limit: number;
  };
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
  facets?: Record<string, Array<{ value: string; count: number }>>;
}

export interface SearchSuggestionsParams {
  field?: string;
  limit?: number;
}

export interface SearchSuggestionsResponse {
  data: string[];
}

export function useSearchApi() {
  const { getToken } = useAuth();

  const search = useCallback(async <T>(params: SearchParams): Promise<PaginatedResponse<T>> => {
    const token = await getToken();
    const { pagination = { page: 1, limit: 20 }, ...restParams } = params;
    
    const response = await axios.post('/api/v1/search', {
      ...restParams,
      entity_type: params.entityType,
      pagination
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    return {
      ...response.data,
      totalPages: response.data.total_pages // Convert snake_case to camelCase
    };
  }, [getToken]);

  const getSuggestions = useCallback(async (
    query: string,
    params: SearchSuggestionsParams = {}
  ): Promise<SearchSuggestionsResponse> => {
    const token = await getToken();
    const response = await axios.get('/api/v1/search/suggest', {
      params: { query, ...params },
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  }, [getToken]);

  return {
    search,
    getSuggestions
  };
}

export async function search<T>(params: SearchParams): Promise<PaginatedResponse<T>> {
  const response = await fetch('/api/v1/search/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: params.query,
      entity_type: params.entityType,
      filters: params.filters,
      page: params.page || 1,
      per_page: params.perPage || 10,
      sort_by: params.sortBy,
      sort_order: params.sortOrder || 'desc',
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Search failed');
  }

  return response.json();
}

export function useSearch<T>(params: SearchParams) {
  const [data, setData] = useState<PaginatedResponse<T> | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const result = await search<T>(params);
        if (mounted) {
          setData(result);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err : new Error('Search failed'));
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      mounted = false;
    };
  }, [params]);

  return { data, error, loading };
}

// Helper functions for building filter expressions
export function buildFilter(
  field: string,
  value: any,
  operator: FilterOperator = 'eq'
): FilterValue {
  return { value, operator };
}

export function combineFilters(
  filters: Record<string, FilterValue>,
  combineWith: 'and' | 'or' = 'and'
): SearchFilters {
  return {
    ...filters,
    combine_with: combineWith,
  } as SearchFilters;
}

// Example usage:
// const filters = combineFilters({
//   level: buildFilter('level', 10, 'gte'),
//   faction: buildFilter('faction', 'Alliance'),
//   tags: buildFilter('tags', ['rare', 'unique'], 'in')
// }); 