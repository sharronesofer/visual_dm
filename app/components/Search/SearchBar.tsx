import React, { useState, useCallback, useRef } from 'react';
import { useDebounce } from 'use-debounce';
import { SearchIcon, XIcon } from '@heroicons/react/solid';
import { Combobox } from '@headlessui/react';
import { useSearchSuggestions } from '../../hooks/useSearchSuggestions';
import { classNames } from '../../../src/utils/styles';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search...',
  className = '',
  autoFocus = false,
}) => {
  const [query, setQuery] = useState('');
  const [debouncedQuery] = useDebounce(query, 300);
  const inputRef = useRef<HTMLInputElement>(null);

  const { suggestions, isLoading } = useSearchSuggestions(debouncedQuery);

  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    onSearch(value);
  }, [onSearch]);

  const clearSearch = useCallback(() => {
    setQuery('');
    onSearch('');
    inputRef.current?.focus();
  }, [onSearch]);

  return (
    <div className={classNames('relative w-full', className)}>
      <Combobox
        as="div"
        value={query}
        onChange={handleSearch}
        className="relative"
      >
        <div className="relative">
          <SearchIcon
            className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400"
            aria-hidden="true"
          />
          <Combobox.Input
            ref={inputRef}
            className={classNames(
              'w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-10',
              'text-sm text-gray-900 placeholder-gray-500',
              'focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
              'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500'
            )}
            placeholder={placeholder}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus={autoFocus}
            autoComplete="off"
          />
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-500"
            >
              <XIcon className="h-5 w-5" aria-hidden="true" />
              <span className="sr-only">Clear search</span>
            </button>
          )}
        </div>

        {(suggestions.length > 0 || isLoading) && (
          <Combobox.Options
            className={classNames(
              'absolute z-10 mt-1 max-h-60 w-full overflow-auto',
              'rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5',
              'focus:outline-none sm:text-sm'
            )}
          >
            {isLoading ? (
              <div className="relative cursor-default select-none px-4 py-2 text-gray-700">
                Loading suggestions...
              </div>
            ) : suggestions.length === 0 ? (
              <div className="relative cursor-default select-none px-4 py-2 text-gray-700">
                No suggestions found
              </div>
            ) : (
              suggestions.map((suggestion) => (
                <Combobox.Option
                  key={suggestion.id}
                  value={suggestion.text}
                  className={({ active }) =>
                    classNames(
                      'relative cursor-default select-none py-2 pl-3 pr-9',
                      active ? 'bg-primary-600 text-white' : 'text-gray-900'
                    )
                  }
                >
                  {({ active, selected }) => (
                    <>
                      <span className={classNames('block truncate', selected && 'font-semibold')}>
                        {suggestion.text}
                      </span>
                      {suggestion.category && (
                        <span
                          className={classNames(
                            'block truncate text-sm',
                            active ? 'text-primary-200' : 'text-gray-500'
                          )}
                        >
                          {suggestion.category}
                        </span>
                      )}
                    </>
                  )}
                </Combobox.Option>
              ))
            )}
          </Combobox.Options>
        )}
      </Combobox>
    </div>
  );
}; 