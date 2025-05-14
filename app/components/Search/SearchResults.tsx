import React from 'react';
import { EntityType } from '../../../src/types/search';
import { classNames } from '../../../src/utils/styles';
import { Pagination } from './Pagination';

interface SearchResultProps {
  results: Array<{
    id: string;
    type: EntityType;
    title: string;
    description?: string;
    imageUrl?: string;
    metadata?: Record<string, any>;
    highlight?: Record<string, string[]>;
  }>;
  total: number;
  page: number;
  limit: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
}

export const SearchResults: React.FC<SearchResultProps> = ({
  results,
  total,
  page,
  limit,
  onPageChange,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="animate-pulse rounded-lg bg-gray-100 p-4"
          >
            <div className="h-4 w-3/4 rounded bg-gray-200" />
            <div className="mt-2 h-3 w-1/2 rounded bg-gray-200" />
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No results found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {results.map((result) => (
          <div
            key={result.id}
            className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
          >
            <div className="flex items-start space-x-4">
              {result.imageUrl && (
                <img
                  src={result.imageUrl}
                  alt={result.title}
                  className="h-16 w-16 rounded-md object-cover"
                />
              )}
              <div className="flex-1 space-y-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-medium text-gray-900">
                    {result.title}
                  </h3>
                  <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                    {result.type}
                  </span>
                </div>
                {result.description && (
                  <p className="text-sm text-gray-500">
                    {result.description}
                  </p>
                )}
                {result.highlight && Object.keys(result.highlight).length > 0 && (
                  <div className="mt-2 text-sm">
                    {Object.entries(result.highlight).map(([field, highlights]) => (
                      <div key={field} className="mt-1">
                        <span className="font-medium text-gray-700">
                          {field}:
                        </span>
                        {highlights.map((highlight, i) => (
                          <p
                            key={i}
                            className="mt-0.5 text-gray-600"
                            dangerouslySetInnerHTML={{
                              __html: highlight,
                            }}
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                )}
                {result.metadata && Object.keys(result.metadata).length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {Object.entries(result.metadata).map(([key, value]) => (
                      <span
                        key={key}
                        className="inline-flex items-center rounded-full bg-gray-50 px-2 py-0.5 text-xs text-gray-600"
                      >
                        {key}: {value}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <Pagination
        total={total}
        page={page}
        limit={limit}
        onChange={onPageChange}
      />
    </div>
  );
}; 