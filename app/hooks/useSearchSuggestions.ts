import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { searchService } from '../services/search';

export interface SearchSuggestion {
  id: string;
  text: string;
  category?: string;
  type?: string;
  score?: number;
}

export function useSearchSuggestions(query: string) {
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['searchSuggestions', query],
    queryFn: async () => {
      if (!query || query.length < 2) return [];
      return searchService.search(query);
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });

  useEffect(() => {
    if (data) {
      setSuggestions(data);
    } else {
      setSuggestions([]);
    }
  }, [data]);

  return {
    suggestions,
    isLoading: isLoading && query.length >= 2,
    error,
  };
} 