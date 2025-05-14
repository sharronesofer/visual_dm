from typing import Any, Dict, List, Union


FilterOperator = Union[, 'eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'nin', 'contains', 'not_contains', 'starts_with', 'ends_with', 'between']
FilterDataType = Union[, 'str', 'float', 'bool', 'date', 'list']
class FilterValue:
    value: Union[str, float, bool, Date, List[Any>]
    operator?: FilterOperator
class SearchFilters:
    [field: Union[str]: \'FilterValue\', 'and', 'or']
class SearchParams:
    query: str
    entityType?: EntityType
    filters?: \'SearchFilters\'
    page?: float
    perPage?: float
    sortBy?: str
    sortOrder?: Union['asc', 'desc']
    pagination?: {
    page: float
    limit: float
}
interface PaginatedResponse<T> {
  items: List[T]
  total: float
  page: float
  perPage: float
  totalPages: float
  hasNext: bool
  hasPrev: bool
  facets?: Record<string, Array<{ value: str; count: float }>>
}
class SearchSuggestionsParams:
    field?: str
    limit?: float
class SearchSuggestionsResponse:
    data: List[str]
function useSearchApi() {
  const { getToken } = useAuth()
  const search = useCallback(async <T>(params: SearchParams): Promise<PaginatedResponse<T>> => {
    const token = await getToken()
    const { pagination = { page: 1, limit: 20 }, ...restParams } = params
    const response = await axios.post('/api/v1/search', {
      ...restParams,
      entity_type: params.entityType,
      pagination
    }, {
      headers: Dict[str, Any]`
      }
    })
    return {
      ...response.data,
      totalPages: response.data.total_pages 
    }
  }, [getToken])
  const getSuggestions = useCallback(async (
    query: str,
    params: \'SearchSuggestionsParams\' = {}
  ): Promise<SearchSuggestionsResponse> => {
    const token = await getToken()
    const response = await axios.get('/api/v1/search/suggest', {
      params: Dict[str, Any],
      headers: Dict[str, Any]`
      }
    })
    return response.data
  }, [getToken])
  return {
    search,
    getSuggestions
  }
}
async function search<T>(params: SearchParams): Promise<PaginatedResponse<T>> {
  const response = await fetch('/api/v1/search/search', {
    method: 'POST',
    headers: Dict[str, Any],
    body: JSON.stringify({
      query: params.query,
      entity_type: params.entityType,
      filters: params.filters,
      page: params.page || 1,
      per_page: params.perPage || 10,
      sort_by: params.sortBy,
      sort_order: params.sortOrder || 'desc',
    }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Search failed')
  }
  return response.json()
}
function useSearch<T>(params: SearchParams) {
  const [data, setData] = useState<PaginatedResponse<T> | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(false)
  useEffect(() => {
    let mounted = true
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await search<T>(params)
        if (mounted) {
          setData(result)
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err : new Error('Search failed'))
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }
    fetchData()
    return () => {
      mounted = false
    }
  }, [params])
  return { data, error, loading }
}
function buildFilter(
  field: str,
  value: Any,
  operator: FilterOperator = 'eq'
): \'FilterValue\' {
  return { value, operator }
}
function combineFilters(
  filters: Record<string, FilterValue>,
  combineWith: 'and' | 'or' = 'and'
): \'SearchFilters\' {
  return {
    ...filters,
    combine_with: combineWith,
  } as SearchFilters
}