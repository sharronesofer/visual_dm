from typing import Any



class SearchSuggestion:
    id: str
    text: str
    category?: str
    type?: str
    score?: float
function useSearchSuggestions(query: str) {
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([])
  const { data, isLoading, error } = useQuery({
    queryKey: ['searchSuggestions', query],
    queryFn: async () => {
      if (!query || query.length < 2) return []
      return searchService.search(query)
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, 
  })
  useEffect(() => {
    if (data) {
      setSuggestions(data)
    } else {
      setSuggestions([])
    }
  }, [data])
  return {
    suggestions,
    isLoading: isLoading && query.length >= 2,
    error,
  }
} 